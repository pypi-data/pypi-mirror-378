#pragma once
#include "sympow_mma_cfg.cuh"
#include "../../cuda_utils/pipeline.cuh"
#include "../../cuda_utils/gemm.cuh"
#include "../../cuda_utils/copy.cuh"
#include "../../cuda_utils/perf_cfg.cuh"
#include "../../cuda_utils/allocator.cuh"
#include "../../cuda_utils/launch.cuh"

namespace vidrial {

/* ----- fused sympow mma kernel -----
* Kernel uses 2 different coordinate systems for the 2 operations
*   dims M,N,K,P
*   A_slab = [M,K,P]  A_tile = [M_tile,K_tile]  A_tile = Z_tile
*   B_slab = [N,K,P]  B_tile = [N_tile,K_tile]
*   C_slab = [M,N,P]  C_tile = [M_tile,N_tile]
*   dims d,b: using d=M and b=[K,P]
*   X_slab = [d,b]    X_tile = [d_tile,b_tile]
*   Z_slab = [D,b]  Z_tile = [D_tile,b_tile]
*   where D_tile = [d_tile,...]  (repeated power times)
*   and D = [D_tile,d_tile_num]
* The two systems are connected via
*   D = M   and  b = [K,P]
*   so A_slab = [D,K,P],  Z_slab = [D,[K,P]], X_slab = [d,[K,P]]
*   A_tile = [D_tile,K_tile], Z_tile = [D_tile,K_tile], X_tile = [d_tile,K_tile]
* The CTAs grid works like in a standard tiled matmul kernel
*   CTA_idx = [M_tile_idx, N_tile_idx, P_tile_idx] (constant through execution)
*   so that each CTA computes a different C_tile
* During the mainloop:
*   K_tile_idx  ranges  0 -> cfg.K_tile_num
*   b_tile_idx  ranges  [0, P_tile_idx] -> [cfg.K_tile_num, P_tile_idx]
*/ 
template <bool duplicate_correction, bool scale_A, auto... Is, typename Cfg, typename AT, typename BT, typename CT>
__device__ void sympow_M_mma_kernel_impl(int_sequence<Is...>, Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr, float sA) {
    static_assert(cfg.expand_K==false, "This kernel is designed to expand M");
    int tid = threadIdx.x;
    int M_tile_idx = blockIdx.x;
    int N_tile_idx = blockIdx.y;
    int P_tile_idx = blockIdx.z;
    // ----- Iterators of the kernel: -----
    auto mma_tile_coords = MmaMNKCoords(cfg.mma.MNK_tile_shape);
    mma_tile_coords.step_M(M_tile_idx);
    mma_tile_coords.step_N(N_tile_idx);
    mma_tile_coords.step_P(P_tile_idx);
    auto sympow_tile_coords = SympowCoords<decltype(cfg.sympow)>{};
    sympow_tile_coords.step_D(M_tile_idx); // d_tile_idx = M_tile_idx
    sympow_tile_coords.step_b(cfg.mma.K_tile_num * P_tile_idx); // b_tile_idx = [0,P_tile_idx]
    // ------ Global memory slabs ------
    auto gX_slab = make_tensor(make_gmem_ptr(a_ptr), cfg.X.gSlab);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.B.gSlab);
    auto gC_slab = make_tensor(make_gmem_ptr(C_ptr), cfg.C.gSlab);
    // ------ Shared memory pipelines ------
    constexpr static int smempipe = static_min(cfg.perf.smempipe, cfg.mma.K_tile_num);
    auto pipe = SmemPipe<smempipe>();
    extern __shared__ char smem[];
    Allocator<16> alloc(smem);
    AT* Xi_smem = alloc.allocate<AT>(int(cfg.X_smem_size) * smempipe);
    BT* B_smem = alloc.allocate<BT>(size(cfg.B.sTile) * smempipe);
    auto sX_tile_pipes = make_tuple(pipe.create(Xi_smem, get<Is>(cfg.Xi).sTile, get<Is>(cfg.Xi).tile_copy, get<Is>(cfg.Xi_smem_offset) * smempipe)...);
    auto sB_tile_pipe = pipe.create(B_smem, cfg.B.sTile, cfg.B.tile_copy);
    // ------ Register fragments for mma and tprod operations ------
    auto rA_frg_mma = cfg.A.make_mma_frg();
    auto rB_frg_mma = cfg.B.make_mma_frg();
    auto rC_frg_mma = cfg.C.make_mma_frg();
    clear(rC_frg_mma);
    auto rXi_tprod_frg = make_tuple(make_tensor<AT>(get<Is>(cfg.Xi).Frg)...);
    auto rY_tprod_frg = rA_frg_mma.compose(cfg.Y_tprod_frg__2__A_mma_frg);
    using YFrgType = TensorType(rY_tprod_frg);
    YFrgType scale = static_cast<YFrgType>(sympow_tile_coords.scale_correction());
    // ------ Pipeline fetch X_tiles and B_tile ------
    auto pipe_fetch = [&]() {
        if (mma_tile_coords.K_coord() < cfg.mma.K_tile_num) {
            auto gX_tiles = make_tuple(sympow_tile_coords.slice_X_tile<Is>(gX_slab)...);
            auto gB_tile = mma_tile_coords.slice_B_tile(gB_slab);
            pipe.fetch(gB_tile, sB_tile_pipe, cfg.B.tile_copy);
            (..., pipe.fetch(get<Is>(gX_tiles), get<Is>(sX_tile_pipes), get<Is>(cfg.Xi).tile_copy));
        }
        sympow_tile_coords.step_b();
        mma_tile_coords.step_K();
        pipe.commit();
    };
    // ------ Prefill pipeline ------
    for (; pipe.stage < smempipe - 1; pipe.step())
        pipe_fetch();
    // ------ Main loop ------
    for (int i = 0; i < cfg.mma.K_tile_num; i++) {
        pipe_fetch();
        pipe.ready();
        auto sB_tile = pipe.read(sB_tile_pipe);
        auto sX_tiles = make_tuple(coalesce_each(pipe.read(get<Is>(sX_tile_pipes)))...);
        (..., (load_frg<AT, cfg.perf.use_ldsm, false>(get<Is>(sX_tiles), get<Is>(cfg.Xi).tprod_FrgThr, get<Is>(rXi_tprod_frg))));
        if constexpr (cfg.perf.regpipe == 0)
            load_frg<BT, cfg.perf.use_ldsm, sizeof(BT) == 2>(sB_tile, cfg.B.mma_FrgThr, rB_frg_mma);
        tprod(rY_tprod_frg, get<Is>(rXi_tprod_frg)...);
        if constexpr (duplicate_correction)
            tensor_scalar_prod(rY_tprod_frg, scale);
        if constexpr (scale_A)
            tensor_scalar_prod(rA_frg_mma, sA);
        vidrial::gemm(cfg, rA_frg_mma, rB_frg_mma, sB_tile, rC_frg_mma);
        pipe.step();
    }
    pipe.finish();
    // ------ Write C_tile to global memory ------
    alloc.reset(smem);
    CT* C_smem = alloc.allocate<CT>(int(size(cfg.C.sTile)));
    auto sC_tile = make_tensor(make_smem_ptr(C_smem), cfg.C.sTile);
    copy(rC_frg_mma, slice_rest(sC_tile, cfg.C.mma_FrgThr, tid));
    __syncthreads();
    auto gC_tile = mma_tile_coords.slice_C_tile(gC_slab);
    CTA_copy_tile(cfg.C.tile_copy, sC_tile, gC_tile);
}
template <bool duplicate_correction, bool scale_A, typename Cfg, typename AT, typename BT, typename CT>
__global__ void sympow_M_mma_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr, float sA) {
    sympow_M_mma_kernel_impl<duplicate_correction, scale_A>(make_int_sequence<cfg.pow>{}, cfg, a_ptr, B_ptr, C_ptr, sA);
}

