#include <gtest/gtest.h>
#include <cuda_runtime.h>
#include "utilities.cuh"
#include "frgthr_tiling.cuh"

using namespace cute;

namespace vidrial {
namespace {

__global__ void test_store_tile_kernel(auto cfg, auto gA, auto gB, int tile_idx) {
    using T = TensorType(gA);
    auto rA_frg = make_tensor<T>(make_layout(get<0>(cfg.FrTh.shape())));
    copy(slice_rest(gA, cfg.FrTh, threadIdx.x), rA_frg);
    FrgThr_store_tile(cfg, rA_frg, gB, tile_idx);
}

void test_FrgThrTiling_store_tile(auto A_Layout, auto B_Shape, auto A_TileRest, auto A_FrgThr) {
    auto cfg = make_FrgThrTilingCfg(A_TileRest, A_FrgThr);
    auto A = make_managed_tensor<int>(A_Layout);
    for (int i=0; i<size(A); i++) A(i) = (i*83)%47;
    auto B = make_managed_tensor<int>(make_layout(B_Shape));
    int thread_num = size<1>(A_FrgThr);
    for (int tile_idx=0; tile_idx<size<1>(A_TileRest); tile_idx++) {
        test_store_tile_kernel<<<1, thread_num>>>(cfg, A, B, tile_idx);
        CHECK_CUDA();
        auto A_tile = slice_rest(A, A_TileRest, tile_idx);
        ASSERT_TRUE(check_tensors_match(A_tile, B, 0., false));
        clear(B);
    }
}

void test_8x8_battery(auto A_Layout) {
    auto B_Shape = Shape<_4, _4>{};
    auto A_TileRest = zipped_divide(A_Layout, B_Shape);
 
   {
    auto A_FrgThr = Layout<Shape<_2, Shape<_4,_8>>,
                           Stride<_8, Stride<_16, _1>>>{}; 

    test_FrgThrTiling_store_tile(A_Layout, B_Shape, A_TileRest, A_FrgThr);
    }
    {
    auto A_FrgThr = Layout<Shape<_2, Shape<_4,_8>>,
                           Stride<_4, Stride<_1, _8>>>{}; 
    test_FrgThrTiling_store_tile(A_Layout, B_Shape, A_TileRest, A_FrgThr);
    }
    {
    auto A_FrgThr = Layout<Shape<Shape<_2,_2>, Shape<_4,_4>>,
                           Stride<Stride<_8,_4>, Stride<_1, _16>>>{}; 
    test_FrgThrTiling_store_tile(A_Layout, B_Shape, A_TileRest, A_FrgThr);
    }
    {
    auto A_FrgThr = Layout<Shape<_8, _8>,
                           Stride<_1, _8>>{}; 
    test_FrgThrTiling_store_tile(A_Layout, B_Shape, A_TileRest, A_FrgThr);
    }
    {
    auto A_FrgThr = Layout<Shape<_8, _8>,
                           Stride<_8, _1>>{}; 
    test_FrgThrTiling_store_tile(A_Layout, B_Shape, A_TileRest, A_FrgThr);
    }
}

TEST(FrgThrTilingTest, A8x8_colmaj_B4x4_various_FrgThr) {
    auto A_Layout = Layout<Shape<_8, _8>>{};
    test_8x8_battery(A_Layout);
}

TEST(FrgThrTilingTest, A8x8_rowmaj_B4x4_various_FrgThr) {
    auto A_Layout = Layout<Shape<_8, _8>,
                           Stride<_8, _1>>{};
    test_8x8_battery(A_Layout);
}

TEST(FrgThrTilingTest, A8x8_nested_B4x4_various_FrgThr) {
    auto A_Layout = Layout<Shape<Shape<_2,_4>, _8>,
                           Stride<Stride<_8,_16>, _1>>{};
    test_8x8_battery(A_Layout);
}

}

}