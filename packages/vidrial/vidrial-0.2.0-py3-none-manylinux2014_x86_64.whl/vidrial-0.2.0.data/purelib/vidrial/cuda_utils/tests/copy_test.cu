#include <gtest/gtest.h>
#include <cuda_runtime.h>
#include "utilities.cuh"
#include "frg_copy.cuh"

using namespace cute;

namespace vidrial {
namespace {

template<typename Cfg>
__global__ void test_g2r2g_copy(Cfg cfg, auto gA, auto gB) {
    auto frg = load(cfg, gA);
    store(cfg, frg, gB);
}


template<typename T, typename Cfg1, typename Cfg2, typename SmemLayout>
__global__ void test_g2r2s2r2g_copy(Cfg1 cfg_global, Cfg2 cfg_shared, auto gA, SmemLayout smem_layout, auto gB) {
    alignas(16) __shared__ T smem[size(smem_layout)];
    auto sA = make_tensor(make_smem_ptr(smem), smem_layout);
    auto frg = load(cfg_global, gA);
    store(cfg_shared, frg, sA);
    auto frg_reloaded = load(cfg_shared, sA);
    store(cfg_global, frg_reloaded, gB);
}


template<typename T, typename Cfg1, typename Cfg2, typename Cfg3, typename SmemLayout>
__global__ void test_g2r2s2r2g_copy(Cfg1 cfg_global_A, Cfg2 cfg_shared, Cfg3 cfg_global_B, auto gA, SmemLayout smem_layout, auto gB) {
    alignas(16) __shared__ T smem[size(smem_layout)];
    auto sA = make_tensor(make_smem_ptr(smem), smem_layout);
    auto frg = load(cfg_global_A, gA);
    store(cfg_shared, frg, sA);
    auto frg_reloaded = load(cfg_shared, sA);
    store(cfg_global_B, frg_reloaded, gB);
}


template<typename Cfg, typename ExpectedLoadAtom, typename ExpectedStoreAtom>
void check_cfg(Cfg cfg, ExpectedLoadAtom expected_load_atom, ExpectedStoreAtom expected_store_atom) {
#if 0
    print("--------------------------------\n");
    printf("LoadAtom: %s\n", typeid(typename Cfg::LoadAtom).name());
    printf("StoreAtom: %s\n", typeid(typename Cfg::StoreAtom).name());
#else
    static_assert(is_same_v<typename Cfg::LoadAtom, ExpectedLoadAtom>, "LoadAtom mismatch");
    static_assert(is_same_v<typename Cfg::StoreAtom, ExpectedStoreAtom>, "StoreAtom mismatch");
#endif
}


TEST(CopyTest, G2R2G_simple) {
    using ProblemShape = Shape<_32,_32>;
    auto frgthr = make_layout(ProblemShape{}, LayoutLeft{});
    auto cfg = make_FrgCopyCfg<float, decltype(frgthr)>();
    auto gA = make_managed_tensor<float>(make_layout(ProblemShape{}, LayoutLeft{}));
    auto gB = make_managed_tensor<float>(make_layout(ProblemShape{}, LayoutRight{}));
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<float>(i);

    test_g2r2g_copy<<<1, cfg.thread_num>>>(cfg, gA, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

TEST(CopyTest, G2R2S2R2G_simple) {
    using T = float;
    using ProblemShape = Shape<_32,_32>;
    auto frgthr = make_layout(ProblemShape{}, LayoutLeft{});
    auto cfg_global = make_FrgCopyCfg<T, decltype(frgthr)>();
    auto cfg_shared = make_FrgCopyCfg<T, decltype(frgthr)>();
    auto gA = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutLeft{}));
    auto gB = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutRight{}));
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);

    test_g2r2s2r2g_copy<T><<<1, cfg_global.thread_num>>>(cfg_global, cfg_shared, gA, ProblemShape{}, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

TEST(CopyTest, G2R2S2R2G_LDSMx1_float) {
    using T = float;
    using ProblemShape = Shape<_32,_32>;
    using CopyAtom = Copy_Atom<SM75_U32x1_LDSM_N, T>;
    auto frgthr = make_layout(ProblemShape{}, LayoutRight{});
    auto cfg_global = make_FrgCopyCfg<T, decltype(frgthr)>();
    auto cfg_shared = make_FrgCopyCfg<T, decltype(frgthr), CopyAtom>();
    auto gA = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutLeft{}));
    auto gB = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutRight{}));
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);

    test_g2r2s2r2g_copy<T><<<1, cfg_global.thread_num>>>(cfg_global, cfg_shared, gA, ProblemShape{}, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

TEST(CopyTest, G2R2S2R2G_LDSMx1_fp16) {
    using T = cutlass::half_t;
    using ProblemShape = Shape<_32,_32>;
    using CopyAtom = Copy_Atom<SM75_U32x1_LDSM_N, T>;
    auto frgthr = make_layout(Shape<Shape<_2,_16>,Shape<_4,_8>>{}, Stride<Stride<_1,_8>,Stride<_2,_128>>{});
    auto smem_layout = make_layout(ProblemShape{}, LayoutLeft{});
    auto cfg_global = make_FrgCopyCfg<T, decltype(frgthr)>();
    auto cfg_shared = make_FrgCopyCfg<T, decltype(frgthr), CopyAtom>();
    auto gA = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutLeft{}));
    auto gB = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutRight{}));
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);

    test_g2r2s2r2g_copy<T><<<1, cfg_global.thread_num>>>(cfg_global, cfg_shared, gA, smem_layout, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

TEST(CopyTest, G2R2S2R2G_LDSMx4) {
    using T = float;
    using ProblemShape = Shape<_32,_32>;
    using CopyAtom = Copy_Atom<SM75_U32x4_LDSM_N, T>;
    auto frgthr = make_layout(ProblemShape{}, LayoutRight{});
    auto cfg_global = make_FrgCopyCfg<T, decltype(frgthr)>();
    auto cfg_shared = make_FrgCopyCfg<T, decltype(frgthr), CopyAtom>();
    auto gA = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutLeft{}));
    auto gB = make_managed_tensor<T>(make_layout(ProblemShape{}, LayoutRight{}));
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);

    test_g2r2s2r2g_copy<T><<<1, cfg_global.thread_num>>>(cfg_global, cfg_shared, gA, ProblemShape{}, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}