// ---- Expand the contraction dimension of the A matrix in the matmul -----
template <bool duplicate_correction, bool scale_A, auto... Is, typename Cfg, typename AT, typename BT, typename CT>
__device__ void sympow_K_mma_kernel_impl(int_sequence<Is...>, Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr, float sA) {
    static_assert(cfg.expand_K==true, "This kernel is designed to expand K");
    int tid = threadIdx.x;
    int M_tile_idx = blockIdx.x;
    int N_tile_idx = blockIdx.y;
    int P_tile_idx = blockIdx.z;
    // ----- Iterators of the kernel: -----
    auto mma_tile_coords = MmaMNKCoords(cfg.mma.MNK_tile_shape);
    mma_tile_coords.step_M(M_tile_idx);
    mma_tile_coords.step_N(N_tile_idx);
    mma_tile_coords.step_P(P_tile_idx);
    auto sympow_tile_coords = SympowCoords<decltype(cfg.sympow)>{};
    sympow_tile_coords.step_b(M_tile_idx + cfg.mma.M_tile_num * P_tile_idx);
    // ------ Global memory slabs ------
    auto gX_slab = make_tensor(make_gmem_ptr(a_ptr), cfg.X.gSlab);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.B.gSlab);
    auto gC_slab = make_tensor(make_gmem_ptr(C_ptr), cfg.C.gSlab);
    // ------ Shared memory pipelines ------
    constexpr static int smempipe = cfg.perf.smempipe;
    extern __shared__ char smem[];
    Allocator<16> alloc(smem);
    AT* X_smem = alloc.allocate<AT>(int(size(cfg.X.sBatch)) * smempipe);
    BT* B_smem = alloc.allocate<BT>(size(cfg.B.sTile) * smempipe);
    auto pipe = SmemPipe<smempipe>();
    // ----- Preload X_batch -----
    auto sX_batch = make_tensor(make_smem_ptr(X_smem), cfg.X.sBatch);
    auto gX_batch = sympow_tile_coords.slice_X_batch(gX_slab);
    auto sB_tile_pipe = pipe.create(B_smem, cfg.B.sTile, cfg.B.tile_copy);
    CTA_copy_tile(cfg.X.batch_copy, gX_batch, sX_batch);
    cp_async_fence(); cp_async_wait<0>(); __syncthreads();
    // ------ Register fragments for mma and tprod operations ------
    auto rA_frg_mma = make_tensor<typename Cfg::FrgTypeA>(cfg.A.mma_Frg);
    auto rB_frg_mma = make_tensor<typename Cfg::FrgTypeB>(cfg.B.mma_Frg);
    auto rC_frg_mma = make_tensor<typename Cfg::FrgTypeC>(cfg.C.mma_Frg);
    clear(rC_frg_mma);
    auto rXi_tprod_frg = make_tuple(make_tensor<AT>(get<Is>(cfg.Xi).Frg)...);
    auto rY_tprod_frg = rA_frg_mma.compose(cfg.Y_tprod_frg__2__A_mma_frg);
    using YFrgType = TensorType(rY_tprod_frg);
    //  ----- prefill -----
    auto pipe_fetch = [&]() {
        if (mma_tile_coords.valid_K_tile(cfg.mma.K)) {
            auto gB_tile = mma_tile_coords.slice_B_tile(gB_slab);
            pipe.fetch(gB_tile, sB_tile_pipe, cfg.B.tile_copy);
            mma_tile_coords.step_K();
        }
        pipe.commit();
    };
    for (; pipe.stage < smempipe - 1; pipe.step())
        pipe_fetch();
    //  ----- main loop -----
    while (sympow_tile_coords.valid_D_tile()) {
        pipe_fetch();
        pipe.ready();
        auto sB_tile = pipe.read(sB_tile_pipe);
        if constexpr (cfg.perf.regpipe == 0)
            load_frg<BT, cfg.perf.use_ldsm, sizeof(BT) == 2>(sB_tile, cfg.B.mma_FrgThr, rB_frg_mma);
        auto sXi_tile = make_tuple(sympow_tile_coords.slice_X_tile_from_batch<Is>(sX_batch)...);
        (..., (sympow_tile_coords.D_tile_iter.template last_changed<Is>() ? load_frg<AT, cfg.perf.use_ldsm, false>(get<Is>(sXi_tile), get<Is>(cfg.Xi).tprod_FrgThr, get<Is>(rXi_tprod_frg)) : void()));
        tprod(rY_tprod_frg, get<Is>(rXi_tprod_frg)...);
        if constexpr (duplicate_correction)
            tensor_scalar_prod(rY_tprod_frg, static_cast<YFrgType>(sympow_tile_coords.scale_correction()));
        if constexpr (scale_A)
            tensor_scalar_prod(rA_frg_mma, sA);
        vidrial::gemm(cfg, rA_frg_mma, rB_frg_mma, sB_tile, rC_frg_mma);
        pipe.step();
        sympow_tile_coords.step_D();
    }
    pipe.finish();
    // write back
    alloc.reset(smem);
    CT* C_smem = alloc.allocate<CT>(int(size(cfg.C.sTile)));
    auto sC_tile = make_tensor(make_smem_ptr(C_smem), cfg.C.sTile);
    copy(rC_frg_mma, slice_rest(sC_tile, cfg.C.mma_FrgThr, tid));
    __syncthreads();
    auto gC_tile = mma_tile_coords.slice_C_tile(gC_slab);
    CTA_copy_tile(cfg.C.tile_copy, sC_tile, gC_tile);
}


