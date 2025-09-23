#pragma once
#include "tprod_bwd.cuh"
#include "../sympow/sympow_cfg.cuh"

namespace vidrial {

template <typename _SympowCfg, typename SmemAccI>
struct SympowBwdCfg {
    using SympowCfg = _SympowCfg;
    using T = typename SympowCfg::T;
    SympowCfg fwd{};
    static constexpr SmemAccI smem_acc_I{};
    static constexpr auto d = SympowCfg::d;
    static constexpr auto d_tile = SympowCfg::d_tile;
    using Coords = SympowCoords<SympowCfg>;
    template<auto... i>
    static constexpr auto get_TprodBwd(index_sequence<i...> seq) {
        return make_tuple(TprodBwdCfg<float, i, typename SympowCfg::ZTileShape, typename SympowCfg::ZFrgThr>{}...);
    }
    using TprodBwd = decltype(get_TprodBwd(make_index_sequence<SympowCfg::p>{}));
    TprodBwd tprod_bwd;
};

template <typename T, int p, typename SmemAccI> CUTE_HOST_DEVICE
auto make_sympow_bwd_cfg(auto Z_frg_shape, auto X_tile_shape, auto gZ_slab, auto gX_slab, auto sZ_tile) {
    auto sympow_cfg = make_sympow_kernel_cfg<T, p>(Z_frg_shape, X_tile_shape, gZ_slab, gX_slab, sZ_tile);
    auto cfg = SympowBwdCfg<decltype(sympow_cfg), SmemAccI>{};
    return cfg;
}
template <typename T, int p, bool smem_acc=false> CUTE_HOST_DEVICE
auto make_sympow_bwd_cfg(auto Z_frg_shape, auto X_tile_shape, auto gZ_slab, auto gX_slab, auto sZ_tile) {
    auto smem_acc_I = make_variadic_tuple(make_int_sequence<p>{},
        [](auto) {
            if constexpr (smem_acc)
                return _1{};
            else
                return _0{};
        });
    return make_sympow_bwd_cfg<T, p, decltype(smem_acc_I)>(Z_frg_shape, X_tile_shape, gZ_slab, gX_slab, sZ_tile);
}


// --------------- Utilities for the sympow config ---------------

template<auto i, typename Cfg> CUTE_DEVICE
static constexpr auto rXigrad_batch_frg_shape(Cfg& cfg) {
    auto shp = get<i>(cfg.fwd.Xi).Frg.shape();
    if constexpr (get<i>(cfg.smem_acc_I) == _0{}) { // if i is not accumulated in smem we need a fragment
        return make_shape(shp, Int<cfg.d/cfg.d_tile>{});
    } else {
        return shp;
    }
}
template<auto i, typename Cfg> CUTE_DEVICE
static constexpr auto make_rXigrad_batch_frg(Cfg& cfg) {
    using T = typename Cfg::T;
    return make_tensor<T>(rXigrad_batch_frg_shape<i>(cfg));
}

template<auto i, typename Cfg> CUTE_DEVICE
void sympow_tile_bwd_smem_acc(Cfg& cfg, auto& coords, auto& sXgrad_batch, auto& rXIgrad_frg, auto& rXI_tile_frg, auto& rYgrad_tile_frg) {
    using T = typename Cfg::T;
    auto sXigrad_tile = coords.slice_X_tile_from_batch<i>(sXgrad_batch);
    auto sXigrad_frg = slice_rest(sXigrad_tile, get<i>(cfg.fwd.Xi).tprod_FrgThr, threadIdx.x);
    auto& rXigrad_frg = get<i>(rXIgrad_frg);
    bool owns_frg = get<i>(cfg.tprod_bwd).owns_frg();
    tprod_bwd_warp(get<i>(cfg.tprod_bwd), rXI_tile_frg, rXigrad_frg, rYgrad_tile_frg);
    constexpr bool sync_smem = !get<i>(Cfg{}.tprod_bwd).smart_reduce.skip_smem_reduce; // Only necessary to sync if warp_reduce_size > 1
    if (coords.D_tile_iter.template store_dim<i>()) {
        if (owns_frg)
            add_tensor(rXigrad_frg, sXigrad_frg);
        if constexpr (sync_smem)
            __syncthreads();
        tprod_bwd_CTA(get<i>(cfg.tprod_bwd), rXigrad_frg, sXigrad_tile);
        if constexpr (sync_smem)
            __syncthreads();
        if (owns_frg)
            copy(rXigrad_frg, sXigrad_frg);
        clear(rXigrad_frg);
        if constexpr (sync_smem)
            __syncthreads();
    }
}

template<auto i, typename Cfg> CUTE_DEVICE
void sympow_tile_bwd_iter(Cfg& cfg, auto& coords, auto& sXgrad_batch, auto& rXIgrad_frg, auto& rXI_tile_frg, auto& rYgrad_tile_frg) {
    using T = typename Cfg::T;
    if constexpr (get<i>(cfg.smem_acc_I) == _1{}) { // fully accumulate the gradient to sXgrad_batch
        sympow_tile_bwd_smem_acc<i>(cfg, coords, sXgrad_batch, rXIgrad_frg, rXI_tile_frg, rYgrad_tile_frg);
    } else {
        auto rXigrad_frg = slice_rest(get<i>(rXIgrad_frg), get<i>(coords.D_tile_iter.seq));
        tprod_bwd_warp(get<i>(cfg.tprod_bwd), rXI_tile_frg, rXigrad_frg, rYgrad_tile_frg);
    }
}
template<auto i, typename Cfg> CUTE_DEVICE
void sympow_tile_bwd_epilogue(Cfg& cfg, auto& coords, auto& sXgrad_batch, auto& rXIgrad_batch_frg) {
    using T = typename Cfg::T;
    if constexpr (get<i>(cfg.smem_acc_I) == _0{}) { // only need to store the dimensions that were not accumulated during the iterations
        bool owns_frg = get<i>(cfg.tprod_bwd).owns_frg();
        CUTE_UNROLL
        for (int d_tile_idx = 0; d_tile_idx < cfg.d / cfg.d_tile; d_tile_idx++) {
            auto sXigrad_tile = coords.slice_X_tile_from_batch(sXgrad_batch, d_tile_idx);
            auto sXigrad_frg = slice_rest(sXigrad_tile, get<i>(cfg.fwd.Xi).tprod_FrgThr, threadIdx.x); // potentially contains data
            auto rXigrad_frg = slice_rest(get<i>(rXIgrad_batch_frg), d_tile_idx);
            if (owns_frg)
                add_tensor(rXigrad_frg, sXigrad_frg);
            tprod_bwd_CTA(get<i>(cfg.tprod_bwd), rXigrad_frg, sXigrad_tile);
            if (owns_frg)
                copy(rXigrad_frg, sXigrad_frg);
            __syncthreads();
        }
    }
}

} // end namespace vidrial
 