TEST(CopyTest, G2R2S2R2G_infer_atom) {
    using T = cutlass::half_t;
    using ProblemShape = Shape<_32,_32>;

    auto frgthr = make_layout(Shape<Shape<_2,_16>,Shape<_4,_8>>{}, Stride<Stride<_1,_8>,Stride<_2,_128>>{});
    auto gTileA = make_layout(ProblemShape{}, LayoutLeft{});
    auto gTileB = make_layout(ProblemShape{}, LayoutRight{});
    auto sTile = make_layout(ProblemShape{}, LayoutLeft{});
    auto cfg_global_A = make_gmem_FrgCopyCfg<T, decltype(gTileA), decltype(frgthr)>();
    auto cfg_shared = make_smem_FrgCopyCfg<T, decltype(sTile), decltype(frgthr)>();
    auto cfg_global_B = make_gmem_FrgCopyCfg<T, decltype(gTileB), decltype(frgthr)>();
    auto gA = make_managed_tensor<T>(gTileA);
    auto gB = make_managed_tensor<T>(gTileB);
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);
    
    check_cfg(cfg_global_A, 
        AutoVectorizingCopyWithAssumedAlignment<32>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_shared, 
        Copy_Atom<SM75_U32x4_LDSM_N, T>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_global_B, 
        AutoVectorizingCopyWithAssumedAlignment<8>{},
        AutoVectorizingCopyWithAssumedAlignment<8>{});

    test_g2r2s2r2g_copy<T><<<1, cfg_global_A.thread_num>>>(cfg_global_A, cfg_shared, cfg_global_B, gA, sTile, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

TEST(CopyTest, G2R2S2R2G_infer_atom_debug) {
    using T = cutlass::half_t;
    using ProblemShape = Shape<_32,_32>;
    using ExpectedCopyAtom = Copy_Atom<SM75_U32x1_LDSM_N, T>;
    auto frgthr = make_layout(Shape<Shape<_2,_16>,Shape<_4,_8>>{}, Stride<Stride<_1,_8>,Stride<_2,_128>>{});
    auto sTile = make_layout(ProblemShape{}, LayoutLeft{});
    

    using Atom1 = DefaultCopy;
    auto atom1_compatible = is_compatible<false, false, T, Atom1, decltype(frgthr), decltype(sTile)>();
    // printf("atom1_compatible: %s\n", atom1_compatible ? "true" : "false");

}

TEST(CopyTest, infer_frgthr_vary_thread_num) {
    using T = cutlass::half_t;
    using SmemLayout = decltype(make_layout(Shape<_32,_32>{}, LayoutLeft{}));
    auto frgthr_1 = infer_frgthr<32, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_1), Layout<Shape<Shape<_2,_16>,Shape<_32>>, Stride<Stride<_1,_64>,Stride<_2>>>>);

    auto frgthr_2 = infer_frgthr<16, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_2), Layout<Shape<Shape<_4,_16>,Shape<_16>>, Stride<Stride<_1,_64>,Stride<_4>>>>);

    auto frgthr_3 = infer_frgthr<8, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_3), Layout<Shape<Shape<_8,_16>,Shape<_8>>, Stride<Stride<_1,_64>,Stride<_8>>>>);

    auto frgthr_4 = infer_frgthr<4, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_4), Layout<Shape<Shape<_16,_16>,Shape<_4>>, Stride<Stride<_1,_64>,Stride<_16>>>>);

    auto frgthr_5 = infer_frgthr<2, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_5), Layout<Shape<Shape<_32,_16>,Shape<_2>>, Stride<Stride<_1,_64>,Stride<_32>>>>);

    auto frgthr_6 = infer_frgthr<1, T, SmemLayout>();
    static_assert(is_same_v<decltype(frgthr_6), Layout<Shape<Shape<_64,_16>,Shape<_1>>, Stride<Stride<_1,_64>,Stride<_0>>>>);
}


