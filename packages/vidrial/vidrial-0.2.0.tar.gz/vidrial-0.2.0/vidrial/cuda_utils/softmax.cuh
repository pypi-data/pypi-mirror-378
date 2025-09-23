#pragma once
#include <iostream>
#include "frg_copy.cuh"
#include "../kernels/reduce/reduce_utils.cuh"

namespace vidrial {
using namespace cute;

template<typename T>
struct SumOp {
    CUTE_DEVICE auto operator()(T a, T b) const {return a + b;}
};

template<typename T>
struct MaxOp {
    CUTE_DEVICE auto operator()(T a, T b) const {return a > b ? a : b;}
};

template<>
struct MaxOp<float> {
    CUTE_DEVICE auto operator()(float a, float b) const {return max(a, b);}
};

template<typename T>
struct MulOp {
    CUTE_DEVICE auto operator()(T a, T b) const {return a * b;}
};

template<typename T>
struct DivOp {
    CUTE_DEVICE auto operator()(T a, T b) const {return a / b;}
};

template<>
struct DivOp<float> {
    CUTE_DEVICE auto operator()(float a, float b) const {return __fdividef(a, b);}
};

template<bool log2, typename T>
struct ExpDiffOp {
    CUTE_DEVICE auto operator()(T a, T b) const {
        if constexpr (log2)
            return static_cast<T>(exp2f(b - a));
        else
            return static_cast<T>(__expf(b - a));
    }
};

template<bool log2, typename T>
struct ExpFmaDiffOp {
    float scale;

    CUTE_HOST_DEVICE ExpFmaDiffOp(float scale) : scale(scale) {}

    CUTE_DEVICE auto operator()(T a, T b) const {
        if constexpr (log2)
            return static_cast<T>(exp2f(a * scale - b));
        else
            return static_cast<T>(__expf(a * scale - b));
    }
};

/**
 * @brief Configurations for performing stable softmax on a tensor, possibly made up with multiple tiles.
 * @tparam T                   The data type of the tensor
 * @tparam TileShape           The shape of the tile [row, col]
 * @tparam FrgThr              The frgthr of the tile
 * @tparam ReduceCfg           The reduce configuration
 * @tparam Frg2rFrg            The frg to rowmax layout, useful for broadcasting the rowmax to the tensor
 * @tparam OFrg2rFrg           The Ofrg to rowsum layout
 * @tparam log2                Whether to use log2 for the softmax
 */
template<typename T_, typename TileShape_, typename FrgThr_, typename ReduceCfg_, typename Frg2rFrg_, typename OFrg2rFrg_, bool log2_=false>
struct SoftmaxCfg {
    using T = T_;
    using TileShape = TileShape_;
    using FrgThr = FrgThr_;
    using ReduceCfg = ReduceCfg_;
    using Frg2rFrg = Frg2rFrg_;
    using OFrg2rFrg = OFrg2rFrg_;
    static constexpr T_ LOG2E = static_cast<T_>(1.44269504089f);
    static constexpr bool log2 = log2_;

