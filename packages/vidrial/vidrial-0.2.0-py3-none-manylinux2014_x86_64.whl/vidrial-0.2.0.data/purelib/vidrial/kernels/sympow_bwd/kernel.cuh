#pragma once
#include "../sympow/sympow_cfg.cuh"
#include "tprod_bwd.cuh"

namespace vidrial {

// -------------- Example Kernels using TprodCfg --------------
template <bool duplicate_correction, auto... Is, typename Cfg, typename XPtr, typename ZGradPtr, typename XGradPtr>
__device__ void tiled_sympow_bwd_kernel_impl(index_sequence<Is...>, Cfg cfg, XPtr X_ptr, ZGradPtr Zgrad_ptr, XGradPtr Xgrad_ptr) {
    using T = typename Cfg::T;
    int tid = threadIdx.x; int bid = blockIdx.x;
    // ----- Iterators of the kernel -----
    auto sympow_tile_coords = typename Cfg::Coords{};
    sympow_tile_coords.step_b(bid);
    // ------ Global memory slabs ------
    auto gX_slab = make_tensor(make_gmem_ptr(X_ptr), cfg.fwd.X.gSlab);
    auto gZgrad_slab = make_tensor(make_gmem_ptr(Zgrad_ptr), cfg.fwd.Z.gSlab);
    auto gXgrad_slab = make_tensor(make_gmem_ptr(Xgrad_ptr), cfg.fwd.X.gSlab);
    auto gX_batch = sympow_tile_coords.slice_X_batch(gX_slab);
    // ------ Shared memory tensors ------
    __shared__ alignas(16) T Z_smem[int(cosize(cfg.fwd.Z.sTile))];
    __shared__ alignas(16) T X_smem[int(cosize(cfg.fwd.X.sBatch))];
    __shared__ alignas(16) T Xgrad_smem[int(cosize(cfg.fwd.X.sBatch))];
    auto sZgrad_tile = make_tensor(make_smem_ptr(Z_smem), cfg.fwd.Z.sTile);
    auto sX_batch = make_tensor(make_smem_ptr(X_smem), cfg.fwd.X.sBatch);
    auto sXgrad_batch = make_tensor(make_smem_ptr(Xgrad_smem), cfg.fwd.X.sBatch);
    CTA_copy_tile(cfg.fwd.X.batch_copy, gX_batch, sX_batch);
    if (threadIdx.x < size<1>(cfg.fwd.X.batch_copy.FrgThr))
        clear(slice_rest(sXgrad_batch, cfg.fwd.X.batch_copy.FrgThr, tid));
    cp_async_fence(); cp_async_wait<0>(); __syncthreads();
    auto sZgrad_copy_frg = slice_rest(sZgrad_tile, cfg.fwd.Z.tile_copy.FrgThr, threadIdx.x);
    auto rYgrad_tprod_frg = make_tensor<T>(cfg.fwd.Z.Frg);
    auto rXIgrad_batch_frg = make_tuple(make_rXigrad_batch_frg<Is>(cfg)...);
    // ----- Main loop -----
    while (sympow_tile_coords.valid_D_tile()) {
        auto gZgrad_tile = sympow_tile_coords.slice_Z_tile(gZgrad_slab);
        CTA_copy_tile(cfg.fwd.Z.tile_copy, gZgrad_tile, sZgrad_tile);
        cp_async_fence(); cp_async_wait<0>(); __syncthreads(); // ensure the sZgrad_tile is ready
        copy(slice_rest(sZgrad_tile, cfg.fwd.Z.tprod_FrgThr, threadIdx.x), rYgrad_tprod_frg);
        if constexpr (duplicate_correction)
            tensor_scalar_prod(rYgrad_tprod_frg, static_cast<T>(sympow_tile_coords.scale_correction()));
        auto rXi_tprod_frg = sympow_load_Xi_frgs<Is...>(cfg.fwd, sympow_tile_coords, sX_batch);
        (..., sympow_tile_bwd_iter<Is>(cfg, sympow_tile_coords, sXgrad_batch, rXIgrad_batch_frg, rXi_tprod_frg, rYgrad_tprod_frg));
        sympow_tile_coords.step_D();
    }
    (..., sympow_tile_bwd_epilogue<Is>(cfg, sympow_tile_coords, sXgrad_batch, rXIgrad_batch_frg));
    auto gXgrad_batch = sympow_tile_coords.slice_X_batch(gXgrad_slab);
    CTA_copy_tile(cfg.fwd.X.batch_copy, sXgrad_batch, gXgrad_batch);
}

template <bool duplicate_correction, typename Cfg, typename XPtr, typename ZGradPtr, typename XGradPtr>
__global__ void tiled_sympow_bwd_kernel(Cfg cfg, XPtr X_ptr, ZGradPtr Zgrad_ptr, XGradPtr Xgrad_ptr) {
    tiled_sympow_bwd_kernel_impl<duplicate_correction>(make_index_sequence<cfg.fwd.p>{}, cfg, X_ptr, Zgrad_ptr, Xgrad_ptr);
}
template<bool duplicate_correction, typename Cfg, typename XPtr, typename ZGradPtr, typename XGradPtr>
int launch_tiled_sympow_bwd_kernel(Cfg cfg, XPtr X_ptr, ZGradPtr Zgrad_ptr, XGradPtr Xgrad_ptr) {
    int blocks = cfg.fwd.b_tile_num;
    int threads = cfg.fwd.thread_num;
    tiled_sympow_bwd_kernel<duplicate_correction><<<blocks, threads>>>(cfg, X_ptr, Zgrad_ptr, Xgrad_ptr);
    CUDA_CHECK_LAST_ERROR("CUDA kernel launch error");
    return 0;
}

} // namespace vidrial