TEST(CopyTest, infer_frgthr_vary_tile_layout) {
    using T = cutlass::half_t;
    auto frgthr_1 = coalesce_each(infer_frgthr<32, T, decltype(make_layout(Shape<_32,_32>{}, LayoutLeft{}))>());
    auto frgthr_1_expected = coalesce_each(make_layout(Shape<Shape<_2,_16>,Shape<_32>>{}, Stride<Stride<_1,_64>,Stride<_2>>{}));
    static_assert(is_same_v<decltype(frgthr_1), decltype(frgthr_1_expected)>);

    auto frgthr_2 = coalesce_each(infer_frgthr<32, T, decltype(make_layout(Shape<_32,_32>{}, LayoutRight{}))>());
    auto frgthr_2_expected = coalesce_each(make_layout(Shape<Shape<_2,_16>,Shape<_16, _2>>{}, Stride<Stride<_32, _2>,Stride<_64,_1>>{}));
    static_assert(is_same_v<decltype(frgthr_2), decltype(frgthr_2_expected)>);
}


TEST(CopyTest, infer_frgthr_vary_tile_size) {
    using T = cutlass::half_t;
    auto frgthr_1 = coalesce_each(infer_frgthr<32, T, decltype(make_layout(Shape<_4,_4>{}, LayoutLeft{}))>());
    auto frgthr_1_expected = coalesce_each(make_layout(Shape<_1,_16>{}, Stride<_0, _1>{}));
    static_assert(is_same_v<decltype(frgthr_1), decltype(frgthr_1_expected)>);

    auto frgthr_2 = coalesce_each(infer_frgthr<32, T, decltype(make_layout(Shape<_1,_16>{}, LayoutLeft{}))>());
    auto frgthr_2_expected = coalesce_each(make_layout(Shape<_1,_16>{}, Stride<_0, _1>{}));
    static_assert(is_same_v<decltype(frgthr_2), decltype(frgthr_2_expected)>);

    auto frgthr_3 = coalesce_each(infer_frgthr<8, T, decltype(make_layout(Shape<_1,_16>{}, LayoutLeft{}))>());
    auto frgthr_3_expected = coalesce_each(make_layout(Shape<_2,_8>{}, Stride<_1, _2>{}));
    static_assert(is_same_v<decltype(frgthr_3), decltype(frgthr_3_expected)>);
}


