#include <gtest/gtest.h>
#include <cuda_runtime.h>
#include "utilities.cuh"
#include "../kernels/mma/mma_cfg.cuh"
#include "../kernels/mma/kernel.cuh"
#include "../kernels/sympow_mma/sympow_mma_cfg.cuh"
#include "swizzle_cfg.cuh"
#include "ABC_utils.cuh"

namespace vidrial {
using namespace cute;

namespace {

TEST(SwizzleTest, case1) {
    using T = half_t;
    constexpr int power = 2;
    constexpr bool expand_K = false;
    constexpr int d_tile = 4;
    constexpr int d = 8;
    constexpr int D = sympow_dim<power, d, d_tile>();
    constexpr int M = D;
    constexpr int N = 256;
    constexpr int K = 256;
    constexpr int P = 13;
    constexpr int M_tile = static_pow<power>(d_tile);
    constexpr int N_tile = 16;
    constexpr int K_tile = 16;
    using MNKPSlabShape = Shape<Int<D>,Int<N>,Int<K>,Int<P>>; // M=256, N=256, K=256, P=13
    using MNKTileShape = Shape<Int<M_tile>,Int<N_tile>,Int<K_tile>>; // M_tile=64, N_tile=64, K_tile=16
    using GaSlab = Layout<Shape<Int<d>,Int<K>,Int<P>>>; // d, K, P
    using GBSlab = Layout<Shape<Int<N>,Int<K>,Int<P>>>; // N, K, P
    using GCSlab = Layout<Shape<Int<M>,Int<N>,Int<P>>>; // M, N, P
    using PerfCfg = PerfCfg<2, 1, true, 1>;
    using Atom = decltype(default_MMA_atom<T>());
    using MNKAtomPlacement = Shape<_1,_1,_1>;
    using SympowMMACfg_t = SympowMmaKernelCfg<T, power, Atom, MNKAtomPlacement, MNKPSlabShape, MNKTileShape, d, d_tile, expand_K, GaSlab, GBSlab, GCSlab, PerfCfg>;
    SympowMMACfg_t cfg;
    
    EXPECT_EQ((cfg.A.swizzle_cfg.swizzle), (Swizzle<Int<2>{}, Int<3>{}, Int<3>{}>{}));
    EXPECT_EQ((cfg.B.swizzle_cfg.swizzle), (Swizzle<Int<2>{}, Int<3>{}, Int<3>{}>{}));
}

TEST(SwizzleTest, case2) {
    using T = float;
    using Atom = decltype(default_MMA_atom<T>());
    using MNKAtomPlacement = Shape<_1,_1,_1>;
    using PerfCfg = vidrial::PerfCfg<2, 1, true, 1>;
    using Cfg = vidrial::SympowMmaKernelCfg<float, 2, Atom, MNKAtomPlacement, cute::tuple<cute::C<48>, cute::C<64>, cute::C<64>, cute::C<1>>, cute::tuple<cute::C<16>, cute::C<16>, cute::C<16>>, 8, 4, false, cute::Layout<cute::tuple<cute::C<8>, cute::C<64>, cute::C<1>>, cute::tuple<cute::_1, cute::C<8>, cute::C<0>>>, cute::Layout<cute::tuple<cute::C<64>, cute::C<64>, cute::_1>, cute::tuple<cute::_1, cute::_64, cute::_0>>, cute::Layout<cute::tuple<cute::C<48>, cute::C<64>, cute::_1>, cute::tuple<cute::_1, cute::C<48>, cute::C<0>>>, PerfCfg>;
    Cfg cfg;
    EXPECT_EQ((cfg.A.swizzle_cfg.swizzle), (Swizzle<Int<3>{}, Int<2>{}, Int<3>{}>{}));
    EXPECT_EQ((cfg.B.swizzle_cfg.swizzle), (Swizzle<Int<3>{}, Int<2>{}, Int<3>{}>{}));
}


TEST(SwizzleTest, case3) {
    using G2SCfg_ = vidrial::TileCopyCfg<cutlass::bfloat16_t, 32, cute::tuple<cute::C<16L>, cute::C<16L>>, cute::Layout<cute::tuple<cute::C<16L>, cute::C<16L>>, cute::tuple<cute::C<1L>, cute::C<64L>>>, cute::Layout<cute::tuple<cute::C<16L>, cute::C<16L>>, cute::tuple<cute::C<1>, cute::C<16L>>>>;

    using STile_=cute::Layout<cute::tuple<cute::C<16L>, cute::C<16L>>, cute::tuple<cute::C<1>, cute::C<16L>>>;
    
    using FrgThr_=cute::Layout<cute::tuple<cute::tuple<cute::_2, cute::C<2L>, cute::C<2L>>, cute::tuple<cute::_4, cute::C<8>, cute::tuple<cute::_1, cute::_1, cute::_1>>>, cute::tuple<cute::tuple<cute::C<16L>, cute::C<8>, cute::C<128L>>, cute::tuple<cute::C<32L>, cute::_1, cute::tuple<cute::C<0>, cute::C<0>, cute::C<0>>>>>;    
    constexpr int swizzle_mode=0;

    using Cfg = vidrial::SwizzleCfg<G2SCfg_, STile_, FrgThr_, swizzle_mode>;
    Cfg cfg;
    EXPECT_EQ((cfg.swizzle), (Swizzle<Int<2>{}, Int<3>{}, Int<3>{}>{}));
    
}

TEST(SwizzleTest, case4) {
    using T = cutlass::half_t;
    using ABC_t = A_t;
    using MmaAtom = cute::MMA_Atom<cute::SM80_16x8x8_F32F16F16F32_TN>;
    using MNKTileShape = cute::tuple<cute::_16, cute::_16, cute::_16>;
    using MNKAtomPlacement = cute::tuple<cute::_1, cute::_2, cute::C<1>>;
    using GSlab = cute::Layout<cute::tuple<cute::_16, cute::_16, cute::_1>, cute::tuple<cute::_1, cute::_16, cute::C<0>>>;
    using PerfCfg = vidrial::PerfCfg<2, 1, true, 1>;
    using Cfg = vidrial::ABC_MmaCfg<T, ABC_t, MmaAtom, MNKTileShape, MNKAtomPlacement, GSlab, PerfCfg>;
    Cfg cfg;
    EXPECT_EQ((cfg.swizzle_cfg.swizzle), (Swizzle<Int<2>{}, Int<3>{}, Int<3>{}>{}));
}

TEST(SwizzleTest, new_api_1) {
    using T = cutlass::half_t;
    using STile = decltype(make_layout(Shape<_64, _64>{}, LayoutRight{}));
    using WriteFrgThr = decltype(make_layout(Shape<Shape<_8, _8>, Shape<_8, _8>>{}, Stride<Stride<_64, _8>, Stride<_512, _1>>{}));
    using ReadFrgThr = decltype(make_layout(Shape<Shape<Shape<_2, _2>, Shape<_2, _8>>, Shape<Shape<_4, _8>, _2>>{}, Stride<Stride<Stride<_64, _8>, Stride<_32, _512>>, Stride<Stride<_128, _1>, _16>>{}));
    using WriteAtom = Copy_Atom<SM80_CP_ASYNC_CACHEGLOBAL<uint128_t>, T>;
    constexpr auto swizzle = make_swizzle_g2s2r<T, STile, WriteFrgThr, ReadFrgThr, WriteAtom>();
    EXPECT_EQ((swizzle), (Swizzle<Int<3>{}, Int<3>{}, Int<3>{}>{}));
}

}
}// namespace vidrial