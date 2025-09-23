#pragma once
#include <gtest/gtest.h>
#include "reduce_utils.cuh"

namespace vidrial {
namespace {

TEST(make_ThreadReduceCfg, full_reduce) {
    auto XShape = Shape<_4, _4>{};
    auto XFrgThr = Layout<Shape<_4, _4>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_1{}, _4{}));
    auto correct_x_FrgThr =  Layout<Shape<_1, _4>, Stride<_0, _1>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}
TEST(make_ThreadReduceCfg, case0) {
    auto XShape = Shape<_4, _4>{};
    auto XFrgThr = Layout<Shape<_2, _8>, Stride<_1, _2>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_2{}, _4{}));
    auto correct_x_FrgThr =  Layout<Shape<_1, _8>, Stride<_0, _1>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}
TEST(make_ThreadReduceCfg, case1) {
    auto XShape = Shape<_4, _4>{};
    auto XFrgThr = Layout<Shape<Shape<_2, _2>, Shape<_2, _2>>,
                          Stride<Stride<_1, _4>, Stride<_2, _8>>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_2{}, _4{}));
    auto correct_x_FrgThr =  Layout<Shape<_2, Shape<_2, _2>>, Stride<_2, Stride<_1,_4>>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}
TEST(make_ThreadReduceCfg, case2) {
    auto XShape = Shape<_4, _4>{};
    auto XFrgThr = Layout<Shape<Shape<_2, _2>, Shape<_2, _2>>,
                          Stride<Stride<_2, _4>, Stride<_1, _8>>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_2{}, _4{}));
    auto correct_x_FrgThr =  Layout<Shape<_2, Shape<_2, _2>>, Stride<_2, Stride<_1,_4>>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}
TEST(make_ThreadReduceCfg, case3) {
    auto XShape = Shape<_8, _8>{};
    auto XFrgThr = Layout<Shape<Shape<_2, _2>, Shape<_4, _4>>,
                          Stride<Stride<_8, _4>, Stride<_16, _1>>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_4{}, _8{}));
    auto correct_x_FrgThr =  Layout<Shape<_2, Shape<_4, _4>>, Stride<_4, Stride<_8,_1>>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}
TEST(make_ThreadReduceCfg, case4) {
    auto XShape = Shape<Shape<_8,_4>, _32>{};
    auto XFrgThr = Layout<Shape<Shape<_4, _4, _2>, Shape<_4, _8>>,
                          Stride<Stride<_32, _1, _16>, Stride<_4, _128>>>{};
    auto cfg = make_ThreadReduceCfg<decltype(XShape), decltype(XFrgThr)>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_4{}, _32{}));
    auto correct_x_FrgThr =  Layout<Shape<_4, Shape<_4, _8>>, Stride<_4, Stride<_1,_16>>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
}


//--------  Warp Reduce Cfg tests --------

TEST(make_WarpReduceCfg, case0) {
    using XShape = Shape<_16, _8>;
    using XFrgThr = Layout<Shape<_2, Shape<_4,_16>>,
                           Stride<_16, Stride<_32, _1>>>;
    auto cfg = make_WarpReduceCfg<XShape, XFrgThr>();
    EXPECT_EQ(cfg.x_Shape, make_shape(_2{}, _8{}));
    auto correct_x_FrgThr = Layout<Shape<_2,Shape<_4,Shape<_8,_2>>>,
                                   Stride<_2,Stride<_4,Stride<_0,_1>>>>{};
    EXPECT_EQ(cfg.x_FrgThr, correct_x_FrgThr);
    auto correct_X_ReduceSteps = Layout<_8,_4>{};
    EXPECT_EQ(cfg.X_ReduceSteps, correct_X_ReduceSteps);
}

TEST(make_WarpReduceCfg, NoReduction) {
    using XShape = Shape<_1, Shape<_8>>;
    using XFrgThr = Layout<Shape<Shape<_2,_4>, _1>,
                           Stride<Stride<_1,_2>,_0>>;
    auto cfg = make_WarpReduceCfg<XShape, XFrgThr>();
    EXPECT_EQ(cfg.x_Shape, XShape{});
    EXPECT_EQ(cfg.x_FrgThr, XFrgThr{});
    auto correct_X_ReduceSteps = Layout<_1,_0>{};
    EXPECT_EQ(cfg.X_ReduceSteps, correct_X_ReduceSteps);
}


// warp_reduce tests
__global__ void test_warp_reduce(auto cfg, auto gX, auto gx) {
    using T = TensorType(gX);
    auto X_Frg = make_layout(get<0>(cfg.X_FrgThr.shape()));
    auto rX_frg = make_tensor<T>(X_Frg); // will become x_frg after reduction
    auto gX_frg = slice_rest(gX, cfg.X_FrgThr, threadIdx.x);
    copy(gX_frg, rX_frg);
    warp_reduce(cfg, SumCallable{}, rX_frg);
    auto gx_frg = slice_rest(gx, cfg.x_FrgThr, threadIdx.x);
    copy(rX_frg, gx_frg);
}

