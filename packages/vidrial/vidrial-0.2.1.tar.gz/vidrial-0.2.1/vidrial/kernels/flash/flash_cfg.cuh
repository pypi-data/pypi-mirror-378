#pragma once
#include <cute/tensor.hpp>
#include "../../cuda_utils/mask_cfg.cuh"
#include "../../kernels/mma/mma_cfg.cuh"
#include "../../cuda_utils/utilities.cuh"
#include "../../cuda_utils/frg_copy.cuh"
#include "../../cuda_utils/perf_cfg.cuh"
#include "../../cuda_utils/mask_cfg.cuh"
#include "../../cuda_utils/softmax.cuh"
#include "../../kernels/mma/mma_cfg.cuh"
#include "../../kernels/reduce/reduce_utils.cuh"

namespace vidrial {
using namespace cute;

#define CEIL_DIV(x, y) (((x) + (y) - 1) / (y))

/**
 * @brief FlashKernelCfg is a configuration for a flash attention kernel.
 * @tparam MmaCfg1 The configuration for the first mma
 * @tparam MmaCfg2 The configuration for the second mma
 * @tparam MaskCfg The configuration for the mask
 * @tparam SoftmaxCfg The configuration for the softmax
 */
template <typename LT_, typename MmaCfg1, typename MmaCfg2, typename MaskCfg, typename SoftmaxCfg, typename GLSlab>
struct FlashKernelCfg {
    using T = typename MmaCfg1::T;
    using LT = LT_;
    using Mma1_C_frg__2__Mma2_A_frg = decltype(left_inverse(get<0>(MmaCfg1{}.C.mma_FrgThr)).compose(get<0>(MmaCfg2{}.A.mma_FrgThr)));
    using PerfCfg1 = typename MmaCfg1::PerfCfg;
    using PerfCfg2 = typename MmaCfg2::PerfCfg;

    static constexpr PerfCfg1 perf1{};
    static constexpr PerfCfg2 perf2{};
    static constexpr bool q_in_reg = PerfCfg1::q_in_reg;
    static constexpr int threads = size(MmaCfg1::thread_num);
    MmaCfg1 mma1;
    MmaCfg2 mma2;
    MaskCfg mask;
    Mma1_C_frg__2__Mma2_A_frg mma1_C_frg__2__mma2_A_frg;
    SoftmaxCfg softmax;
    GLSlab gLSlab;

