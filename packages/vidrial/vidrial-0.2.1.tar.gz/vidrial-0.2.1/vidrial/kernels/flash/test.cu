#include <gtest/gtest.h>
#include "cuda_utils/utilities.cuh"
#include "cuda_utils/softmax.cuh"
#include "reduce/reduce_utils.cuh"

namespace vidrial {
namespace {
using namespace cute;

TEST(SoftmaxTest, Test2) {
    using T = float;
    using TileShape = Shape<_16, _32>; // [row, col]
    using FrgThr = Layout<
        Shape<
            Shape<Shape<_2, _2>, _1, _4>,
            Shape<_4, _8, Shape<_1, _1, _1>>
            >, 
        Stride<
            Stride<Stride<_16, _8>, _0, _128>,
            Stride<_32, _1, Stride<_0, _0, _0>>
        >
    >; // (((_2,_2),_1,_4),(_4,_8,(_1,_1,_1))):(((_1,_256),_0,_8),(_2,_32,(_0,_0,_0)))
    auto cfg = make_SoftmaxCfg<T, TileShape, FrgThr, static_cast<T>(1.0), false, false>();
    print("cfg.frg2mfrg = "); print(cfg.frg2mfrg); print("\n");
}

}
}