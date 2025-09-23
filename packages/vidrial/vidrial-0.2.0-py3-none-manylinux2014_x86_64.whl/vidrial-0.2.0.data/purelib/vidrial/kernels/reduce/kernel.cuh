#pragma once
#include "../copy/copy_cfg.cuh"
#include "reduce_utils.cuh"
#include "../../cuda_utils/allocator.cuh"

namespace vidrial {

template<typename _T, int _thread_num,
         typename XTileShape,
         typename GXSlab, typename GxSlab>
struct ReduceKernelCfg {
    using T = _T;
    static constexpr int thread_num = _thread_num;
    using xTileShape = decltype(wrap(get<1>(XTileShape{})));
    using XTilingCfg = decltype(make_tiling_cfg<T, thread_num>(GXSlab{}.shape(), XTileShape{}, GXSlab{}));
    using xTilingCfg = decltype(make_tiling_cfg<T, thread_num>(GxSlab{}.shape(), xTileShape{}, GxSlab{}));
    // TODO: pick a smarter XFrgThr layout that allows as much thread level reduction as possible
    using XFrgThr = typename XTilingCfg::TileCopy::FrgThr_t;
    using SmartReduceCfg = decltype(make_SmartReduceCfg(XTileShape{}, XFrgThr{}));
    XTilingCfg X_tiling;
    xTilingCfg x_tiling;
    SmartReduceCfg smart_reduce;
    static constexpr int block_num = size<1,1>(XTilingCfg{}.TileBlock);
    static constexpr int reduce_tile_num = size<1,0>(XTilingCfg{}.TileBlock);
};

template<typename Cfg, typename XT, typename xT, typename Fn>
__global__ void reduce_kernel(Cfg cfg, XT* gX_ptr, xT* gx_ptr, Fn fn) {
    using T = typename Cfg::T;
    static_assert(is_same_v<T, XT> && is_same_v<T, xT>, "Invalid types");
    auto gX_slab = make_tensor(gX_ptr, cfg.X_tiling.gSlab);
    __shared__ alignas(16) T X_tile_smem[cosize(cfg.X_tiling.tile_copy.sTile)];
    __shared__ alignas(16) T x_tile_smem[cosize(cfg.x_tiling.tile_copy.sTile)];
    auto sX_tile = make_tensor(make_smem_ptr(X_tile_smem), cfg.X_tiling.sTile);
    auto sx_tile = make_tensor(make_smem_ptr(x_tile_smem), cfg.x_tiling.sTile);
    auto rx_acc_frg = make_tensor<T>(get<0>(cfg.smart_reduce.x.frg_thr.shape()));
    clear(rx_acc_frg); // TODO: make initial value configurable
    // Accumulate across all the tiles
    for (int reduce_tile_idx = 0; reduce_tile_idx < cfg.reduce_tile_num; reduce_tile_idx++) {
        auto tile_coords = make_coord(reduce_tile_idx, blockIdx.x);
        auto gX_tile = slice_rest(gX_slab, cfg.X_tiling.TileBlock, tile_coords);
        CTA_copy_tile(cfg.X_tiling.tile_copy, gX_tile, sX_tile);
        cp_async_fence(); cp_async_wait<0>(); __syncthreads();
        auto rX_frg = make_tensor<T>(get<0>(cfg.smart_reduce.X.frg_thr.shape()));
        copy(slice_rest(sX_tile, cfg.smart_reduce.X.frg_thr, threadIdx.x), rX_frg);
        smart_reduce_thread(cfg.smart_reduce, rX_frg, rx_acc_frg, fn);
    };
    smart_reduce_cta(cfg.smart_reduce, rx_acc_frg, sx_tile, fn);
    // Store accumulation to smem
    if (cfg.smart_reduce.owns_frg())
        copy(rx_acc_frg, slice_rest(sx_tile, cfg.smart_reduce.x.frg_thr, threadIdx.x));
    __syncthreads();
    // Store the result back to gmem
    auto gx_slab = make_tensor(gx_ptr, cfg.x_tiling.gSlab);
    auto gx_tile = slice_rest(gx_slab, cfg.x_tiling.TileBlock, blockIdx.x);
    CTA_copy_tile(cfg.x_tiling.tile_copy, sx_tile, gx_tile);
}

template<typename Cfg, typename XT, typename xT, typename Fn>
void launch_reduce_kernel(Cfg cfg, XT* gX_ptr, xT* gx_ptr, Fn fn) {
    reduce_kernel<<<cfg.block_num, cfg.thread_num>>>(cfg, gX_ptr, gx_ptr, fn);
}

} // namespace vidrial