    static int smem_size() {
        using A1T = typename MmaCfg1::T;
        using B1T = typename MmaCfg1::T;
        using B2T = typename MmaCfg2::T;
        using C2T = typename MmaCfg2::T;
        using A1_STile = typename MmaCfg1::ACfg::STile;
        using B1_STile = typename MmaCfg1::BCfg::STile;
        using B2_STile = typename MmaCfg2::BCfg::STile;
        using C2_STile = typename MmaCfg2::CCfg::STile;

        int Q_size = Allocator<16>::total<A1T>(size(A1_STile{}) * MmaCfg1::K_tile_num);

        int QKV_size = Allocator<16>::total<A1T, B1T, B2T>(
            size(A1_STile{}) * (q_in_reg ? 0 : MmaCfg1::K_tile_num),
            size(B1_STile{}) * perf1.smempipe,
            size(B2_STile{}) * perf2.smempipe
        );
        int O_size = Allocator<16>::total<C2T>(size(C2_STile{}));
        int l_size = Allocator<16>::total<LT>(size<0>(C2_STile{}));
        if constexpr (q_in_reg) {
            return static_max(Q_size, static_max(QKV_size, O_size + l_size));
        } else {
            return static_max(QKV_size, O_size + l_size);
        }
    }
};

/**
 * @brief Guess the missing slab from the given slabs using canonical stride. All slabs conform to the following shape convention:
 *        A: (M, K, P)
 *        B: (N, K, P)
 *        C: (M, N, P)
 *        - P is the batch mode
 * @tparam ASlab The slab of the first mma, or void indicating A is missing
 * @tparam BSlab The slab of the second mma, or void indicating B is missing
 * @tparam CSlab The slab of the third mma, or void indicating C is missing
 * @return The missing slab
 */
template <typename ASlab, typename BSlab, typename CSlab, typename Stride_t=LayoutLeft>
constexpr auto make_missing_slab(Stride_t) {
    if constexpr (is_void_v<ASlab>) { // A is missing
        constexpr int M = size<0>(CSlab{});
        constexpr int K = size<1>(BSlab{});
        constexpr int P = size<2>(CSlab{});
        return static_tree_cast<int64_t>(make_layout(static_tree_cast<int64_t>(Shape<Int<M>, Int<K>, Int<P>>{}), Stride_t{}));
    } else if constexpr (is_void_v<BSlab>) { // B is missing
        constexpr int N = size<1>(CSlab{});
        constexpr int K = size<1>(ASlab{});
        constexpr int P = size<2>(CSlab{});
        return static_tree_cast<int64_t>(make_layout(static_tree_cast<int64_t>(Shape<Int<N>, Int<K>, Int<P>>{}), Stride_t{}));
    } else { // C is missing
        constexpr int M = size<0>(ASlab{});
        constexpr int N = size<0>(BSlab{});
        constexpr int P = size<2>(ASlab{});
        return static_tree_cast<int64_t>(make_layout(static_tree_cast<int64_t>(Shape<Int<M>, Int<N>, Int<P>>{}), Stride_t{}));
    }
}

/**
 * @brief Computes the mask boundary for N dimension
 * @return The start of the causal region in N dimension and the size of the causal region, in unit of N_tile
 */
template <typename FlashKernelCfg, typename MmaMNKCoords, int r=1, int w=1>
CUTE_HOST_DEVICE auto causal_region(FlashKernelCfg &cfg, MmaMNKCoords &tile_coords) {
    constexpr auto offset = cfg.mma1.N / w - cfg.mma1.M / r;
    static_assert(offset >= 0, "Offset must be non-negative for causal mask");
    constexpr int N_tile = cfg.mma1.N_tile;
    constexpr int M_tile = cfg.mma1.M_tile;
    auto M_idx = tile_coords.M_coord() * M_tile;
    auto start = (M_idx / r + offset) / (N_tile / w);
    auto end = CEIL_DIV((M_idx + M_tile) / r + offset, (N_tile / w));
    return std::make_pair(start, end);
}

/**
 * @brief Compute the atom placement for the second mma
 */
template <typename MmaCfg1, typename _MmaAtom2>
constexpr auto get_atom_placement_MNK() {
    constexpr auto cfg = MmaCfg1{};
    using Atom1Shape_t = typename decltype(cfg.mma_Atom)::Shape_MNK;
    using Atom2Shape_t = typename _MmaAtom2::Shape_MNK;
    using Placement1_t = typename MmaCfg1::MNKAtomPlacement;
    constexpr int total_atoms = cfg.thread_num / size(typename _MmaAtom2::ThrID{});
    constexpr int M_placement_1 = size<0>(Placement1_t{});
    constexpr int N_placement_1 = size<1>(Placement1_t{});
    constexpr int K_placement_1 = size<2>(Placement1_t{});
    constexpr int M_placement_2 = M_placement_1 * size<0>(Atom1Shape_t{}) / size<0>(Atom2Shape_t{});
    constexpr int K_placement_2 = N_placement_1 * size<1>(Atom1Shape_t{}) / size<1>(Atom2Shape_t{});
    constexpr int N_placement_2 = total_atoms / (M_placement_2 * K_placement_2);
    static_assert(N_placement_2 >= 1, "N_placement_2 must be at least 1");
    static_assert(K_placement_2 >= 1, "K_placement_2 must be at least 1");
    return make_tile(Int<M_placement_2>{}, Int<N_placement_2>{}, Int<K_placement_2>{});
}

/**
 * @brief Compute the permutation required to make the second mma's B tile's K dimension match the first mma's C atom layout. Note that this function doesn't check inter-atom frgthr layout compatibility.
 */
template <typename MmaCfg1, typename MmaAtom2, typename TileMNK2_t, typename Placement2_t>
constexpr auto get_permutation_MNK() {
    constexpr auto cfg = MmaCfg1{};
    using Atom1Shape_t = typename decltype(cfg.mma_Atom)::Shape_MNK;
    using Atom2Shape_t = typename MmaAtom2::Shape_MNK;
    using Placement1_t = typename MmaCfg1::MNKAtomPlacement;
    constexpr auto AtomShape1_C = select<0, 1>(Atom1Shape_t{});
    constexpr auto AtomShape2_A = select<0, 2>(Atom2Shape_t{});
    // --- first mma's C ---
    constexpr auto OpShape1_tiled_C = make_tile(AtomShape1_C, make_tile(get<0>(Placement1_t{}), get<1>(Placement1_t{}))); // [[M_atom, N_atom], [M_num_atom, N_num_atom]]
    constexpr auto OpShape2_tiled_A = make_tile(AtomShape2_A, make_tile(get<0>(Placement2_t{}), get<2>(Placement2_t{}))); // [[M_atom, K_atom], [M_num_atom, K_num_atom]]
    constexpr auto OpShape1_C = zip(OpShape1_tiled_C); // [[M_atom, M_num_atom], [N_atom, N_num_atom]]
    constexpr auto OpShape1_C_shape = transform(OpShape1_C, [](auto x) {
        return size(x);
    });
    constexpr auto Rest1_C = get<1>(zipped_divide(make_layout(cfg.C.tileShape), OpShape1_C_shape).shape()); // [M_rest, N_rest]
    constexpr auto Tile1_C = make_tile(
        make_tile(get<0, 0>(OpShape1_C), get<0, 1>(OpShape1_C), get<0>(Rest1_C)),
        make_tile(get<1, 0>(OpShape1_C), get<1, 1>(OpShape1_C), get<1>(Rest1_C))
    );

    // --- second mma's A ---
    constexpr auto OpShape2_A = zip(OpShape2_tiled_A); // [[M_atom, M_num_atom], [K_atom, K_num_atom]]
    constexpr auto OpShape2_A_shape = transform(OpShape2_A, [](auto x) {
        return size(x);
    });
    constexpr auto TileShape2_A = select<0, 2>(TileMNK2_t{});
    constexpr auto Rest2_A = get<1>(zipped_divide(make_layout(TileShape2_A), OpShape2_A_shape).shape()); // [M_rest, K_rest]

    constexpr auto Tile2_A = make_tile(
        make_tile(get<0, 0>(OpShape2_A), get<0, 1>(OpShape2_A), get<0>(Rest2_A)),
        make_tile(get<1, 0>(OpShape2_A), get<1, 1>(OpShape2_A), get<1>(Rest2_A))
    );

    if constexpr (is_same_v<decltype(Rest1_C), decltype(Rest2_A)>) {
        return make_tile(_, _, _);
    } else {
        CUTE_STATIC_ASSERT_V(size<0>(Tile1_C) == size<0>(Tile2_A), "M size mismatch");
        CUTE_STATIC_ASSERT_V(size<1>(Tile1_C) == size<1>(Tile2_A), "N and K size mismatch");
        constexpr auto m1 = select<0, 2, 1>(make_layout(get<0>(Tile1_C))); // [M_atom, M_rest, M_num_atom]
        constexpr auto n1 = select<0, 2, 1>(make_layout(get<1>(Tile1_C))); // [N_atom, N_rest, N_num_atom]
        constexpr auto m2 = select<0, 2, 1>(make_layout(get<0>(Tile2_A))); // [M_atom, M_rest, M_num_atom]
        constexpr auto k2 = select<0, 2, 1>(make_layout(get<1>(Tile2_A))); // [K_atom, K_rest, K_num_atom]
        using m_perm_t = decltype(left_inverse(m2).compose(m1));
        using k_perm_t = decltype(left_inverse(k2).compose(n1));
        return make_tile(m_perm_t{}, _, k_perm_t{});
    }

}

template <typename T, typename LT, typename MmaAtom1, typename MNKTileShape1, typename MNKAtomPlacement1, typename MmaAtom2, typename NTile2, typename GQSlab, typename GKSlab, typename GVSlab, typename GOSlab, typename GLSlab, typename Perf1Cfg = DefaultPerfCfg, typename Perf2Cfg = DefaultPerfCfg>
auto make_FlashKernelCfg() {
    constexpr int M_TILE_1 = size<0>(MNKTileShape1{});
    constexpr int N_TILE_1 = size<1>(MNKTileShape1{});
    using MNKTileShape2 = Shape<Int<M_TILE_1>, NTile2, Int<N_TILE_1>>;

    using FakeSSlab = decltype(make_missing_slab<GQSlab, GKSlab, void>(LayoutLeft{}));
    constexpr auto mma1 = MmaKernelCfg<T, MmaAtom1, MNKTileShape1, MNKAtomPlacement1, GQSlab, GKSlab, FakeSSlab, Perf1Cfg>();

    // ---- Compute the atom placement for the second mma ----
    constexpr auto atom_placement_2 = get_atom_placement_MNK<decltype(mma1), MmaAtom2>();

    // ---- Compute the permutation for the second mma ----
    using permutation_2_t = decltype(get_permutation_MNK<decltype(mma1), MmaAtom2, MNKTileShape2, decltype(atom_placement_2)>());
    auto permutation_2 = get_permutation_MNK<decltype(mma1), MmaAtom2, MNKTileShape2, decltype(atom_placement_2)>();

    // ---- Construct the second mma cfg ----
    using FakeASlab = decltype(make_missing_slab<void, GVSlab, GOSlab>(LayoutLeft{}));
    constexpr auto mma2 = MmaKernelCfg<T, MmaAtom2, MNKTileShape2, decltype(atom_placement_2), FakeASlab, GVSlab, GOSlab, Perf2Cfg, permutation_2_t>{};
    static_assert(size<0>(mma1.MNK_tile_shape) == size<0>(mma2.MNK_tile_shape), "M tile mismatch");
    static_assert(size<1>(mma1.MNK_tile_shape) == size<2>(mma2.MNK_tile_shape), "N/K tile mismatch");
    static_assert(mma1.M == mma2.M, "M mismatch");
    static_assert(mma1.N == mma2.K, "N/K mismatch");
    static_assert(mma1.perf.smempipe / mma1.K_tile_num == mma2.perf.smempipe, "smempipe mismatch");

    // ---- Construct the mask cfg ----
    constexpr auto mask_cfg = make_mask_cfg<T, MNKTileShape1, decltype(mma1.C.mma_FrgThr), CausalMask, OpNegInf>();

    // ---- Construct the softmax cfg ----
    using softmax_cfg_t = decltype(make_SoftmaxCfg<LT, decltype(mma1.C.sTile.shape()), decltype(mma1.C.mma_FrgThr), decltype(mma2.C.sTile.shape()), decltype(mma2.C.mma_FrgThr), true>());  

    return FlashKernelCfg<LT, decltype(mma1), decltype(mma2), decltype(mask_cfg), softmax_cfg_t, GLSlab>{};
}

} // namespace vidrial