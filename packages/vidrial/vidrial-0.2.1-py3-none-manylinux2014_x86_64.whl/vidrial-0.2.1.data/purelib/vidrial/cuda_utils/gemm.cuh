#pragma once
#include "cute/tensor.hpp"
#include "copy.cuh"
#include "perf_cfg.cuh"

namespace vidrial {

/*
 * A flavor of gemm algorithm that doesn't read all K frgments of B
 * into register, but pipeline the read.
 */
template<int pipe_size=1, typename Cfg, typename rA_Engine, typename rA_Layout, typename rB_Engine, typename rB_Layout, typename sB_Engine, typename sB_Layout, typename rC_Engine, typename rC_Layout>
CUTE_DEVICE void gemm_impl(Cfg const& cfg, Tensor<rA_Engine, rA_Layout> const& rA_frg, Tensor<rB_Engine, rB_Layout> & rB_frg, Tensor<sB_Engine, sB_Layout> const& sB_tile, Tensor<rC_Engine, rC_Layout> &rC_frg)
{
    static_assert(is_smem<sB_Engine>::value,
                 "sB must be a smem-backed tensor");
    static_assert(!is_smem<rC_Engine>::value,
                 "rC must be a register-backed tensor");
    static_assert(!is_smem<rA_Engine>::value,
                 "rA must be a register-backed tensor");
    using T = typename sB_Engine::value_type;
    auto tid = threadIdx.x;
    auto result = slice_and_retile<T, cfg.perf.use_ldsm>(sB_tile, cfg.B.mma_FrgThr, rB_frg);
    auto copy_atom = std::get<0>(result); // might be a default copy atom or an ldsm atom
    auto sB_frg = std::get<1>(result); // sliced fragment of sB_tile
    auto rB_frg_copy = std::get<2>(result); // a retiled version of rB_frg, points to the same register, but it may have a larger V size than rB_frg if a large ldsm atom is used
    using rB_frg_copy_shape = decltype(rB_frg_copy.shape());
    using rB_frg_shape = decltype(rB_frg.shape());
    using rA_frg_shape = decltype(rA_frg.shape());
    CUTE_STATIC_ASSERT_V(size(rB_frg) == size(rB_frg_copy), "rB_frg and rB_frg_copy must have the same size");
    static_assert(size(rB_frg_copy_shape{}) % size(rB_frg_shape{}) == 0, "rB_frg_copy's per copy size must be a multiple of rB_frg's per k step size");
    static constexpr int copy_steps = size<2>(rB_frg_copy_shape{});
    static constexpr int iter_per_copy = size(rB_frg_copy_shape{}) / size(rB_frg_shape{});
    static constexpr int k_size = size<2>(rA_frg_shape{});
    static constexpr int k_size_B = size<2>(rB_frg_shape{}); // rB_frg's K size might be smaller than rA_frg's K size
    static constexpr int prefetch_iter = (copy_steps - pipe_size) * iter_per_copy;

    // prefetching
    CUTE_UNROLL
    for (int step = 0; step < static_min(pipe_size, copy_steps); step++) {
        copy(copy_atom, sB_frg(_, _, step), rB_frg_copy(_, _, step));
    }

    // main loop
    CUTE_UNROLL
    for (int i = 0, copy_step = 0; i < k_size; i++, copy_step = i / iter_per_copy) {
        if (i % iter_per_copy == 0 && i < prefetch_iter)
            copy(copy_atom, sB_frg(_, _, copy_step + pipe_size), rB_frg_copy(_, _, copy_step + pipe_size));
        cute::gemm(cfg.mma_Atom, rA_frg(_, _, i), rB_frg(_, _, i % k_size_B), rC_frg);
    }
}


/*
 * Convenience dispatch for gemm 
 */
template<typename Cfg, typename RA, typename RB, typename SB, typename RC>
CUTE_DEVICE void gemm(Cfg const& cfg, RA const& rA_frg, RB & rB_frg, SB & sB_tile, RC &rC_frg) {
    if constexpr (cfg.perf.regpipe == 0) {
        cute::gemm(cfg.mma_Atom, rA_frg, rB_frg, rC_frg);
    } else {
        vidrial::gemm_impl<cfg.perf.regpipe>(cfg, rA_frg, rB_frg, sB_tile, rC_frg);
    }
}


/*
 * Convenience dispatch for gemm, without having to create rB_frg up front. 
 * The advantage here is that we can minimize the register pressure by only
 * creating rB_frg of the size required by the regpipe size.
 */
template<typename Cfg, typename RA, typename SB, typename RC>
CUTE_DEVICE void gemm(Cfg const& cfg, RA const& rA_frg, SB & sB_tile, RC &rC_frg) {
    using T = typename Cfg::FrgTypeB;
    if constexpr (cfg.perf.regpipe == 0) {
        auto rB_frg_mma = make_tensor<T>(cfg.B.mma_Frg);
        load_frg<T, cfg.perf.use_ldsm, sizeof(T) == 2>(sB_tile, cfg.B.mma_FrgThr, rB_frg_mma);
        cute::gemm(cfg.mma_Atom, rA_frg, rB_frg_mma, rC_frg);
    } else {
        using rB_frg_copy_t = decltype(get<2>(slice_and_retile<T, cfg.perf.use_ldsm, sizeof(T) == 2>(sB_tile, cfg.B.mma_FrgThr, make_tensor<T>(cfg.B.mma_Frg))));
        constexpr auto ratio = size<2>(rB_frg_copy_t{}) / cfg.perf.regpipe; // we can shrink the rB_frg by a factor of ratio
        using rB_frg_shape_t = decltype(append(select<0,1>(cfg.B.mma_Frg), Int<get<2>(cfg.B.mma_Frg) / ratio>{}));
        auto rB_frg = make_tensor<T>(make_layout(rB_frg_shape_t{}));
        vidrial::gemm_impl<cfg.perf.regpipe>(cfg, rA_frg, rB_frg, sB_tile, rC_frg);
    }
}

namespace detail {
    template<typename T, typename FrgThr, typename STile, typename FrgLayout, typename AuxConfig>
    CUTE_DEVICE auto create_regpipe(FrgThr frgThr, STile sTile, FrgLayout frgLayout, AuxConfig) {
        constexpr auto frg = make_tensor<T>(frgLayout);
        using copy_view_t = std::remove_reference_t<decltype(get<2>(slice_and_retile<T, AuxConfig::use_ldsm, false>(sTile, frgThr, frg)))>;
        constexpr auto regpipe = static_min(AuxConfig::regpipe, size<2>(copy_view_t{}));
        constexpr auto vfrag_rest = (size(take<0,2>(copy_view_t{})) * regpipe) / size(take<0,2>(frgLayout));
        constexpr auto pipe_rest = size<2>(frgLayout) / vfrag_rest;
        using FrgShape_t = decltype(append(select<0,1>(frgLayout.shape()), Shape<Int<vfrag_rest>, Int<pipe_rest>>{}));
        auto full_strides = make_layout(FrgShape_t{}).stride();
        auto rest_k_strides = make_stride(get<2,0>(full_strides), Int<0>{});
        auto frg_strides = make_stride(get<0>(full_strides),
                                        get<1>(full_strides),
                                        rest_k_strides);
        auto frg_regpipe = make_tensor<T>(make_layout(FrgShape_t{}, frg_strides));
        return frg_regpipe;
    }

} // namespace detail

/*
    * Perform a matrix multiplication of A tile, B tile, and C fragments.
    * @param cfg: The config object that contains the mma atom.
    * @param a_tile: The A tile (of type cute::Tensor, in smem).
    * @param b_tile: The B tile (of type cute::Tensor, in smem).
    * @param c_frg: The C fragments (of type cute::Tensor, in register).
    */
template<typename Config, typename ATile, typename BTile, typename CFrg>
CUTE_DEVICE void mma(Config& cfg, ATile& a_tile, BTile& b_tile, CFrg& c_frg) {
    CUTE_STATIC_ASSERT(is_smem<ATile>::value, "a_tile must be a smem-backed tensor");
    CUTE_STATIC_ASSERT(is_smem<BTile>::value, "b_tile must be a smem-backed tensor");
    CUTE_STATIC_ASSERT(is_rmem<CFrg>::value, "c_frg must be a register-backed tensor");
    using TA = typename Config::FrgTypeA;
    using TB = typename Config::FrgTypeB;

    auto a_frg = make_tensor<TA>(cfg.A.mma_Frg); // [v, m, n]
    auto b_frg = make_tensor<TB>(cfg.B.mma_Frg);
    load_frg<TA, cfg.perf.use_ldsm, false>(a_tile, cfg.A.mma_FrgThr, a_frg);
    load_frg<TB, cfg.perf.use_ldsm, false>(b_tile, cfg.B.mma_FrgThr, b_frg);
    cute::gemm(cfg.mma_Atom, a_frg, b_frg, c_frg);
};

/*
    * Perform a matrix multiplication of A fragments, B tile, and C fragments.
    * @param cfg: The config object that contains the mma atom.
    * @param a_frg: The A fragments (of type cute::Tensor, in register).
    * @param b_tile: The B tile (of type cute::Tensor, in smem).
    * @param c_frg: The C fragments (of type cute::Tensor, in register).
    */
template<typename Config, typename AFrg, typename BTile, typename CFrg>
CUTE_DEVICE void pipeB_mma(Config& cfg, AFrg& a_frg, BTile& b_tile, CFrg& c_frg) {
    CUTE_STATIC_ASSERT(is_rmem<AFrg>::value, "a_frg must be a register-backed tensor");
    CUTE_STATIC_ASSERT(is_smem<BTile>::value, "b_tile must be a smem-backed tensor");
    CUTE_STATIC_ASSERT(is_rmem<CFrg>::value, "c_frg must be a register-backed tensor");
    using TB = typename Config::FrgTypeB;

    auto b_tile_permuted = coalesce_each(logical_divide(b_tile, cfg.B.perm));
    auto b_frg = vidrial::detail::create_regpipe<TB>(cfg.B.mma_FrgThr, b_tile_permuted, cfg.B.mma_Frg, cfg.perf);
    auto result = slice_and_retile<TB, cfg.perf.use_ldsm, cfg.perf.use_ldsm>(b_tile_permuted, cfg.B.mma_FrgThr, b_frg);
    auto copy_atom = std::get<0>(result); // might be a default copy atom or an ldsm atom
    auto sb_frg = std::get<1>(result); // sliced fragment of b_tile
    auto b_frg_copy = std::get<2>(result); // a retiled version of b_frg, points to the same register, but it may have a larger V size than b_frg if a large ldsm atom is used
    using b_frg_copy_shape = decltype(b_frg_copy.shape());
    using b_frg_shape = decltype(b_frg.shape());
    using a_frg_shape = decltype(a_frg.shape());
    CUTE_STATIC_ASSERT_V(size(b_frg) == size(b_frg_copy), "b_frg and b_frg_copy must have the same size");
    static_assert(size(b_frg_copy_shape{}) % size(b_frg_shape{}) == 0, "b_frg_copy's per copy size must be a multiple of b_frg's per k step size");
    static constexpr int pipe_size = size<2>(b_frg_copy_shape{}) / (size(b_frg_copy_shape{}) / cosize(decltype(b_frg.layout()){}));
    static constexpr int total_copies = size<2>(b_frg_copy_shape{});
    static constexpr int iter_per_copy = size(select<0,1>(b_frg_copy_shape{})) / size(select<0,1>(b_frg_shape{}));
    static constexpr int k_size = size<2>(a_frg_shape{});
    static constexpr int k_size_B = size<2>(b_frg_shape{}); 
    static_assert(k_size_B == k_size, "b_frg and a_frg must have the same K size");

    // prefetching
    CUTE_UNROLL
    for (int step = 0; step < pipe_size - 1; step++) {
        copy(copy_atom, sb_frg(_, _, step), b_frg_copy(_, _, step));
    }

    // main loop
    CUTE_UNROLL
    for (int i = 0, copy_step = pipe_size - 1; i < k_size; i++, copy_step = (i / iter_per_copy) + pipe_size - 1) {
        if (i % iter_per_copy == 0 && copy_step < total_copies)
            copy(copy_atom, sb_frg(_, _, copy_step), b_frg_copy(_, _, copy_step));
        cute::gemm(cfg.mma_Atom, a_frg(_, _, i), b_frg(_, _, i), c_frg);
    }
};

/*
    * Perform a matrix multiplication of A tile, B tile, and C tile.
    * @param cfg: The config object that contains the mma atom.
    * @param a_tile: The A tile (of type cute::Tensor, in smem).
    * @param b_tile: The B tile (of type cute::Tensor, in smem).
    * @param c_frg: The C fragments (of type cute::Tensor, in register).
    */
template<bool scale_A, typename Config, typename ATile, typename BTile, typename CFrg>
CUTE_DEVICE void pipeAB_mma(Config& cfg, ATile& a_tile, BTile& b_tile, CFrg& c_frg, const float sA) {
    CUTE_STATIC_ASSERT(is_smem<ATile>::value, "a_tile must be a smem-backed tensor");
    CUTE_STATIC_ASSERT(is_smem<BTile>::value, "b_tile must be a smem-backed tensor");
    CUTE_STATIC_ASSERT(is_rmem<CFrg>::value, "c_frg must be a register-backed tensor");
    using TA = typename Config::FrgTypeA;
    using TB = typename Config::FrgTypeB;

    auto a_frg = vidrial::detail::create_regpipe<TA>(cfg.A.mma_FrgThr, a_tile, cfg.A.mma_Frg, cfg.perf);
    auto b_frg = vidrial::detail::create_regpipe<TB>(cfg.B.mma_FrgThr, b_tile, cfg.B.mma_Frg, cfg.perf);

    auto a_retiled_result = slice_and_retile<TA, cfg.perf.use_ldsm, cfg.perf.use_ldsm>(a_tile, cfg.A.mma_FrgThr, a_frg);
    auto a_copy_atom = std::get<0>(a_retiled_result); // might be a default copy atom or an ldsm atom
    auto sa_frg = std::get<1>(a_retiled_result); // sliced fragment of a_tile
    auto a_frg_copy = std::get<2>(a_retiled_result); // a retiled version of a_frg, points to the same register, but it may have a larger V size than a_frg if a large ldsm atom is used

    auto b_retiled_result = slice_and_retile<TB, cfg.perf.use_ldsm, cfg.perf.use_ldsm>(b_tile, cfg.B.mma_FrgThr, b_frg);
    auto b_copy_atom = std::get<0>(b_retiled_result);
    auto sb_frg = std::get<1>(b_retiled_result);
    auto b_frg_copy = std::get<2>(b_retiled_result);

    using b_frg_copy_shape = decltype(b_frg_copy.shape());
    using b_frg_shape = decltype(b_frg.shape());
    using a_frg_shape = decltype(a_frg.shape());
    CUTE_STATIC_ASSERT_V(size(b_frg) == size(b_frg_copy), "b_frg and b_frg_copy must have the same size");
    static_assert(size(b_frg_copy_shape{}) % size(b_frg_shape{}) == 0, "b_frg_copy's per copy size must be a multiple of b_frg's per k step size");
    static constexpr int pipe_size = size<2>(b_frg_copy_shape{}) / (size(b_frg_copy_shape{}) / cosize(decltype(b_frg.layout()){}));
    static constexpr int total_copies = size<2>(b_frg_copy_shape{});
    static constexpr int iter_per_copy = size(select<0,1>(b_frg_copy_shape{})) / size(select<0,1>(b_frg_shape{}));
    static constexpr int k_size = size<2>(decltype(cfg.A.mma_Frg){});
    static constexpr int k_size_A = size<2>(a_frg_shape{});
    static constexpr int k_size_B = size<2>(b_frg_shape{});
    static_assert(k_size_A == k_size_B, "a_frg and b_frg must have the same K size");
    static_assert(k_size_A == k_size, "a_frg and b_frg must have the same K size, equal to the mmaFrg's K size");

    // prefetching
    CUTE_UNROLL
    for (int step = 0; step < pipe_size - 1; step++) {
        copy(b_copy_atom, sb_frg(_, _, step), b_frg_copy(_, _, step));
        copy(a_copy_atom, sa_frg(_, _, step), a_frg_copy(_, _, step));
    }

    // main loop
    CUTE_UNROLL
    for (int i = 0, copy_step = pipe_size - 1; i < k_size; i++, copy_step = (i / iter_per_copy) + pipe_size - 1) {
        if (i % iter_per_copy == 0 && copy_step < total_copies) {
            copy(b_copy_atom, sb_frg(_, _, copy_step), b_frg_copy(_, _, copy_step));
            copy(a_copy_atom, sa_frg(_, _, copy_step), a_frg_copy(_, _, copy_step));
        }
        if constexpr (scale_A) {
            tensor_scalar_prod(a_frg(_, _, i % k_size_A), sA);
        }
        cute::gemm(cfg.mma_Atom, a_frg(_, _, i % k_size_A), b_frg(_, _, i % k_size_B), c_frg);
    }
};

template<typename Config, typename ATile, typename BTile, typename CFrg>
CUTE_DEVICE void pipeAB_mma(Config& cfg, ATile& a_tile, BTile& b_tile, CFrg& c_frg) {
    pipeAB_mma<false, Config, ATile, BTile, CFrg>(cfg, a_tile, b_tile, c_frg, 1.0);
};

} // namespace vidrial