TEST(CopyTest, infer_frgthr_vary_type) {
    using T1 = cutlass::half_t;
    using T2 = float;

    auto frgthr_1 = coalesce_each(infer_frgthr<32, T1, decltype(make_layout(Shape<_32,_32>{}, LayoutLeft{}))>());
    auto frgthr_1_expected = coalesce_each(make_layout(Shape<Shape<_2,_16>,Shape<_32>>{}, Stride<Stride<_1,_64>,Stride<_2>>{}));
    static_assert(is_same_v<decltype(frgthr_1), decltype(frgthr_1_expected)>);

    auto frgthr_2 = coalesce_each(infer_frgthr<32, T2, decltype(make_layout(Shape<_32,_32>{}, LayoutLeft{}))>());
    auto frgthr_2_expected = coalesce_each(make_layout(Shape<_32,_32>{}, Stride<_32,_1>{}));
    static_assert(is_same_v<decltype(frgthr_2), decltype(frgthr_2_expected)>);
}

TEST(CopyTest, G2R2S2R2G_infer_frgthr) {
    using T = cutlass::half_t;
    using ProblemShape = Shape<_32,_32>;

    auto gTileA = make_layout(ProblemShape{}, LayoutLeft{});
    auto gTileB = make_layout(ProblemShape{}, LayoutRight{});
    auto sTile = make_layout(ProblemShape{}, LayoutLeft{});
    auto cfg_shared = make_smem_FrgCopyCfg<T, decltype(sTile), 32>();
    auto cfg_global_A = make_gmem_FrgCopyCfg<T, decltype(gTileA), decltype(cfg_shared.frgthr)>();
    auto cfg_global_B = make_gmem_FrgCopyCfg<T, decltype(gTileB), decltype(cfg_shared.frgthr)>();
    auto gA = make_managed_tensor<T>(gTileA);
    auto gB = make_managed_tensor<T>(gTileB);
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);

    check_cfg(cfg_global_A, 
        AutoVectorizingCopyWithAssumedAlignment<32>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_shared, 
        Copy_Atom<SM75_U32x4_LDSM_N, T>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_global_B, 
        AutoVectorizingCopyWithAssumedAlignment<16>{},
        AutoVectorizingCopyWithAssumedAlignment<16>{});

    test_g2r2s2r2g_copy<T><<<1, cfg_global_A.thread_num>>>(cfg_global_A, cfg_shared, cfg_global_B, gA, sTile, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}


