#pragma once

#include "../../cutlass/include/cute/tensor.hpp"
#include "../sympow_mma/sympow_mma_cfg.cuh"
#include "../sympow_bwd/tprod_bwd.cuh"
#include "../../cuda_utils/perf_cfg.cuh"
#include "../../cuda_utils/allocator.cuh"
#include "../../cuda_utils/pipeline.cuh"
#include "../../cuda_utils/gemm.cuh"
#include "../../cuda_utils/launch.cuh"
#include "sympow_C_mma_cfg.cuh"

namespace vidrial {

/* ----- fused sympow mma kernel -----
 * This kernel is a function A,B,c -> cdot = sympow_bwd(c, A@B)
 *     (used in the implementation of sympowA_mma_bwd)
 * Kernel uses 2 different coordinate systems for the 2 operations
 *   dims M,N,K,P
 *   A_slab = [M,K,P]  A_tile = [M_tile,K_tile]
 *   B_slab = [N,K,P]  B_tile = [N_tile,K_tile]
 *   C_slab = [M,N,P]  C_tile = [M_tile,N_tile]
 *   dims d,b: using d=M and b=[K,P]
 *   X_slab = [d,b]    X_tile = [d_tile,b_tile]
 *   Z_slab = [D,b]  Z_tile = [D_tile,b_tile]
 *   where D_tile = [d_tile,...]  (repeated power times)
 *   and D = [D_tile,d_tile_num]
 * The two systems are connected via
 *   D = M   and  b = [N,P] and b_tile = [N_tile,1]
 *   Z_slab = [D,[N,P]], X_slab = [d,[N,P]]
 *   C_tile = Z_tile = [D_tile,N_tile], c_tile = X_tile = [d_tile,N_tile]
 * Each CTA in the grid computes an Xgrad_batch of shape [d, b_tile]
 *   CTA_idx = [N_tile_idx, P_tile_idx] (constant through execution)
 *   so that each CTA computes a different c_tile
 * The mainloop has 2 nested loops:
 *   D_tile_idx  ranges  0 -> cfg.D_tile_num
 *       K_tile_idx  ranges  0 -> cfg.K_tile_num
*/ 
template <bool duplicate_correction, bool scale_A, int smempipe_, auto... Is, typename Cfg, typename AT, typename BT, typename CT>
__device__ void mma_sympow_bwd_kernel_impl(int_sequence<Is...>, Cfg cfg, AT* A_ptr, BT* B_ptr, CT* c_ptr, CT* cgrad_ptr, float sA) {
    int tid = threadIdx.x;
    int N_tile_idx = blockIdx.y;
    int P_tile_idx = blockIdx.z;
    // ----- Iterators of the kernel -----
    auto mma_tile_coords = MmaMNKCoords(cfg.mma.MNK_tile_shape);
    mma_tile_coords.step_N(N_tile_idx);
    mma_tile_coords.step_P(P_tile_idx);
    auto sympow_tile_coords = SympowCoords<decltype(cfg.sympow)>{};
    sympow_tile_coords.step_b(N_tile_idx + cfg.mma.N_tile_num * P_tile_idx); // b_tile_idx = [N_tile_idx, P_tile_idx]
    // ------ Global memory slabs ------
    auto gA_slab = make_tensor(make_gmem_ptr(A_ptr), cfg.A.gSlab);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.B.gSlab);
    auto gX_slab = make_tensor(make_gmem_ptr(c_ptr), cfg.X.gSlab); // gc and gX are equivalent
    auto gXgrad_slab = make_tensor(make_gmem_ptr(cgrad_ptr), cfg.gXSlab);
    auto gX_batch = sympow_tile_coords.slice_X_batch(gX_slab);
    // ------ Shared memory tensors ------
    constexpr static int smempipe = static_min(cfg.perf.smempipe, cfg.mma.K_tile_num * cfg.mma.M_tile_num);
    auto pipe = SmemPipe<smempipe>();
    extern __shared__ char smem[];
    Allocator<16> alloc(smem);
    CT* X_smem = alloc.allocate<CT>(int(cosize(cfg.X.sBatch))); // [d, b_tile]
    CT* Xgrd_smem = alloc.allocate<CT>(int(cosize(cfg.X.sBatch))); // [d, b_tile]
    AT* A_smem = alloc.allocate<AT>(size(cfg.A.sTile) * smempipe);
    BT* B_smem = alloc.allocate<BT>(size(cfg.B.sTile) * smempipe);
    auto sA_tile_pipe = pipe.create(A_smem, cfg.A.sTile, cfg.A.tile_copy);
    auto sB_tile_pipe = pipe.create(B_smem, cfg.B.sTile, cfg.B.tile_copy);
    auto sX_batch = make_tensor(make_smem_ptr(X_smem), cfg.X.sBatch); // [d, b_tile]
    auto sXgrad_batch = make_tensor(make_smem_ptr(Xgrd_smem), cfg.X.sBatch); // [d, b_tile]
    using C_Frg_layout = decltype(cfg.C.make_mma_frg().layout());
    using YFrgType = TensorType(declval<decltype(cfg.C.make_mma_frg())>());
    using Ygrad_Frg_layout = decltype(C_Frg_layout{}.compose(cfg.Z_tprod_frg__2__C_mma_frg));
    // ------ Preload X_batch to shared memory ------
    CTA_copy_tile(cfg.X.batch_copy, gX_batch, sX_batch);
    clear(slice_rest(sXgrad_batch, cfg.X.batch_copy.FrgThr, tid)); // Every thread clears a fragment of the Xgrad_batch
    cp_async_fence(); cp_async_wait<0>(); __syncthreads();
    // ------ Pipeline fetch A_tile and B_tile ------
    auto pipe_fetch = [&]() {
        if (mma_tile_coords.valid_K_tile(cfg.K) && mma_tile_coords.valid_M_tile(cfg.M)) {
            auto gA_tile = mma_tile_coords.slice_A_tile(gA_slab);
            auto gB_tile = mma_tile_coords.slice_B_tile(gB_slab);
            pipe.fetch(gA_tile, sA_tile_pipe, cfg.A.tile_copy);
            pipe.fetch(gB_tile, sB_tile_pipe, cfg.B.tile_copy);
            mma_tile_coords.step_K();
            if (mma_tile_coords.K_coord() == cfg.mma.K_tile_num) {
                mma_tile_coords.reset_K();
                mma_tile_coords.step_M();
            }
        }
        pipe.commit();
    };
    // ------ Prefill pipeline ------
    for (; pipe.stage < smempipe - 1; pipe.step())
        pipe_fetch();
    // ------ Main loop ------
    auto rXIgrad_batch_frg = make_tuple(make_tensor<YFrgType>(rXigrad_batch_frg_shape<Is>(cfg.sympow_bwd))...);
    if (threadIdx.x < size<1>(cfg.sympow.X.batch_copy.FrgThr))
        clear(slice_rest(sXgrad_batch, cfg.sympow.X.batch_copy.FrgThr, tid));
    while (sympow_tile_coords.valid_D_tile()) {
        // ------ Register fragments for mma and tprod operations ------
        auto rC_frg_mma = cfg.C.make_mma_frg();
        clear(rC_frg_mma);
        CUTE_UNROLL
        for (int k_tile = 0; k_tile < cfg.mma.K_tile_num; k_tile++) {
            pipe_fetch();
            pipe.ready();
            auto sA_tile = pipe.read(sA_tile_pipe);
            auto sB_tile = pipe.read(sB_tile_pipe);
            vidrial::pipeAB_mma<scale_A>(cfg, sA_tile, sB_tile, rC_frg_mma, sA);
            pipe.step();
        }
        auto rYgrad_tprod_frg = rC_frg_mma.compose(cfg.Z_tprod_frg__2__C_mma_frg);
        if constexpr (duplicate_correction)
            tensor_scalar_prod(rYgrad_tprod_frg, static_cast<YFrgType>(sympow_tile_coords.scale_correction()));
        // We are ready to perform an accumulation step onto Xigrad using the Ygrad_frg
        auto rXi_tprod_frg = sympow_load_Xi_frgs<Is...>(cfg.sympow, sympow_tile_coords, sX_batch);
        (..., sympow_tile_bwd_iter<Is>(cfg.sympow_bwd, sympow_tile_coords, sXgrad_batch, rXIgrad_batch_frg, rXi_tprod_frg, rYgrad_tprod_frg));
        sympow_tile_coords.step_D();
    }
    (..., sympow_tile_bwd_epilogue<Is>(cfg.sympow_bwd, sympow_tile_coords, sXgrad_batch, rXIgrad_batch_frg));
    // ------ Write X_tile to global memory ------
    auto gXgrad_batch = sympow_tile_coords.slice_X_batch(gXgrad_slab);
    CTA_copy_tile(cfg.X.batch_copy, sXgrad_batch, gXgrad_batch);
}
template <bool duplicate_correction, bool scale_A, int smempipe, typename Cfg, typename AT, typename BT, typename CT>
__global__ void mma_sympow_bwd_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* c_ptr, CT* Cgrad_ptr, float sA) {
    mma_sympow_bwd_kernel_impl<duplicate_correction, scale_A, smempipe>(make_int_sequence<cfg.pow>{}, cfg, a_ptr, B_ptr, c_ptr, Cgrad_ptr, sA);
}

