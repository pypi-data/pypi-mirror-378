#pragma once
#include "cuda_utils/tprod.cuh"
#include "../reduce/reduce_utils.cuh"

namespace vidrial {

// The bwd process of sympow involves objects of the following shapes:
// Y_grad: [[d_tile, ...], b_tile]
// X_i: [[d_tile], b_tile]
// X_i_grad: [[d_tile], b_tile]
// Y_grad_for_i: [[d_tile, ...], b_tile]
// Y_grad_for_i_warp_reduced: [warp_reduce([d_tile, ...]), b_tile]
//
// The following steps are performed for each factor i:
// i. Y_grad_for_i = Y_grad * \prod_{j \neq i} X_j
// ii. Y_grad_for_i_warp_reduced = warp_reduce(Y_grad_for_i)
// iii. X_i_grad = CTA_reduce(Y_grad_for_i_warp_reduced)

template <int dim, auto... Is, typename YTensor, typename XTensors>
CUTE_HOST_DEVICE void tprod_bcast_multiply_all_except(index_sequence<Is...>, YTensor& Y, const XTensors& Xs) {
    (..., [&]() {
        if constexpr (Is != dim)
            tprod_bcast_multiply<Is>(Y, get<Is>(Xs));
    }());
}

template <int dim, typename YTensor, typename XTensors>
CUTE_HOST_DEVICE void tprod_bcast_multiply_all_except(YTensor& Y, const XTensors& Xs) {
    constexpr int rnk = rank(decltype(Xs){});
    tprod_bcast_multiply_all_except<dim>(make_index_sequence<rnk>{}, Y, Xs);
}


template<typename _T, int _dim, typename _YShape, typename YFrgThr>
struct TprodBwdCfg {
    using T = _T;
    using YShape = _YShape;
    static constexpr int dim = _dim;
    // RY: [reduce_dims, [dim, batch]]
    using RYShape = decltype(make_shape(drop<dim>(get<0>(YShape{})),
                                        make_shape(get<0,dim>(YShape{}), get<1>(YShape{}))));
    using RYLayout = Layout<RYShape>;
    using Y2RY_t = decltype(make_layout(layout_insert<dim>(get<0>(RYLayout{}), get<1,0>(RYLayout{})),
                                      get<1,1>(RYLayout{})));
    using RY2Y_t = decltype(left_inverse(Y2RY_t{}).compose(RYLayout{}));
    using RYFrgThr = decltype(Y2RY_t{}.compose(YFrgThr{}));
    using RYFrg2YFrg_t = decltype(left_inverse(get<0>(YFrgThr{})).compose(RY2Y_t{}).compose(get<0>(RYFrgThr{})));
    using SmartReduce = decltype(make_SmartReduceCfg(RYShape{}, RYFrgThr{}));
    using XFrgThr = decltype(typename SmartReduce::x_t{}.frg_thr);
    using XFrgShape = decltype(typename SmartReduce::x_t{}.frg_shape);
    YShape Y_Shape;
    RYShape RY_Shape;
    SmartReduce smart_reduce;
    Y2RY_t Y2RY;
    RY2Y_t RY2Y;
    RYFrg2YFrg_t RYFrg2YFrg;
    YFrgThr Y_FrgThr;
    XFrgThr X_FrgThr;
    XFrgShape X_FrgShape;
    CUTE_DEVICE bool owns_frg() { return smart_reduce.owns_frg(); }
};

__device__ void tprod_bwd_warp(auto& cfg, const auto& rXI_tprod_frg, auto& rXigrad_frg, const auto& rYgrad_tprod_frg) {
    auto rY_frg = make_tensor_like(rYgrad_tprod_frg);
    copy(rYgrad_tprod_frg, rY_frg);
    tprod_bcast_multiply_all_except<cfg.dim>(rY_frg, rXI_tprod_frg);
    auto rRY_frg = rY_frg.compose(cfg.RYFrg2YFrg); // reshape Y to be compatible with reduce
    smart_reduce_thread(cfg.smart_reduce, rRY_frg, rXigrad_frg, SumCallable{});
}

__device__ void tprod_bwd_CTA(auto& cfg, auto& rXigrad_frg, auto& sXigrad_tile) {
    smart_reduce_cta(cfg.smart_reduce, rXigrad_frg, sXigrad_tile, SumCallable{});
}

__device__ void tprod_bwd(auto& cfg, auto& rXI_tprod_frg, auto& rXigrad_frg, auto& rYgrad_tprod_frg, auto& sXigrad_tile) {
    tprod_bwd_warp(cfg, rXI_tprod_frg, rXigrad_frg, rYgrad_tprod_frg);
    tprod_bwd_CTA(cfg, rXigrad_frg, sXigrad_tile);
}


} // namespace vidrial