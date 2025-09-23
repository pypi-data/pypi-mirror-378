#pragma once
#include <type_traits>
#include <cstdio>
#include <tuple>
#include <iostream>
#include "../../cuda_utils/frg_copy.cuh"
#include "../../kernels/flash/flash_cfg.cuh"
#include "../../kernels/reduce/reduce_utils.cuh"
#include "../../cuda_utils/utilities.cuh"
#include "../../cuda_utils/pipeline.cuh"
#include "../../cuda_utils/gemm.cuh"
#include "../../cuda_utils/copy.cuh"
#include "../../cuda_utils/allocator.cuh"
#include "../../cuda_utils/launch.cuh"
#include "../../cuda_utils/softmax.cuh"
#include "../../cuda_utils/frg_copy.cuh"

namespace vidrial {

using namespace cute;

template<typename Cfg>
CUTE_HOST_DEVICE auto make_rQ_frg(Cfg const& cfg) {
    using rQ_frg_t = decltype(cfg.mma1.A.make_mma_frg().layout());
    constexpr auto rQ_frg_all_layout = zipped_product(rQ_frg_t{}, Int<cfg.mma1.K_tile_num>{});
    return make_tensor<Cfg::T>(rQ_frg_all_layout);
}

template<typename LT_, typename MmaCfg1, typename MmaCfg2, typename MaskCfg, typename SoftmaxCfg, typename GLSlab>
void print_cfg(FlashKernelCfg<LT_, MmaCfg1, MmaCfg2, MaskCfg, SoftmaxCfg, GLSlab> const& cfg, std::string prefix = "") {
    std::cout << "FlashKernelCfg:\n";
    std::cout << prefix << "  mma1: "; print_cfg(cfg.mma1, prefix + "  "); std::cout << "\n";
    std::cout << prefix << "  mma2: "; print_cfg(cfg.mma2, prefix + "  "); std::cout << "\n";
    std::cout << prefix << "  mask: "; print_cfg(cfg.mask, prefix + "  "); std::cout << "\n";
    std::cout << prefix << "  softmax: "; print_cfg(cfg.softmax, prefix + "  "); std::cout << "\n";
    std::cout << prefix << "  gLSlab: "; print(cfg.gLSlab); std::cout << "\n";
}


// #define DEBUG 1
#define DEBUG_THREAD (threadIdx.x == 0 && blockIdx.x == 2 && blockIdx.y == 0 && blockIdx.z == 0)

#ifdef DEBUG
#define DEBUG_PRINT_TENSOR(msg) \
    __syncthreads(); \
    store(S_copy_cfg, rS_frg_mma, sS_tile); \
    __syncthreads(); \
    if (DEBUG_THREAD) { \
        print(msg); print_tensor(sS_tile); print("\n"); \
    } \
    __syncthreads()
#else
#define DEBUG_PRINT_TENSOR(msg)
#endif

#ifdef DEBUG
#define DEBUG_PRINT_ROWSUM(msg) \
    __syncthreads(); \
    auto rowsum_frg_copy = make_tensor<LT>(rowsum_frg.layout()); \
    copy(rowsum_frg, rowsum_frg_copy); \
    smart_reduce_cta(cfg.softmax.reduce, rowsum_frg_copy, sRow_tile, SumOp<LT>{}); \
    store(R_copy_cfg, rowsum_frg_copy, sRow_tile); \
    __syncthreads(); \
    if (DEBUG_THREAD) { \
        print(msg); print_tensor(sRow_tile); print("\n"); \
    } \
    __syncthreads()
#else
#define DEBUG_PRINT_ROWSUM(msg)
#endif

template <typename Cfg, typename T, typename LT>
__global__ void __launch_bounds__(Cfg::threads, 1) flash_kernel(Cfg const cfg, T* Q_ptr, T* K_ptr, T* V_ptr, T* O_ptr, LT* l_ptr, float const softmax_scale) {
    int tid = threadIdx.x;
    int bid_M = blockIdx.x; int bid_N = blockIdx.y; int bid_P = blockIdx.z;
    auto coord_qk = MmaMNKCoords(cfg.mma1.MNK_tile_shape);
    auto coord_pv = MmaMNKCoords(cfg.mma2.MNK_tile_shape);
    coord_qk.step_M(bid_M); coord_qk.step_P(bid_P);
    coord_pv.step_M(bid_M); coord_pv.step_N(bid_N); coord_pv.step_P(bid_P);
    auto [mask_start, mask_end] = causal_region(cfg, coord_qk);
    coord_qk.step_N(mask_start); coord_pv.step_K(mask_start);
    // ----- Global memory slabs -----
    auto gQ_slab = make_tensor(make_gmem_ptr(Q_ptr), cfg.mma1.A.gSlab);
    auto gK_slab = make_tensor(make_gmem_ptr(K_ptr), cfg.mma1.B.gSlab);
    auto gV_slab = make_tensor(make_gmem_ptr(V_ptr), cfg.mma2.B.gSlab);
    auto gO_slab = make_tensor(make_gmem_ptr(O_ptr), cfg.mma2.C.gSlab);
    auto gl_slab = make_tensor(make_gmem_ptr(l_ptr), cfg.gLSlab);
    // ----- Shared memory pipelines -----
    constexpr static int smempipe_k = cfg.mma1.perf.smempipe;
    constexpr static int smempipe_v = cfg.mma2.perf.smempipe;
    auto pipe_k = SmemPipe<smempipe_k>();
    auto pipe_v = SmemPipe<smempipe_v>();
    extern __shared__ char smem[];
    Allocator<16> alloc(smem);
    T* Q_smem = alloc.allocate<T>(size(cfg.mma1.A.sTile) * cfg.mma1.K_tile_num);
    if constexpr (cfg.q_in_reg) // Q and the rest can share the same smem if Q is in reg
        alloc.reset(smem);
    T* K_smem = alloc.allocate<T>(size(cfg.mma1.B.sTile) * smempipe_k);
    T* V_smem = alloc.allocate<T>(size(cfg.mma2.B.sTile) * smempipe_v);
    LT* Reduce_smem = nullptr;
    if constexpr (cfg.softmax.reduce.warp_reduce_size > 1)
        Reduce_smem = alloc.allocate<LT>(size(cfg.softmax.reduce.x.shape));
    auto sRow = make_tensor(make_smem_ptr(Reduce_smem), cfg.softmax.reduce.x.shape);
#ifdef DEBUG
    LT* Debug_S_smem = alloc.allocate<LT>(cfg.mma1.M_tile * cfg.mma1.N_tile);
    LT* Debug_Rowmax_smem = alloc.allocate<LT>(cfg.mma1.M_tile);
#endif
    auto pipe_q = SmemPipe<cfg.mma1.K_tile_num>();
    auto sQ_tile_pipe = pipe_q.create(Q_smem, cfg.mma1.A.sTile, cfg.mma1.A.tile_copy);
    auto sK_tile_pipe = pipe_k.create(K_smem, cfg.mma1.B.sTile, cfg.mma1.B.tile_copy);
    auto sV_tile_pipe = pipe_v.create(V_smem, cfg.mma2.B.sTile, cfg.mma2.B.tile_copy);
    decltype(make_rQ_frg(cfg)) rQ_frg;
    if constexpr (cfg.q_in_reg)
        rQ_frg = make_rQ_frg(cfg);
    auto rS_frg_mma = cfg.mma1.C.make_mma_frg();
    auto rP_frg_mma = rS_frg_mma.compose(cfg.mma1_C_frg__2__mma2_A_frg);
    auto rO_frg_mma = cfg.mma2.C.make_mma_frg();
    clear(rO_frg_mma);
#ifdef DEBUG
    auto sS_tile = make_tensor(make_smem_ptr(Debug_S_smem), Shape<Int<cfg.mma1.M_tile>, Int<cfg.mma1.N_tile>>{});
    auto sRow_tile = make_tensor(make_smem_ptr(Debug_Rowmax_smem), cfg.softmax.reduce.x.shape);
    auto S_copy_cfg = make_smem_FrgCopyCfg<LT, decltype(sS_tile.layout()), decltype(cfg.mma1.C.mma_FrgThr), decltype(rS_frg_mma.layout())>();
    auto R_copy_cfg = make_smem_FrgCopyCfg<LT, decltype(sRow_tile.layout()), decltype(cfg.softmax.reduce.x.frg_thr)>();
#endif
    // ----- Pipeline routines -----
    auto preload_Q = [&]() {
        CUTE_UNROLL
        for (int k_tile = 0; k_tile < cfg.mma1.K_tile_num; k_tile++) {
            auto gQ_tile = coord_qk.slice_A_tile(gQ_slab);
            auto sQ_tile = slice_rest(sQ_tile_pipe, k_tile);
            CTA_copy_tile(cfg.mma1.A.tile_copy, gQ_tile, sQ_tile);
            coord_qk.step_K();
        }
        cp_async_fence(); cp_async_wait<0>(); __syncthreads();
        CUTE_UNROLL
        for (int k_tile = 0; k_tile < cfg.mma1.K_tile_num; k_tile++) {
            auto sQ_tile = slice_rest(sQ_tile_pipe, k_tile);
            auto rQ_frg_tile = slice_rest(rQ_frg, k_tile);
            load(cfg.mma1.A.frg_copy, sQ_tile, rQ_frg_tile);
        }
        __syncthreads();
    };
    auto pipe_fetch_QK = [&](int fetch_end) {
        if (coord_qk.valid_K_tile(cfg.mma1.K) && (int)coord_qk.N_coord() < fetch_end) {
            if constexpr (!cfg.q_in_reg) {
                if (coord_qk.N_coord() == mask_start) {
                    auto gQ_tile = coord_qk.slice_A_tile(gQ_slab);
                    pipe_q.fetch(gQ_tile, sQ_tile_pipe, cfg.mma1.A.tile_copy);
                }
            }
            auto gK_tile = coord_qk.slice_B_tile(gK_slab);
            pipe_k.fetch(gK_tile, sK_tile_pipe, cfg.mma1.B.tile_copy);
            coord_qk.step_K();
            if (coord_qk.K_coord() == cfg.mma1.K_tile_num) {
                coord_qk.reset_K();
                if (coord_qk.N_coord() == (mask_end - 1))
                    coord_qk.reset_N();
                else
                    coord_qk.step_N();
            }
        }
        pipe_k.commit();
    };
    auto pipe_fetch_V = [&](int fetch_end) {
        if (coord_pv.valid_K_tile(cfg.mma2.K) && (int)coord_pv.K_coord() < fetch_end) {
            auto gV_tile = coord_pv.slice_B_tile(gV_slab);
            pipe_v.fetch(gV_tile, sV_tile_pipe, cfg.mma2.B.tile_copy);
            if (coord_pv.K_coord() == (mask_end - 1)) 
                coord_pv.reset_K();
            else
                coord_pv.step_K();
        }
        pipe_v.commit();
    };
    // ----- Mma routines -----
    auto qk_mma = [&](int fetch_end) {
        clear(rS_frg_mma);
        CUTE_UNROLL
        for (int k_tile = 0; k_tile < cfg.mma1.K_tile_num; k_tile++) {
            pipe_k.template ready<smempipe_v>();
            auto sK_tile = pipe_k.read(sK_tile_pipe);
            if constexpr (cfg.q_in_reg) {
                auto rQ_frg_tile = slice_rest(rQ_frg, k_tile);
                pipeB_mma(cfg.mma1, rQ_frg_tile, sK_tile, rS_frg_mma);
            } else {
                auto sQ_tile = pipe_q.read(sQ_tile_pipe);
                pipeAB_mma(cfg.mma1, sQ_tile, sK_tile, rS_frg_mma);
                pipe_q.step();
            }
            pipe_k.step(); 
            pipe_fetch_QK(fetch_end);
        }
    };
    auto pv_mma = [&](int fetch_end) {
        pipe_v.template ready<smempipe_k>();
        auto rP_frg = convert_type<T>(rP_frg_mma);
        auto sV_tile = pipe_v.read(sV_tile_pipe);
        pipeB_mma(cfg.mma2, rP_frg, sV_tile, rO_frg_mma);
        pipe_v.step();
        pipe_fetch_V(fetch_end);
    };
    // ----- Preload Q ----- 
    if constexpr (cfg.q_in_reg) {
        preload_Q();
        coord_qk.reset_K();
    }
    // ----- Prefill pipeline ----- 
    CUTE_UNROLL
    for (int i = 0; i < smempipe_v; i++) {
        CUTE_UNROLL
        for (int j = 0; j < cfg.mma1.K_tile_num; j++) {
            pipe_fetch_QK(mask_end);
            if ((i != smempipe_v - 1) || (j != cfg.mma1.K_tile_num - 1))
                pipe_k.step();
            if (i == 0 && j != cfg.mma1.K_tile_num - 1)
                pipe_q.step();
        }
        pipe_fetch_V(mask_end);
        if (i != smempipe_v - 1)
            pipe_v.step();
    }
    // ----- Initialize rowmax and rowsum -----
    auto rowmax_frg = init_tensor<LT, decltype(cfg.softmax.reduce.x.frg_shape)>(-std::numeric_limits<LT>::infinity());
    auto lse_frg = init_tensor<LT, decltype(cfg.softmax.reduce.x.frg_shape)>(static_cast<LT>(0.0f));
    // ----- Main loop 1, masked case -----
    for (int n_tile = mask_start; n_tile < mask_end; n_tile++) {
        auto mstate = make_mask_state(cfg.mask, coord_qk.M_coord() * cfg.mma1.M_tile, n_tile * cfg.mma1.N_tile, (int)cfg.mma1.M, (int)cfg.mma1.N);
        qk_mma(n_tile == mask_end - 1 ? mask_start : mask_end);
        mask_frg(cfg.mask, mstate, rS_frg_mma);
        if (n_tile == mask_start)
            softmax(cfg.softmax, rS_frg_mma, sRow, rowmax_frg, lse_frg, softmax_scale);
        else
            softmax_rescale(cfg.softmax, rS_frg_mma, rO_frg_mma, sRow, rowmax_frg, lse_frg, softmax_scale);
        pv_mma(n_tile == mask_end - 1 ? mask_start : mask_end);
    }
    // ----- Main loop 2, non-masked case ----- 
    for (int n_tile = 0; n_tile < mask_start; n_tile++) {
        qk_mma(mask_start);
        softmax_rescale(cfg.softmax, rS_frg_mma, rO_frg_mma, sRow, rowmax_frg, lse_frg, softmax_scale);
        pv_mma(mask_start);
    }
    pipe_v.finish();
    // ----- Write O and rowsum to global memory -----
    softmax_epilogue(cfg.softmax, rO_frg_mma, lse_frg, sRow);
    alloc.reset(smem);
    T* O_smem = alloc.allocate<T>(size(cfg.mma2.C.sTile));
    auto sO_tile = make_tensor(make_smem_ptr(O_smem), cfg.mma2.C.sTile);
    __syncthreads();
    copy(rO_frg_mma, slice_rest(sO_tile, cfg.mma2.C.mma_FrgThr, tid));
    __syncthreads();
    auto gO_tile = coord_pv.slice_C_tile(gO_slab);
    auto gL_tile = coord_pv.slice_L_tile(gl_slab);
    if (cfg.softmax.reduce.owns_frg())
        copy(lse_frg, slice_rest(gL_tile, cfg.softmax.reduce.x.frg_thr, tid));
    CTA_copy_tile(cfg.mma2.C.tile_copy, sO_tile, gO_tile);
}

int launch_flash_attention_kernel(auto cfg, auto Q_ptr, auto K_ptr, auto V_ptr, auto O_ptr, auto l_ptr, float softmax_scale) {
    dim3 blocks(cfg.mma2.M_tile_num, cfg.mma2.N_tile_num, cfg.mma2.P_tile_num);
    int threads = int(size(cfg.mma2.Threads));
    using T = typename decltype(cfg)::T;
    using LT = typename decltype(cfg)::LT;
    int smem_size = cfg.smem_size();
#ifdef DEBUG
    smem_size += cfg.mma1.M_tile * cfg.mma1.N_tile * sizeof(LT);
#endif
    auto kernel = &flash_kernel<decltype(cfg), T, LT>;
    CUDA_CHECK_RETURN(adjust_dynamic_smem_size(kernel, smem_size), "Error setting max dynamic shared memory size");
    if constexpr (cfg.softmax.log2)
        softmax_scale *= cfg.softmax.LOG2E;
    kernel<<<blocks, threads, smem_size>>>(cfg, Q_ptr, K_ptr, V_ptr, O_ptr, l_ptr, softmax_scale);
    CUDA_CHECK_LAST_ERROR("CUDA kernel launch error");
    return 0;
}


} // namespace vidrial