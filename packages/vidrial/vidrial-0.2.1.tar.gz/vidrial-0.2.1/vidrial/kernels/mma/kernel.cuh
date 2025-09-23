#pragma once
#include "mma_cfg.cuh"
#include "../../cuda_utils/copy.cuh"
#include "../../cuda_utils/gemm.cuh"
#include "../../cuda_utils/pipeline.cuh"
#include "../../cuda_utils/launch.cuh"
#include "../../cuda_utils/allocator.cuh"
namespace vidrial {

template <typename Cfg, typename T>
__global__ void tiled_mma_kernel(Cfg cfg, T* A_ptr, T* B_ptr, T* C_ptr) {
    int tid = threadIdx.x;
    int bid_M = blockIdx.x; int bid_N = blockIdx.y; int bid_P = blockIdx.z;
    auto tile_coords = MmaMNKCoords(cfg.MNK_tile_shape);
    tile_coords.step_M(blockIdx.x); tile_coords.step_N(blockIdx.y); tile_coords.step_P(blockIdx.z);
    // ----- Global memory slabs -----
    auto gA_slab = make_tensor(make_gmem_ptr(A_ptr), cfg.A.gSlab);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.B.gSlab);
    auto gC_slab = make_tensor(make_gmem_ptr(C_ptr), cfg.C.gSlab);
    // ----- Shared memory pipelines -----
    constexpr static int smempipe = static_min(cfg.perf.smempipe, cfg.K_tile_num);
    auto pipe = SmemPipe<smempipe>();
    extern __shared__ char smem[];
    Allocator<16> alloc(smem);
    T* A_smem = alloc.allocate<T>(size(cfg.A.sTile) * smempipe);
    T* B_smem = alloc.allocate<T>(size(cfg.B.sTile) * smempipe);
    auto sA_tile_pipe = pipe.create(A_smem, cfg.A.sTile, cfg.A.tile_copy);
    auto sB_tile_pipe = pipe.create(B_smem, cfg.B.sTile, cfg.B.tile_copy);
    auto rA_frg_mma = cfg.A.make_mma_frg();
    auto rB_frg_mma = cfg.B.make_mma_frg();
    auto rC_frg_mma = cfg.C.make_mma_frg();
    clear(rC_frg_mma);
    // ----- Pipeline fetch A_tile and B_tile -----
    auto pipe_fetch = [&]() {
        if (tile_coords.valid_K_tile(cfg.K)) {
            auto gA_tile = tile_coords.slice_A_tile(gA_slab);
            auto gB_tile = tile_coords.slice_B_tile(gB_slab);
            pipe.fetch(gA_tile, sA_tile_pipe, cfg.A.tile_copy);
            pipe.fetch(gB_tile, sB_tile_pipe, cfg.B.tile_copy);
            tile_coords.step_K();
        }
        pipe.commit();
    };
    // ----- Prefill pipeline -----
    for (; pipe.stage < smempipe - 1; pipe.step())
        pipe_fetch();
    // ----- Main loop -----
    for (int k_tile = 0; k_tile < cfg.K_tile_num; k_tile++) {
        pipe_fetch();
        pipe.ready();
        auto sA_tile = pipe.read(sA_tile_pipe);
        auto sB_tile = pipe.read(sB_tile_pipe);
        load_frg<T, cfg.perf.use_ldsm, false>(sA_tile, cfg.A.mma_FrgThr, rA_frg_mma);
        if constexpr (cfg.perf.regpipe == 0)
            load_frg<T, cfg.perf.use_ldsm, false>(sB_tile, cfg.B.mma_FrgThr, rB_frg_mma);
        vidrial::gemm(cfg, rA_frg_mma, rB_frg_mma, sB_tile, rC_frg_mma);
        pipe.step();
    }
    pipe.finish();
    // ----- Write C_tile to global memory -----
    alloc.reset(smem);
    T* C_smem = alloc.allocate<T>(size(cfg.C.sTile));
    auto sC_tile = make_tensor(make_smem_ptr(C_smem), cfg.C.sTile);
    copy(rC_frg_mma, slice_rest(sC_tile, cfg.C.mma_FrgThr, tid));
    __syncthreads();
    auto gC_tile = tile_coords.slice_C_tile(gC_slab);
    CTA_copy_tile(cfg.C.tile_copy, sC_tile, gC_tile);
}

int launch_tiled_mma_kernel(auto cfg, auto A_ptr, auto B_ptr, auto C_ptr) {
    dim3 blocks(cfg.M_tile_num, cfg.N_tile_num, cfg.P_tile_num);
    int threads = int(size(cfg.Threads));
    using T = typename decltype(cfg)::T;
    int smem_size = cfg.smem_size();
    auto kernel = tiled_mma_kernel<decltype(cfg), T>;
    CUDA_CHECK_RETURN(adjust_dynamic_smem_size(kernel, smem_size), "Error setting max dynamic shared memory size");
    kernel<<<blocks, threads, smem_size>>>(cfg, A_ptr, B_ptr, C_ptr);
    CUDA_CHECK_LAST_ERROR("CUDA kernel launch error");
    return 0;
}

} // namespace vidrial