    TileShape tile_shape;
    FrgThr frgthr;
    ReduceCfg reduce;
    Frg2rFrg frg2rfrg;
    OFrg2rFrg ofrg2rfrg;
};

/**
 * @brief Make the softmax configuration
 * @tparam T          The data type of the tensor
 * @tparam TileShape  The shape of the softmax tile [row, col]
 * @tparam FrgThr     The frgthr of the softmax tile
 * @tparam OTileShape The shape of the output tile [row, col]
 * @tparam OFrgThr    The frgthr of the output tile
 * @tparam log2       Whether to use log2 for the softmax
 */
template<typename T, typename TileShape, typename FrgThr, typename OTileShape, typename OFrgThr, bool log2=false>
CUTE_HOST_DEVICE auto make_SoftmaxCfg() {
    CUTE_STATIC_ASSERT(rank(TileShape{}) == 2, "TileShape must be 2D");
    constexpr auto tile = make_layout(TileShape{});
    // reduce cfg
    constexpr auto reduce_tile = select<1, 0>(tile); // [reduce, batch] or [col, row]
    constexpr auto reduce_frgthr = left_inverse(reduce_tile).compose(tile).compose(FrgThr{});
    using reduce_cfg_t = decltype(make_SmartReduceCfg<false>(decltype(reduce_tile.shape()){}, decltype(reduce_frgthr){}));
    constexpr auto reduce = reduce_cfg_t{};
    // frg to rowmax
    constexpr auto rfrg = get<0>(reduce.x.frg_thr);
    constexpr auto Frg = get<0>(reduce_frgthr);
    constexpr auto Frg2rfrg = left_inverse(rfrg).compose(reduce.X_2_x).compose(Frg);
    // Ofrg to rowsum, we rely on the fact that the rfrg for reducing attention tile and output tile are the same shape
    constexpr auto otile = make_layout(OTileShape{});
    constexpr auto reduce_otile = select<1, 0>(otile); // [reduce, batch] or [col, row]
    constexpr auto reduce_ofrgthr = left_inverse(reduce_otile).compose(otile).compose(OFrgThr{});
    using oreduce_cfg_t = decltype(make_SmartReduceCfg<false>(decltype(reduce_otile.shape()){}, decltype(reduce_ofrgthr){}));
    constexpr auto oreduce = oreduce_cfg_t{};
    constexpr auto ofrg = get<0>(oreduce.x.frg_thr);
    constexpr auto OFrg = get<0>(reduce_ofrgthr);
    constexpr auto OFrg2rfrg = left_inverse(ofrg).compose(oreduce.X_2_x).compose(OFrg);

    return SoftmaxCfg<T, TileShape, FrgThr, reduce_cfg_t, decltype(Frg2rfrg), decltype(OFrg2rfrg), log2>{};
}


/**
 * @brief Perform softmax on a tensor, without rescaling/considering other tiles in the tensor
 * @param cfg   The configuration
 * @param frg   The tensor to perform softmax on
 * @param sRow  The shared memory tile for reduction (in some cases useful)
 * @param rowmax_frg The rowmax of the tensor so far: [rows]
 * @param rowsum_frg The rowsum of the tensor so far: [reduce, rows]
 * @param softmax_scale The scale factor for the softmax
 */
CUTE_DEVICE void softmax(auto const& cfg, auto& frg, auto& sRow, auto& rowmax_frg, auto& rowsum_frg, float softmax_scale) {
    using T = TensorType(frg);
    smart_reduce(cfg.reduce, frg, rowmax_frg, sRow, MaxOp<T>{});
    tensor_scalar_prod(rowmax_frg, softmax_scale);
    elementwise_tensor(ExpFmaDiffOp<cfg.log2, T>{softmax_scale}, frg, rowmax_frg.compose(cfg.frg2rfrg));
    thread_reduce(cfg.reduce.thread_reduce, SumOp<T>{}, frg, rowsum_frg);
}

/**
 * @brief Perform softmax on a tensor while rescaling the output from the previous iteration
 * @param cfg   The configuration
 * @param frg   The tensor to perform softmax on
 * @param sRow  The shared memory tile for reduction (in some cases useful)
 * @param rO_frg The tensor to perform rescaling on, shares the same shape as frg
 * @param rowmax_frg The rowmax of the tensor so far: [rows]
 * @param rowsum_frg The rowsum of the tensor so far: [reduce, rows]
 * @param softmax_scale The scale factor for the softmax
 */
CUTE_DEVICE void softmax_rescale(auto const& cfg, auto& frg, auto& rO_frg, auto& sRow, auto& rowmax_frg, auto& rowsum_frg, float softmax_scale) {
    using T = TensorType(frg);
    auto current_rowmax_frg = smart_reduce(cfg.reduce, frg, sRow, MaxOp<T>{});
    auto rescaler_frg = current_rowmax_frg.compose(cfg.frg2rfrg);
    tensor_scalar_prod(current_rowmax_frg, softmax_scale);
    dual_elementwise_tensor(MaxOp<T>{}, ExpDiffOp<cfg.log2, T>{}, rowmax_frg, current_rowmax_frg); // compute rescaler
    elementwise_tensor(ExpFmaDiffOp<cfg.log2, T>{softmax_scale}, frg, rowmax_frg.compose(cfg.frg2rfrg));
    elementwise_tensor(MulOp<T>{}, rO_frg, rescaler_frg); // rescale outout
    elementwise_tensor(MulOp<T>{}, rowsum_frg, current_rowmax_frg); // rescale rowsum
    thread_reduce(cfg.reduce.thread_reduce, SumOp<T>{}, frg, rowsum_frg);
}

/**
 * @brief Finish reducing the rowsum and discount the tensor by the rowsum
 * @param cfg         The configuration
 * @param rO_frg      The output fragments so far
 * @param rowsum_frg  The rowsum fragments so far
 * @param sRow        The shared memory tile for reduction (in some cases useful)
 */
CUTE_DEVICE void softmax_epilogue(auto const& cfg, auto& rO_frg, auto& rowsum_frg, auto& sRow) {
    using T = TensorType(rowsum_frg);
    smart_reduce_cta(cfg.reduce, rowsum_frg, sRow, SumOp<T>{});
    elementwise_tensor(DivOp<T>{}, rO_frg, rowsum_frg.compose(cfg.ofrg2rfrg));
}

template<typename T_, typename TileShape_, typename FrgThr_, typename ReduceCfg_, typename Frg2rFrg_, typename OFrg2rFrg_, bool log2_>
void print_cfg(SoftmaxCfg<T_, TileShape_, FrgThr_, ReduceCfg_, Frg2rFrg_, OFrg2rFrg_, log2_> const& cfg, std::string prefix = "") {
    std::cout << "SoftmaxCfg:\n";
    std::cout << prefix << "  tile_shape: "; print(cfg.tile_shape); std::cout << "\n";
    std::cout << prefix << "  frgthr: "; print(cfg.frgthr); std::cout << "\n";
    std::cout << prefix << "  reduce: "; print_cfg(cfg.reduce, prefix + "  reduce: "); std::cout << "\n";
    std::cout << prefix << "  frg2rfrg: "; print(cfg.frg2rfrg); std::cout << "\n";
    std::cout << prefix << "  ofrg2rfrg: "; print(cfg.ofrg2rfrg); std::cout << "\n";
}
}