template<bool duplicate_correction=true, bool scale_A=false, int smempipe=1, typename Cfg, typename AT, typename BT, typename CT>
int launch_mma_sympow_bwd_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* c_ptr, CT* cgrad_ptr, float sA) {
    dim3 blocks(1, cfg.mma.N_tile_num, cfg.mma.P);
    int threads = cfg.thread_num;
    int smem_size = cfg.smem_size(); // Use calculated instead of hardcoded

    // print("cfg.C.mma_FrgThr "); print(cfg.C.mma_FrgThr); print("\n");
    // print("cfg.C.tileShape "); print(cfg.C.tileShape); print("\n");
    // print("cfg.sympow.X_BatchShape "); print(cfg.sympow.X_BatchShape); print("\n");
    // print("cfg.sympow.Xi<0>.FrgThr "); print(get<0>(cfg.sympow.Xi).tprod_FrgThr); print("\n");
    // print("cfg.sympow.Xi<1>.FrgThr "); print(get<1>(cfg.sympow.Xi).tprod_FrgThr); print("\n");
    
    auto kernel = mma_sympow_bwd_kernel<duplicate_correction, scale_A, smempipe, Cfg, AT, BT, CT>;
    CUDA_CHECK_RETURN(adjust_dynamic_smem_size(kernel, smem_size), "Error setting max dynamic shared memory size");
    kernel<<<blocks,threads,smem_size>>>(cfg, a_ptr, B_ptr, c_ptr, cgrad_ptr, sA);
    return 0;
}

} // namespace vidrial