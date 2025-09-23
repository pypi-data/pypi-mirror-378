
#include <cuda.h>
#include <cuda_runtime.h>
#include <iostream>
#include "cute/tensor.hpp"
#include "kernels/flash/kernel.cuh"

using namespace cute;
using namespace vidrial;

extern "C" int launch(void* __raw_Q, void* __raw_K, void* __raw_V, void* __raw_O, void* __raw_l) {
    using T = bfloat16_t;
    using LT = float;
    using Atom1 = MMA_Atom<SM80_16x8x16_F32BF16BF16F32_TN>;
    using Atom2 = MMA_Atom<SM80_16x8x16_F32BF16BF16F32_TN>;
    using MNKTileShape_1 = decltype(static_tree_cast<int64_t>(Shape<Int<64>, Int<128>, Int<64>>{}));
    using NTile2 = decltype(static_tree_cast<int64_t>(Int<64>{}));
    using MNKAtomPlacement_1 = decltype(static_tree_cast<int64_t>(Shape<Int<4>, Int<1>, Int<1>>{}));
    using GQSlab = decltype(static_tree_cast<int64_t>(Layout<Shape<Int<8192>, Int<64>, Int<4>>, Stride<Int<64>, Int<1>, Int<524288>>>{}));
    using GKSlab = decltype(static_tree_cast<int64_t>(Layout<Shape<Int<8192>, Int<64>, Int<4>>, Stride<Int<64>, Int<1>, Int<524288>>>{}));
    using GVSlab = decltype(static_tree_cast<int64_t>(Layout<Shape<Int<64>, Int<8192>, Int<4>>, Stride<Int<1>, Int<64>, Int<524288>>>{}));
    using GOSlab = decltype(static_tree_cast<int64_t>(Layout<Shape<Int<8192>, Int<64>, Int<4>>, Stride<Int<64>, Int<1>, Int<524288>>>{}));
    using GLSlab = decltype(static_tree_cast<int64_t>(Layout<Shape<Int<8192>, Int<4>>, Stride<Int<1>, Int<8192>>>{}));
    using PerfCfg1 = FlashPerfCfg<1, 2, true, 1, false>;
    using PerfCfg2 = PerfCfg<1, 2, true, 1>;
    auto cfg = make_FlashKernelCfg<T, LT, Atom1, MNKTileShape_1, MNKAtomPlacement_1, Atom2, NTile2, GQSlab, GKSlab, GVSlab, GOSlab, GLSlab, PerfCfg1, PerfCfg2>();
    auto Q = reinterpret_cast<T*>(__raw_Q);
    auto K = reinterpret_cast<T*>(__raw_K);
    auto V = reinterpret_cast<T*>(__raw_V);
    auto O = reinterpret_cast<T*>(__raw_O);
    auto l = reinterpret_cast<LT*>(__raw_l);
    return launch_flash_attention_kernel(cfg, Q, K, V, O, l);
}