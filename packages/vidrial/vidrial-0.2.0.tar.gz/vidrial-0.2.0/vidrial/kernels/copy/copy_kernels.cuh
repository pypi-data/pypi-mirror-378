#pragma once
#include "copy_cfg.cuh"

namespace vidrial {

// ------------- Example Kernels -------------
template<typename T, typename Cfg>
__global__ void tensor_scalar_add_kernel(Cfg cfg, T* A_ptr, T* B_ptr, T scalar) {
    static_assert(is_same<T, typename Cfg::T>::value);
    int tid = threadIdx.x; int bid = blockIdx.x;
    auto gA_slab = make_tensor(make_gmem_ptr(A_ptr), cfg.gSlab);
    auto gA_tile = slice_rest(gA_slab, cfg.TileBlock, bid);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.gSlab);
    auto gB_tile = slice_rest(gB_slab, cfg.TileBlock, bid);
    __shared__ T smem[int(size(cfg.sTile))];
    auto sA_tile = make_tensor(make_smem_ptr(smem), cfg.sTile);
    if (tid < size<1>(cfg.tile_copy.FrgThr)) {
        copy(cfg.tile_copy.g2s_atom,
            slice_rest(gA_tile, cfg.tile_copy.FrgThr, tid),
            slice_rest(sA_tile, cfg.tile_copy.FrgThr, tid));
        cp_async_fence(); cp_async_wait<0>(); __syncthreads();
        auto rA_frg = make_tensor<T>(cfg.tile_copy.Frg);
        copy(slice_rest(sA_tile, cfg.tile_copy.FrgThr, tid), rA_frg);
        add_tensor_scalar(rA_frg, scalar);
        copy(cfg.tile_copy.universal_atom,
            rA_frg,
            slice_rest(gB_tile, cfg.tile_copy.FrgThr, tid));
    }
}

template<typename Cfg, typename SPtr, typename DPtr>
__global__ void tiled_move_kernel(Cfg cfg, SPtr S_ptr, DPtr D_ptr) {
    using T = typename Cfg::T;
    int tid = threadIdx.x; int bid = blockIdx.x;
    auto gS_slab = make_tensor(make_gmem_ptr(S_ptr), cfg.S.gSlab);
    auto gD_slab = make_tensor(make_gmem_ptr(D_ptr), cfg.D.gSlab);
    auto gS_tile = slice_rest(gS_slab, cfg.S.TileBlock, bid);
    auto gD_tile = slice_rest(gD_slab, cfg.D.TileBlock, bid);
    __shared__ T smem[int(size(cfg.sTile))];
    auto s_tile = make_tensor(make_smem_ptr(smem), cfg.sTile);
    copy(cfg.S.tile_copy.g2s_atom,
        slice_rest(gS_tile, cfg.S.tile_copy.FrgThr, tid),
        slice_rest(s_tile, cfg.S.tile_copy.FrgThr, tid));
    cp_async_fence(); cp_async_wait<0>(); __syncthreads();
    copy(cfg.D.tile_copy.universal_atom,
         slice_rest(s_tile, cfg.D.tile_copy.FrgThr, tid),
         slice_rest(gD_tile, cfg.D.tile_copy.FrgThr, tid));
}

} // namespace vidrial