TEST(warp_reduce, case0) {
    using XShape = Shape<_16, _8>;
    using XFrgThr = Layout<Shape<_2, Shape<_4,_16>>,
                           Stride<_16, Stride<_32, _1>>>;
    auto cfg = make_WarpReduceCfg<XShape, XFrgThr>();
    auto gX = make_managed_tensor<int>(Layout<XShape>{});
    auto gx = make_managed_tensor<int>(make_layout(cfg.x_Shape));
    auto correct_gx = make_tensor<int>(cfg.x_Shape);
    fill(gX, 1);
    fill(correct_gx, 8);
    int thread_num = size<1>(XFrgThr{});
    test_warp_reduce<<<1, thread_num>>>(cfg, gX, gx);
    cudaDeviceSynchronize();
    ASSERT_TRUE(check_tensors_match(gx, correct_gx, 0, false));
}


// ------------ SmartReduceCfg tests ------------

void check_SmartReduceCfg(auto cfg, auto correct_cfg) {
    EXPECT_EQ(cfg.X.shape, correct_cfg.X.shape);
    EXPECT_EQ(cfg.X.frg_thr, correct_cfg.X.frg_thr);
    EXPECT_EQ(cfg.x.shape, correct_cfg.x.shape);
    EXPECT_EQ(cfg.x.frg_thr, correct_cfg.x.frg_thr);
    EXPECT_EQ(cfg.A.shape, correct_cfg.A.shape);
    EXPECT_EQ(cfg.skip_smem_reduce, correct_cfg.skip_smem_reduce);
}

TEST(SmartReduce, Case0) {
    struct CorrectValueCfg {
        struct X_t {
            Shape<_8, _4> shape;
            Layout<Shape<_1, _32>> frg_thr;
        } X;
        struct x_t {
            Shape<_4> shape;
            using FrgThr = Layout<Shape<_1,Shape<_8,_4>>,Stride<_0,Stride<_0,_1>>>;
            FrgThr frg_thr;
        } x;
        struct A_t {
            Shape<_1, _4> shape;
        } A;
        bool skip_smem_reduce = true;
    } correct_cfg;
    auto cfg = make_SmartReduceCfg(correct_cfg.X.shape, correct_cfg.X.frg_thr);
    check_SmartReduceCfg(cfg, correct_cfg);
}
TEST(SmartReduce, Case1) {
    struct CorrectValueCfg {
        struct X_t {
            Shape<_8, _8> shape;
            Layout<Shape<_2, _32>> frg_thr;
        } X;
        struct x_t {
            Shape<_8> shape;
            using FrgThr = Layout<Shape<_1,Shape<_4,_8>>,Stride<_0,Stride<_0,_1>>>;
            FrgThr frg_thr;
        } x;
        struct A_t {
            Shape<_1, _8> shape;
        } A;
        bool skip_smem_reduce = true;
    } correct_cfg;
    auto cfg = make_SmartReduceCfg(correct_cfg.X.shape, correct_cfg.X.frg_thr);
    check_SmartReduceCfg(cfg, correct_cfg);
}
TEST(SmartReduce, Case2) {
    struct CorrectValueCfg {
        struct X_t {
            Shape<_32, _32> shape;
            using FrgThr = Layout<Shape<Shape<_4,_4>, Shape<_8,_8>>,
                                  Stride<Stride<_1,_32>, Stride<_4,_128>>>;
            FrgThr frg_thr;
        } X;
        struct x_t {
            Shape<_32> shape;
            using FrgThr = Layout<Shape<_4,Shape<_8,_8>>,
                                  Stride<_1,Stride<_0,_4>>>;
            FrgThr frg_thr;
        } x;
        struct A_t {
            Shape<_1, _32> shape;
        } A;
        bool skip_smem_reduce = true;
    } correct_cfg;
    auto cfg = make_SmartReduceCfg(correct_cfg.X.shape, correct_cfg.X.frg_thr);
    check_SmartReduceCfg(cfg, correct_cfg);
}
TEST(SmartReduce, Case3) {
    struct CorrectValueCfg {
        struct X_t {
            Shape<_32, _32> shape;
            using FrgThr = Layout<Shape<Shape<_4,_4>, Shape<_8,_8>>,
                                  Stride<Stride<_1,_32>, Stride<_128,_4>>>;
            FrgThr frg_thr;
        } X;
        struct x_t {
            Shape<_32> shape;
            using FrgThr = Layout<Shape<_4,Shape<_8,_8>>,
                                  Stride<_1,Stride<_4,_0>>>;
            FrgThr frg_thr;
        } x;
        struct A_t {
            Shape<_2, _32> shape;
        } A;
        bool skip_smem_reduce = false;
    } correct_cfg;
    auto cfg = make_SmartReduceCfg(correct_cfg.X.shape, correct_cfg.X.frg_thr);
    check_SmartReduceCfg(cfg, correct_cfg);
}







} // namespace vidrial
} // namespace