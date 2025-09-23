#include <gtest/gtest.h>
#include "sympow_bwd.cuh"
#include "kernels/sympow_bwd/kernel.cuh"

namespace vidrial {
namespace {

template<typename T, int p, typename XSlabShape, typename Params, bool duplicate_correction = true>
void test_sympow_bwd(XSlabShape X_slab_shape, Params params) {
    using XTileShape = typename Params::XTileShape;
    using ZTileLayout = typename Params::ZTileLayout;
    using ZFrgShape = typename Params::ZFrgShape;
    using ZFrgThr = typename Params::ZFrgThr;
    static constexpr int d_blk = get<0>(XTileShape{});
    auto Z_slab_shape = sympow_shape<p, d_blk>(X_slab_shape);
    using XSlab = Layout<XSlabShape>;
    using ZSlab = Layout<decltype(Z_slab_shape)>;
    constexpr int reduce_buffer_size = 256;
    auto cfg = make_sympow_bwd_cfg<T, p>(ZFrgShape{}, XTileShape{}, ZSlab{}, XSlab{}, ZTileLayout{});
    auto gX = make_managed_tensor<T>(XSlab{});
    auto gZ_grad = make_managed_tensor<T>(ZSlab{});
    auto gX_delta = make_managed_tensor<T>(XSlab{});
    randomize_tensor(gX);
    randomize_tensor(gZ_grad);
    randomize_tensor(gX_delta);
    auto gXgrad = make_managed_tensor<T>(XSlab{});
    int blocks = cfg.fwd.b_tile_num;
    tiled_sympow_bwd_kernel<duplicate_correction><<<blocks, cfg.fwd.thread_num>>>(cfg, gX.data(), gZ_grad.data(), gXgrad.data());
    CHECK_CUDA();
}

TEST(SympowCfg, SimpleP2) {
    constexpr int p = 2;
    struct Params {
        using XTileShape = Shape<_4,_2>;
        using ZTileLayout = Layout<decltype(tpow_shape<p>(XTileShape{}))>;
        using ZFrgShape = Shape<Shape<_2, _2>, _1>;
        using ZFrgThr = decltype(zipped_divide(ZTileLayout{}, ZFrgShape{}));
    };
    test_sympow_bwd<float, 2>(make_shape(_4{},_2{}), Params{});
}
TEST(SympowCfg, SimpleP2_) {
    constexpr int p = 2;
    struct Params {
        using XTileShape = Shape<_8,_8>;
        using ZTileLayout = Layout<decltype(tpow_shape<p>(XTileShape{}))>;
        using ZFrgShape = Shape<Shape<_4, _4>, _1>;
        using ZFrgThr = decltype(zipped_divide(ZTileLayout{}, ZFrgShape{}));
    };
    test_sympow_bwd<float, 2>(make_shape(_16{},_16{}), Params{});
}
TEST(SympowCfg, SimpleP3) {
    constexpr int p = 3;
    struct Params {
        using XTileShape = Shape<_8,_8>;
        using ZTileLayout = Layout<decltype(tpow_shape<p>(XTileShape{}))>;
        using ZFrgShape = Shape<Shape<_4, _4, _2>, _1>;
        using ZFrgThr = decltype(zipped_divide(ZTileLayout{}, ZFrgShape{}));
    };
    test_sympow_bwd<float, p>(make_shape(_16{},_16{}), Params{});
}
TEST(SympowCfg, SimpleP4) {
    constexpr int p = 4;
    struct Params {
        using XTileShape = Shape<_4,_8>;
        using ZTileLayout = Layout<decltype(tpow_shape<p>(XTileShape{}))>;
        using ZFrgShape = Shape<Shape<_4, _4, _2, _1>, _1>;
        using ZFrgThr = decltype(zipped_divide(ZTileLayout{}, ZFrgShape{}));
    };
    test_sympow_bwd<float, p>(make_shape(_16{},_16{}), Params{});
}


}
}