template <bool duplicate_correction, bool scale_A, typename Cfg, typename AT, typename BT, typename CT>
__global__ void sympow_K_mma_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr, float sA) {
    sympow_K_mma_kernel_impl<duplicate_correction, scale_A>(make_int_sequence<cfg.pow>{}, cfg, a_ptr, B_ptr, C_ptr, sA);
}


template<bool duplicate_correction=true, bool scale_A=false, int smempipe=1, typename Cfg, typename AT, typename BT, typename CT>
int launch_sympow_mma_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr, float sA) {
    dim3 blocks(cfg.mma.M_tile_num, cfg.mma.N_tile_num, cfg.mma.P_tile_num);
    int threads = Cfg::thread_num;
    int smem_size = cfg.smem_size();
    if constexpr (cfg.expand_K) {
        auto kernel = sympow_K_mma_kernel<duplicate_correction, scale_A, Cfg, AT, BT, CT>;
        CUDA_CHECK_RETURN(adjust_dynamic_smem_size(kernel, smem_size), "Error setting max dynamic shared memory size");
        kernel<<<blocks,threads,smem_size>>>(cfg, a_ptr, B_ptr, C_ptr, sA);
    } else {
        auto kernel = sympow_M_mma_kernel<duplicate_correction, scale_A, Cfg, AT, BT, CT>;
        CUDA_CHECK_RETURN(adjust_dynamic_smem_size(kernel, smem_size), "Error setting max dynamic shared memory size");
        kernel<<<blocks,threads,smem_size>>>(cfg, a_ptr, B_ptr, C_ptr, sA);
    }
    CUDA_CHECK_LAST_ERROR("CUDA kernel launch error");
    return 0;
}

template<bool duplicate_correction=true, int smempipe=1, typename Cfg, typename AT, typename BT, typename CT>
int launch_sympow_mma_kernel(Cfg cfg, AT* a_ptr, BT* B_ptr, CT* C_ptr) {
    return launch_sympow_mma_kernel<duplicate_correction, false, smempipe>(cfg, a_ptr, B_ptr, C_ptr, 1.0);
}

} // namespace vidrial