TEST(CopyTest, G2R2S2R2G_infer_atom_bf16) {
    using T = cutlass::bfloat16_t;
    using ProblemShape = Shape<_32,_64>;

    auto frgthr = make_layout(Shape<Shape<Shape<_2,_2>, Shape<_2, _8>>, Shape<_4,_8>>{}, Stride<Stride<Stride<_32,_8>, Stride<_16, _256>>, Stride<_64,_1>>{});
    auto gTileA = make_layout(ProblemShape{}, LayoutLeft{});
    auto gTileB = make_layout(ProblemShape{}, LayoutRight{});
    auto sTile = make_layout(ProblemShape{}, LayoutRight{});

    // using Atom1 = Copy_Atom<SM75_U32x1_LDSM_N, T>;
    // auto atom1_compatible = is_compatible<true, false, T, Atom1, decltype(frgthr), decltype(sTile)>();
    // printf("atom1_compatible: %s\n", atom1_compatible ? "true" : "false");

    auto cfg_global_A = make_gmem_FrgCopyCfg<T, decltype(gTileA), decltype(frgthr)>();
    auto cfg_shared = make_smem_FrgCopyCfg<T, decltype(sTile), decltype(frgthr)>();
    auto cfg_global_B = make_gmem_FrgCopyCfg<T, decltype(gTileB), decltype(frgthr)>();
    auto gA = make_managed_tensor<T>(gTileA);
    auto gB = make_managed_tensor<T>(gTileB);
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);
    
    check_cfg(cfg_global_A, 
        AutoVectorizingCopyWithAssumedAlignment<16>{}, 
        AutoVectorizingCopyWithAssumedAlignment<16>{});
    check_cfg(cfg_shared, 
        Copy_Atom<SM75_U32x4_LDSM_N, T>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_global_B, 
        AutoVectorizingCopyWithAssumedAlignment<32>{},
        AutoVectorizingCopyWithAssumedAlignment<32>{});

    test_g2r2s2r2g_copy<T><<<1, cfg_global_A.thread_num>>>(cfg_global_A, cfg_shared, cfg_global_B, gA, sTile, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}


TEST(CopyTest, G2R2S2R2G_swizzle) {
    using T = cutlass::bfloat16_t;
    using ProblemShape = Shape<_32,_64>;

    auto frgthr = make_layout(Shape<Shape<Shape<_2,_2>, Shape<_2, _8>>, Shape<_4,_8>>{}, Stride<Stride<Stride<_32,_8>, Stride<_16, _256>>, Stride<_64,_1>>{});
    auto gTileA = make_layout(ProblemShape{}, LayoutLeft{});
    auto gTileB = make_layout(ProblemShape{}, LayoutRight{});
    auto sTile = make_layout(ProblemShape{}, LayoutRight{});
    auto swizzle_sTile = composition(Swizzle<3, 3, 3>{}, sTile);
    // using Atom1 = Copy_Atom<SM75_U32x1_LDSM_N, T>;
    // auto atom1_compatible = is_compatible<true, false, T, Atom1, decltype(frgthr), decltype(sTile)>();
    // printf("atom1_compatible: %s\n", atom1_compatible ? "true" : "false");

    auto cfg_global_A = make_gmem_FrgCopyCfg<T, decltype(gTileA), decltype(frgthr)>();
    auto cfg_shared = make_smem_FrgCopyCfg<T, decltype(swizzle_sTile), decltype(frgthr)>();
    auto cfg_global_B = make_gmem_FrgCopyCfg<T, decltype(gTileB), decltype(frgthr)>();
    auto gA = make_managed_tensor<T>(gTileA);
    auto gB = make_managed_tensor<T>(gTileB);
    for (int i=0; i<size(gA); i++) gA(i) = static_cast<T>(i);
    
    check_cfg(cfg_global_A, 
        AutoVectorizingCopyWithAssumedAlignment<16>{}, 
        AutoVectorizingCopyWithAssumedAlignment<16>{});
    check_cfg(cfg_shared, 
        Copy_Atom<SM75_U32x4_LDSM_N, T>{}, 
        AutoVectorizingCopyWithAssumedAlignment<32>{});
    check_cfg(cfg_global_B, 
        AutoVectorizingCopyWithAssumedAlignment<32>{},
        AutoVectorizingCopyWithAssumedAlignment<32>{});

    test_g2r2s2r2g_copy<T><<<1, cfg_global_A.thread_num>>>(cfg_global_A, cfg_shared, cfg_global_B, gA, sTile, gB);
    CHECK_CUDA();
    ASSERT_TRUE(check_tensors_match(gA, gB, 0., false));
}

}
} //