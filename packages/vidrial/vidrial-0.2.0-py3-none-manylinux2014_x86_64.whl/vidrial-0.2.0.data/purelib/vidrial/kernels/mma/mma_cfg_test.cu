#include <gtest/gtest.h>
#include <cuda_runtime.h>
#include "mma_cfg.cuh"
#include "mma/kernel.cuh"
#include "ABC_utils.cuh"
#include "perf_cfg.cuh"

using namespace cute;

namespace vidrial {
namespace {

TEST(MmaCfgTest, SimpleFmaMmaTest) {
    using Atom = MMA_Atom<UniversalFMA<half_t, half_t, half_t, half_t>>;
    using MNKPTestShape = Shape<_1,_8,_16,_1>;
    using MNKTileShape = Shape<_1,_8,_1>;
    using MNKAtomPlacement = Shape<_1,_4,_1>;
    auto AShape = ABC_get_MNKP(A_t{}, MNKPTestShape{});
    auto BShape = ABC_get_MNKP(B_t{}, MNKPTestShape{});
    auto CShape = ABC_get_MNKP(C_t{}, MNKPTestShape{});
    auto gA = make_managed_tensor<half_t>(make_layout(AShape));
    auto gB = make_managed_tensor<half_t>(make_layout(BShape));
    auto gC = make_managed_tensor<half_t>(make_layout(CShape));
    for (int i = 0; i < size(gA); ++i) gA(i) = static_cast<half_t>(i%14/14.);
    for (int i = 0; i < size(gB); ++i) gB(i) = static_cast<half_t>(i%27/27.);
    auto cfg = MmaKernelCfg<half_t, Atom, MNKTileShape, MNKAtomPlacement, decltype(gA.layout()), decltype(gB.layout()), decltype(gC.layout()), DefaultPerfCfg>{};
    launch_tiled_mma_kernel(cfg, gA.data(), gB.data(), gC.data());
    cudaDeviceSynchronize(); cudaError_t error = cudaGetLastError();
    if (error != cudaSuccess) { std::cerr << "CUDA error: " << cudaGetErrorString(error) << std::endl; }
    auto gC_ref = make_managed_tensor<half_t>(gC.layout());
    clear(gC_ref);
    for (int p=0; p<int(get<3>(MNKPTestShape{})); ++p)
        gemm(gA(_,_,p), gB(_,_,p), gC_ref(_,_,p));
    bool match = check_tensors_match(gC, gC_ref, 1e-1, false);
    EXPECT_TRUE(match);
}

TEST(MmaCfgTest, SimpleMmaTest) {
    using MNKPTestShape = Shape<_64,_64,_128,_1>;
    using MNKTileShape = Shape<_32,_32,_16>;
    auto atom = default_MMA_atom<half_t>();
    using MNKAtomPlacement = Shape<_2,_2,_1>;
    auto AShape = ABC_get_MNKP(A_t{}, MNKPTestShape{});
    auto BShape = ABC_get_MNKP(B_t{}, MNKPTestShape{});
    auto CShape = ABC_get_MNKP(C_t{}, MNKPTestShape{});
    auto gA = make_managed_tensor<half_t>(make_layout(AShape));
    auto gB = make_managed_tensor<half_t>(make_layout(BShape));
    auto gC = make_managed_tensor<half_t>(make_layout(CShape));
    for (int i = 0; i < size(gA); ++i) gA(i) = static_cast<half_t>(i%14/14.);
    for (int i = 0; i < size(gB); ++i) gB(i) = static_cast<half_t>(i%27/27.);
    auto cfg = make_mma_cfg<half_t>(MNKTileShape{}, atom, MNKAtomPlacement{}, gA.layout(), gB.layout(), gC.layout());
    launch_tiled_mma_kernel(cfg, gA.data(), gB.data(), gC.data());
    cudaDeviceSynchronize(); cudaError_t error = cudaGetLastError();
    if (error != cudaSuccess) { std::cerr << "CUDA error: " << cudaGetErrorString(error) << std::endl; }
    auto gC_ref = make_managed_tensor<half_t>(gC.layout());
    clear(gC_ref);
    for (int p=0; p<int(get<3>(MNKPTestShape{})); ++p)
        gemm(gA(_,_,p), gB(_,_,p), gC_ref(_,_,p));
    bool match = check_tensors_match(gC, gC_ref, 1e-1, false);
    EXPECT_TRUE(match);
}

template<bool AColMaj, bool BColMaj, bool CColMaj, typename MNKTileShape, typename MNKAtomPlacement, typename T>
void test_mma_kernel(auto AShape, auto BShape, auto CShape, T* A_ptr, T* B_ptr, T* C_ptr) {
    // If the ABC matrices are row major we don't want the P (batch) dimension to go first
    auto ARowMaj = select<1,0,2>(make_layout(select<1,0,2>(AShape)));
    auto BRowMaj = select<1,0,2>(make_layout(select<1,0,2>(BShape)));
    auto CRowMaj = select<1,0,2>(make_layout(select<1,0,2>(CShape)));
    auto A = std::conditional_t<AColMaj, Layout<decltype(AShape)>, decltype(ARowMaj)>{};
    auto B = std::conditional_t<BColMaj, Layout<decltype(BShape)>, decltype(BRowMaj)>{};
    auto C = std::conditional_t<CColMaj, Layout<decltype(CShape)>, decltype(CRowMaj)>{};
    auto atom = default_MMA_atom<T>();
    auto cfg = make_mma_cfg<T>(MNKTileShape{}, atom, MNKAtomPlacement{}, A, B, C);
    launch_tiled_mma_kernel(cfg, A_ptr, B_ptr, C_ptr);
    cudaDeviceSynchronize(); cudaError_t error = cudaGetLastError();
    if (error != cudaSuccess) { std::cerr << "CUDA error: " << cudaGetErrorString(error) << std::endl; }
    auto gA = make_tensor(A_ptr, cfg.A.gSlab);
    auto gB = make_tensor(B_ptr, cfg.B.gSlab);
    auto gC = make_tensor(C_ptr, cfg.C.gSlab);
    default_sTile(select<0,1>(cfg.C.gSlab), cfg.C.sTile.shape());
    EXPECT_EQ(error, cudaSuccess);
    auto gC_ref = make_managed_tensor<half_t>(gC.layout());
    clear(gC_ref);
    for (int p=0; p<cfg.P; ++p)
        gemm(gA(_,_,p), gB(_,_,p), gC_ref(_,_,p));
    bool match = check_tensors_match(gC, gC_ref, 1e-1, false);
    EXPECT_TRUE(match);
}
template<typename MNKPTestShape, typename MNKTileShape, typename MNKAtomPlacement>
void test_default_mma_kernel_all_rowcol_combinations() {
    auto AShape = ABC_get_MNKP(A_t{}, MNKPTestShape{});
    auto BShape = ABC_get_MNKP(B_t{}, MNKPTestShape{});
    auto CShape = ABC_get_MNKP(C_t{}, MNKPTestShape{});
    auto _gA = make_managed_tensor<half_t>(make_layout(AShape));
    auto _gB = make_managed_tensor<half_t>(make_layout(BShape));
    auto _gC = make_managed_tensor<half_t>(make_layout(CShape));
    for (int i = 0; i < size(_gA); ++i) _gA(i) = static_cast<half_t>(i%14/14.);
    for (int i = 0; i < size(_gB); ++i) _gB(i) = static_cast<half_t>(i%27/27.);
    auto A_ptr = _gA.data();
    auto B_ptr = _gB.data();
    auto C_ptr = _gC.data();
    // only try some combinations to speed up the test
    test_mma_kernel<1,1,1, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    // test_mma_kernel<1,1,0, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    test_mma_kernel<1,0,1, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    // test_mma_kernel<1,0,0, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    // test_mma_kernel<0,1,1, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    // test_mma_kernel<0,1,0, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    test_mma_kernel<0,0,1, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
    test_mma_kernel<0,0,0, MNKTileShape, MNKAtomPlacement>(AShape, BShape, CShape, A_ptr, B_ptr, C_ptr);
}
TEST(MmaCfgTest, mma_kernel_Shape16x16x16_Tile16x16x16_AtomPlacement1x1x1) {
    using MNKPTestShape = Shape<_16,_16,_16,_1>;
    using MNKTileShape = Shape<_16,_16,_16>;
    using MNKAtomPlacement = Shape<_1,_1,_1>;
    test_default_mma_kernel_all_rowcol_combinations<MNKPTestShape, MNKTileShape, MNKAtomPlacement>();
}
TEST(MmaCfgTest, mma_kernel_Shape16x16x16_Tile16x16x16_AtomPlacement1x2x1) {
    using MNKPTestShape = Shape<_16,_16,_16,_1>;
    using MNKTileShape = Shape<_16,_16,_16>;
    using MNKAtomPlacement = Shape<_1,_2,_1>;
    test_default_mma_kernel_all_rowcol_combinations<MNKPTestShape, MNKTileShape, MNKAtomPlacement>();
}
TEST(MmaCfgTest, mma_kernel_Shape64x128x64_Tile16x8x16) {
    using MNKPTestShape = Shape<_64,_128,_64,_4>;
    using MNKTileShape = Shape<_64,_64,_16>;
    using MNKAtomPlacement = Shape<_2,_4,_1>;
    test_default_mma_kernel_all_rowcol_combinations<MNKPTestShape, MNKTileShape, MNKAtomPlacement>();
}
TEST(MmaCfgTest, mma_kernel_Shape64x128x64_Tile32x32x32) {
    using MNKPTestShape = Shape<_64,_128,_64,_2>;
    using MNKTileShape = Shape<_32,_32,_32>;
    using MNKAtomPlacement = Shape<_2,_2,_1>;
    test_default_mma_kernel_all_rowcol_combinations<MNKPTestShape, MNKTileShape, MNKAtomPlacement>();
}
} // namespace
} // namespace vidrial 