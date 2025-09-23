#pragma once
#include <iostream>
#include "../../cuda_utils/utilities.cuh"
#include "../../cuda_utils/frgthr_tiling.cuh"

using namespace cute;

namespace vidrial {

/*----------------- Thread Reduce -----------------
 * X_Shape: [reduce, batch]
 * x_Shape: [thread_reduce, batch]
 * where thread_reduce is the size of the fragment along the reduce dimension
 * 
 * At the CTA level, calling thread_reduce transforms:
 *                      X -> x
 * At the thread level, rX_frg -> rx_frg
 * 
 * Depending on the X_FrgThr, which maps [X_frg_idx, thr_idx] -> X_idx
 * The fragment X_frg is split into [innerReduce, innerBatch]
 *   innerReduceBatch_2_Frg: [innerReduce, innerBatch] -> X_Frg
 * Accordingly, reduce is split into [innerReduce, outerReduce]
 *      ReduceSplit: [innerReduce_idx, warp_reduce_idx] -> reduce_idx
 * CanonicalFrg: [innerReduce_idx, innerBatch_idx] -> X_frg_idx
 */
template<typename _XShape, typename _XFrgThr, typename _xShape, typename _xFrgThr, typename _CanonicalFrg, typename _X2x>
struct ThreadReduceCfg {
    using XShape = _XShape;
    using XFrgThr = _XFrgThr;
    using xShape = _xShape;
    using xFrgThr = _xFrgThr;
    using CanonicalFrg = _CanonicalFrg;
    using X2x = _X2x;
    using xFrgShape = decltype(get<0>(xFrgThr{}).shape());
    static constexpr int local_reduce = size<0>(CanonicalFrg{});
    static constexpr int local_batch = size<1>(CanonicalFrg{});
    XShape X_Shape;
    XFrgThr X_FrgThr;
    xShape x_Shape;
    xFrgThr x_FrgThr;
    CanonicalFrg canonical_frg;
    X2x X_2_x;
    xFrgShape x_Frg_Shape;
};

template<typename _XShape, typename _XFrgThr, typename _xShape, typename _xFrgThr, typename _CanonicalFrg, typename _X2x>
void print_cfg(ThreadReduceCfg<_XShape, _XFrgThr, _xShape, _xFrgThr, _CanonicalFrg, _X2x> const& cfg, std::string prefix = "") {
    std::cout << "ThreadReduceCfg:\n";
    std::cout << prefix << "  X_Shape: "; print(cfg.X_Shape); std::cout << "\n";
    std::cout << prefix << "  X_FrgThr: "; print(cfg.X_FrgThr); std::cout << "\n";
    std::cout << prefix << "  x_Shape: "; print(cfg.x_Shape); std::cout << "\n";
    std::cout << prefix << "  x_FrgThr: "; print(cfg.x_FrgThr); std::cout << "\n";
    std::cout << prefix << "  canonical_frg: "; print(cfg.canonical_frg); std::cout << "\n";
    std::cout << prefix << "  X_2_x: "; print(cfg.X_2_x); std::cout << "\n";
    std::cout << prefix << "  x_FrgShape: "; print(cfg.x_Frg_Shape); std::cout << "\n";
}

template<typename XShape, typename XFrgThr>
auto make_ThreadReduceCfg() {
    auto X_Frg = get<0>(XFrgThr{});
    auto X_Thr = get<1>(XFrgThr{});
    auto X2Red = projection_layout<0>(XShape{});
    auto X2Bat = projection_layout<1>(XShape{});
    auto innerBat2Frg = nullspace(X2Red.compose(X_Frg));
    auto innerRed2Frg = nullspace(X2Bat.compose(X_Frg));
    auto innerBat2X = X_Frg.compose(innerBat2Frg);
    auto innerRed2X = X_Frg.compose(innerRed2Frg);
    auto outerRed2X = complement(innerRed2X, size<0>(XShape{}));
    auto x2X = make_layout(XShape{}).compose(outerRed2X, _);
    auto x_FrgThr = left_inverse(x2X).compose(make_layout(innerBat2X, X_Thr));
    auto RedBat2Frg = make_layout(innerRed2Frg, innerBat2Frg);
    auto RedBat2xFrg = make_layout(make_layout(size(innerRed2Frg), _0{}), make_layout(innerBat2Frg.shape()));
    auto XFrg2xFrg = RedBat2xFrg.compose(right_inverse(RedBat2Frg));
    auto XFrg2x = get<0>(x_FrgThr).compose(XFrg2xFrg);
    auto X2x = make_layout(XFrg2x, get<1>(x_FrgThr)).compose(left_inverse(XFrgThr{})).compose(make_layout(XShape{}));
    auto canonicalFrg = make_layout(innerRed2Frg, innerBat2Frg);
    return ThreadReduceCfg<XShape, XFrgThr, decltype(x2X.shape()), decltype(x_FrgThr), decltype(canonicalFrg), decltype(X2x)>{};
}

/**
 * @brief Performs thread reduce
 * @param cfg The configuration of the thread reduce
 * @param fn The reduction function
 * @param rX_frg The fragment of X to reduce
 * @param rx_frg The fragment of x to accumulate the result
 */
CUTE_DEVICE void thread_reduce(auto& cfg, auto&& fn, auto& rX_frg, auto& rx_frg) {
    using T = TensorType(rX_frg);
    auto rX_cfrg = rX_frg.compose(cfg.canonical_frg);
    CUTE_UNROLL
    for (int innerBatch_idx = 0; innerBatch_idx < cfg.local_batch; innerBatch_idx++) {
        T carry = rX_cfrg(_0{}, innerBatch_idx);
        CUTE_UNROLL
        for (int innerReduce_idx = 1; innerReduce_idx < cfg.local_reduce; innerReduce_idx++)
            carry = fn(carry, rX_cfrg(innerReduce_idx, innerBatch_idx));
        using Tx = TensorType(rx_frg);
        rx_frg(innerBatch_idx) = static_cast<Tx>(fn(carry, rx_frg(innerBatch_idx)));
    }
}

/**
 * @brief Out-of-place version of thread_reduce, with zero initial value
 * @param cfg The configuration of the thread reduce
 * @param fn The reduction function
 * @param rX_frg The fragment of X to reduce
 * @return The fragment of x after the reduction
 */
CUTE_DEVICE auto thread_reduce(auto& cfg, auto&& fn, auto& rX_frg) {
    using T = TensorType(rX_frg);
    auto rx_frg = make_tensor<T>(cfg.x_Frg_Shape);
    clear(rx_frg);
    thread_reduce(cfg, fn, rX_frg, rx_frg);
    return rx_frg;
}


/*----------------- Warp Reduce -----------------
 * X: [thread_reduce, batch]
 * x: [warp_reduce, batch]
 * Accepts X_frg that are irreducible at the thread level and reduces X-> x
 * as much as possible using warp_level shufl instructions.
 * We assume that X_frg is irreducible at the thread level so X_frg = x_frg
*/
template<typename _XShape, typename _XFrgThr, typename _xShape, typename _xFrgThr, typename _X2x, typename _XReduceSteps>
struct WarpReduceCfg {
    using XShape = _XShape;
    using XFrgThr = _XFrgThr;
    using xShape = _xShape;
    using xFrgThr = _xFrgThr;
    using X2x = _X2x;
    using XReduceSteps = _XReduceSteps; // e.g. ReduceSteps = 4:2, then the threads 0,2,4,6 of each warp will perform a reduce/broadcast
    XShape X_Shape;
    XFrgThr X_FrgThr;
    xShape x_Shape;
    xFrgThr x_FrgThr;
    X2x X_2_x;
    XReduceSteps X_ReduceSteps;
};

template<typename _XShape, typename _XFrgThr, typename _xShape, typename _xFrgThr, typename _X2x, typename _XReduceSteps>
void print_cfg(WarpReduceCfg<_XShape, _XFrgThr, _xShape, _xFrgThr, _X2x, _XReduceSteps> const& cfg, std::string prefix = "") {
    std::cout << "WarpReduceCfg:\n";
    std::cout << prefix << "  X_Shape: "; print(cfg.X_Shape); std::cout << "\n";
    std::cout << prefix << "  X_FrgThr: "; print(cfg.X_FrgThr); std::cout << "\n";
    std::cout << prefix << "  x_Shape: "; print(cfg.x_Shape); std::cout << "\n";
    std::cout << prefix << "  x_FrgThr: "; print(cfg.x_FrgThr); std::cout << "\n";
    std::cout << prefix << "  X_2_x: "; print(cfg.X_2_x); std::cout << "\n";
    std::cout << prefix << "  X_ReduceSteps: "; print(cfg.X_ReduceSteps); std::cout << "\n";
}

template<typename XShape, typename XFrgThr>
auto make_WarpReduceCfg() {
    constexpr auto X_Frg = get<0>(XFrgThr{});
    constexpr auto X_Thr = get<1>(XFrgThr{});
    constexpr auto warp_size = static_min(32, size(X_Thr));
    auto ThreadPartition = zipped_divide(get<1>(XFrgThr{}), Int<warp_size>{});
    auto X_Shard = make_layout(get<0>(XFrgThr{}), get<0>(ThreadPartition));
    auto X_Warp = get<1>(ThreadPartition);
    auto ShardWarp = make_layout(X_Shard, X_Warp);
    auto X2Red = projection_layout<0>(XShape{});
    auto X2Bat = projection_layout<1>(XShape{});
    auto frgBat2Frg = nullspace(X2Red.compose(X_Frg));
    auto innerBat2Shard = nullspace(X2Red.compose(X_Shard));
    auto innerRed2Shard = nullspace(X2Bat.compose(X_Shard));
    auto frgBat2X = X_Frg.compose(frgBat2Frg);
    auto innerRed2X = X_Shard.compose(innerRed2Shard);
    auto outerRed2X = complement(innerRed2X, size<0>(XShape{}));
    auto x2X = make_layout(XShape{}).compose(outerRed2X, _);
    auto y2X = complement(x2X, size(XShape{}));
    auto xy2X = make_layout(x2X, y2X);
    auto X2xy = right_inverse(xy2X);
    auto xy2x = projection_layout<0>(xy2X.shape());
    auto X2x = xy2x.compose(X2xy);
    auto x_Thr = X2x.compose(X_Thr);
    auto x_Frg = left_inverse(x2X).compose(frgBat2X);
    auto x_FrgThr = make_layout(x_Frg, x_Thr);
    auto innerRed2Thr_ = left_inverse(X_Thr).compose(innerRed2X);
    auto innerRed2Thr = coalesce(innerRed2Thr_);
    return WarpReduceCfg<XShape, XFrgThr, decltype(x2X.shape()), decltype(x_FrgThr), decltype(X2x), decltype(innerRed2Thr)>{};
}

template<typename ReduceSteps>
CUTE_DEVICE void warp_reduce_value(auto& fn, auto& value) {
    static_assert(depth(ReduceSteps{})<=1);
    constexpr int reduce_size = get<0>(ReduceSteps{}.shape());
    constexpr int reduce_stride = get<0>(ReduceSteps{}.stride());
    static_assert(1<<static_log2<reduce_stride>()==reduce_stride, "reduce_stride must be a power of 2");
    static_assert(1<<static_log2<reduce_size>()==reduce_size, "reduce_size must be a power of 2");
    CUTE_UNROLL
    for (int lane_mask = reduce_stride; lane_mask < reduce_size*reduce_stride; lane_mask *= 2) {
        auto tmp = __shfl_xor_sync(0xffffffff, value, lane_mask, warpSize);
        value = static_cast<std::decay_t<decltype(value)>>(fn(value, tmp));
    }
    if constexpr (rank(ReduceSteps{}) > 1)
        warp_reduce_value<decltype(drop<0>(ReduceSteps{}))>(fn, value);
}

/**
 * @brief Performs warp reduce by iteratively reducing the value using shuffle instructions
 * @param cfg The configuration of the warp reduce
 * @param fn The reduction function
 * @param rX_frg The fragment of X to reduce
 */
CUTE_DEVICE void warp_reduce(auto& cfg, auto&& fn, auto& rX_frg) {
    // it is assumed that the fragment is irreducible. All innerReduce elements
    // belong to different threads in the same warp
    if constexpr (size(decltype(cfg.X_ReduceSteps){})>1) {
        CUTE_UNROLL
        for (int i=0; i<size(rX_frg); i++) {
            warp_reduce_value<decltype(cfg.X_ReduceSteps)>(fn, rX_frg(i));
        }
    }
}

/* ---------------  Smart Reduction ----------------------
 * Reduces X: [reduce, batch] -> x: [batch]
 * args:
 * - rX_frg: fragment of X according to X_FrgThr
 * - sx: [batch] shared memory tensor x holding the initial accumulator value
 * - sB: [reduce-1, batch] shared memory buffer
 * the results of the accumulation are stored in sx
 */
template<bool _skip_smem_reduce, bool _owning_thread_optimization,
         typename XShape, typename XFrgThr, typename X2x,
         typename xShape, typename xFrgThr,
         typename AShape, typename AFrgTiling, 
         typename ThreadReduce, typename WarpReduce>
struct SmartReduceCfg {
    static constexpr int warp_reduce_size = size<0>(AShape{});
    static constexpr bool skip_smem_reduce = _skip_smem_reduce;
    static constexpr bool owning_thread_optimization = _owning_thread_optimization;
    static constexpr int thread_num = size<1>(XFrgThr{});
    ThreadReduce thread_reduce;
    WarpReduce warp_reduce;
    X2x X_2_x;
    struct X_t {
        XShape shape; // [reduce, batch]
        XFrgThr frg_thr;
        decltype(get<0>(XFrgThr{}.shape())) frg_shape;
    } X;
    struct x_t {
        xShape shape; // [batch]
        xFrgThr frg_thr;
        decltype(get<0>(xFrgThr{}.shape())) frg_shape;
    } x;
    struct A_t {
        AFrgTiling frg_tiling; // store and load rows of A
        using FrgThr_t = typename AFrgTiling::FrTh_t;
        AShape shape; // [warp_reduce_size, batch]
        FrgThr_t frg_thr;
        decltype(get<0>(FrgThr_t{}.shape())) frg_shape;
    } A;
    CUTE_HOST_DEVICE bool owns_frg() const {
        return owns_frg(threadIdx.x);
    }
    CUTE_HOST_DEVICE bool owns_frg(int thread_idx) const {
        // check if this thread is the first among all the threads that hold the same fragment
        auto l = get<1>(x.frg_thr);
        auto flip_str = transform(l.stride(), [](auto s) {
                if constexpr (s == _0{}) { return _1{}; }
                else { return _0{}; }
            });
        auto L = make_layout(l.shape(), flip_str);
        return L(thread_idx) == 0 && threadIdx.x < size<1>(x.frg_thr);
    }
};

template<bool _skip_smem_reduce, bool _owning_thread_optimization,
         typename XShape, typename XFrgThr, typename X2x,
         typename xShape, typename xFrgThr,
         typename AShape, typename AFrgTiling, 
         typename ThreadReduce, typename WarpReduce>
void print_cfg(SmartReduceCfg<_skip_smem_reduce, _owning_thread_optimization,
                       XShape, XFrgThr, X2x,
                       xShape, xFrgThr,
                       AShape, AFrgTiling, 
                       ThreadReduce, WarpReduce> const& cfg, std::string prefix = "") {
    std::cout << "SmartReduceCfg:\n";
    std::cout << prefix << "  X.shape: "; print(cfg.X.shape); std::cout << "\n";
    std::cout << prefix << "  X.frg_thr: "; print(cfg.X.frg_thr); std::cout << "\n";
    std::cout << prefix << "  X.frg_shape: "; print(cfg.X.frg_shape); std::cout << "\n";
    std::cout << prefix << "  x.shape: "; print(cfg.x.shape); std::cout << "\n";
    std::cout << prefix << "  x.frg_thr: "; print(cfg.x.frg_thr); std::cout << "\n";
    std::cout << prefix << "  x.frg_shape: "; print(cfg.x.frg_shape); std::cout << "\n";
    std::cout << prefix << "  A.shape: "; print(cfg.A.shape); std::cout << "\n";
    std::cout << prefix << "  A.frg_tiling: "; print_cfg(cfg.A.frg_tiling, prefix + "  A.frg_tiling: "); std::cout << "\n";
    std::cout << prefix << "  warp_reduce_size: " << cfg.warp_reduce_size << "\n";
    std::cout << prefix << "  skip_smem_reduce: " << cfg.skip_smem_reduce << "\n";
    std::cout << prefix << "  owning_thread_optimization: " << cfg.owning_thread_optimization << "\n";
    std::cout << prefix << "  thread_num: " << cfg.thread_num << "\n";
    std::cout << prefix << "  thread_reduce: "; print_cfg(cfg.thread_reduce, prefix + "  thread_reduce: "); std::cout << "\n";
    std::cout << prefix << "  warp_reduce: "; print_cfg(cfg.warp_reduce, prefix + "  warp_reduce: "); std::cout << "\n";
    std::cout << prefix << "  X_2_x: "; print(cfg.X_2_x); std::cout << "\n";
}

template<bool owning_thread_optimization=true, typename XShape, typename XFrgThr>
auto make_SmartReduceCfg(XShape, XFrgThr) {
    constexpr int thread_num = size<1>(XFrgThr{});
    constexpr int warp_num = (thread_num + 31) / 32;
    constexpr int reduce = size<0>(XShape{});
    constexpr int batch = size<1>(XShape{});
    // First step of the reduction is local to the thread
    auto thread_reduce = make_ThreadReduceCfg<XShape, XFrgThr>();
    // second step is local to the warp
    auto warp_reduce = make_WarpReduceCfg<decltype(thread_reduce.x_Shape), decltype(thread_reduce.x_FrgThr)>();
    static_assert(size<1>(warp_reduce.x_Shape) == batch);
    // how much is left to reduce after the warp reduction
    constexpr int warp_reduce_size = size<0>(decltype(warp_reduce.x_Shape){});
    static_assert(warp_reduce_size > 0 && warp_reduce_size <= warp_num);
    constexpr bool skip_smem_reduce = (warp_reduce_size == 1);
    // x variable
    auto x_shape = Shape<Int<batch>>{};
    auto proj = Layout<Shape<Int<warp_reduce_size>,Int<batch>>, Stride<_0,_1>>{};
    auto x_frg_thr = coalesce(proj.compose(warp_reduce.x_FrgThr), make_tuple(_0{},_0{})); // every thread has a natural fragment of x
    // smem buffer holds the accumulated values of the warps
    auto A_shape = warp_reduce.x_Shape;
    auto A_tile_shape = Shape<_1, Int<batch>>{};
    auto A_tile_rest = zipped_divide(make_layout(A_shape), A_tile_shape);
    auto A_frg_thr = warp_reduce.x_FrgThr;
    auto A_frg_tiling = make_FrgThrTilingCfg(A_tile_rest, A_frg_thr);
    auto X2x = make_layout(XShape{}, make_stride(_0{}, _1{}));
    return SmartReduceCfg<skip_smem_reduce, owning_thread_optimization,
                       XShape, XFrgThr, decltype(X2x),
                       decltype(x_shape), decltype(x_frg_thr),
                       decltype(A_shape), decltype(A_frg_tiling),
                       decltype(thread_reduce), decltype(warp_reduce)>{};
}

// Internal implementation of smart_reduce_cta with owning thread optimization
CUTE_DEVICE void _smart_reduce_cta_owning_thread(auto& cfg, auto& rx_acc_frg, auto& sx, auto&& fn) {
    CUTE_UNROLL
    for (int warp_reduce_idx=1; warp_reduce_idx<cfg.warp_reduce_size; warp_reduce_idx++) {
        FrgThr_store_tile(cfg.A.frg_tiling, rx_acc_frg, sx, warp_reduce_idx); // store one of the rows of [warp_reduce, batch] to sx
        __syncthreads();
        if (cfg.owns_frg()) // if thread owns the accumulator, combine with the current row in sx
            elementwise_tensor(fn, rx_acc_frg, slice_rest(sx, cfg.x.frg_thr, threadIdx.x));
        __syncthreads(); // don't do the next step until we are done reading from smem
    }
}

// Internal implementation of smart_reduce_cta without owning thread optimization
CUTE_DEVICE void _smart_reduce_cta_all_threads(auto& cfg, auto& rx_acc_frg, auto& sx, auto&& fn) {
    if constexpr (cfg.warp_reduce_size > 1) {
        CUTE_UNROLL
        for (int warp_reduce_idx=0; warp_reduce_idx<cfg.warp_reduce_size; warp_reduce_idx++) {
            FrgThr_store_tile(cfg.A.frg_tiling, rx_acc_frg, sx, warp_reduce_idx); // store one of the rows of [warp_reduce, batch] to sx
            __syncthreads();
            elementwise_tensor(fn, rx_acc_frg, slice_rest(sx, cfg.x.frg_thr, threadIdx.x));
            __syncthreads(); // don't do the next step until we are done reading from smem
        }
    }
}

/**
 * @brief Performs CTA reduce by iteratively storing and reading tiles to/from smem and reducing them
 * @param cfg The configuration of the smart reduce
 * @param rx_acc_frg The fragment of x to accumulate the result
 * @param sx The shared memory tensor to accumulate the result
 * @param fn The reduction function
 */
CUTE_DEVICE void reduce_cta(auto& cfg, auto& rx_acc_frg, auto& sx, auto&& fn) {
    if constexpr (cfg.owning_thread_optimization)
        _smart_reduce_cta_owning_thread(cfg, rx_acc_frg, sx, fn);
    else
        _smart_reduce_cta_all_threads(cfg, rx_acc_frg, sx, fn);
}

// -------------- Smart Reduce Functions  --------------
// Smart reduce is a collection of functions that performs reduction operations on tensors, including:
// - smart_thread_reduce: performs local reduction on each thread
// - smart_reduce_warp:   performs thread reduce and then warp reduce
// - smart_reduce:        performs thread reduce, and then warp reduce, and then CTA reduce (with optional owning thread optimization)
// - smart_reduce_cta:    performs warp reduceand then CTA reduce

/**
 * @brief Performs local reduction on each thread
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param rx_acc_frg The fragment of x to accumulate the result
 * @param fn The reduction function
 */
CUTE_DEVICE void smart_reduce_thread(auto& cfg, auto& rX_frg, auto& rx_acc_frg, auto&& fn) {
    thread_reduce(cfg.thread_reduce, fn, rX_frg, rx_acc_frg); // every thread performs a local reduction
}

/**
 * @brief Out-of-place version of smart_reduce_thread, with zero initial value
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param fn The reduction function
 * @return The fragment of x after the reduction
 */
CUTE_DEVICE auto smart_reduce_thread(auto& cfg, auto& rX_frg, auto&& fn) {
    return thread_reduce(cfg.thread_reduce, fn, rX_frg);
}

/**
 * @brief Performs thread reduce and then warp reduce
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param rx_acc_frg The fragment of x to accumulate the result
 * @param fn The reduction function
 */
CUTE_DEVICE void smart_reduce_warp(auto& cfg, auto& rX_frg, auto& rx_acc_frg, auto&& fn) {
    thread_reduce(cfg.thread_reduce, fn, rX_frg, rx_acc_frg); // every thread performs a local reduction
    warp_reduce(cfg.warp_reduce, fn, rx_acc_frg); // then the warp reduces as much as possible
}

/**
 * @brief Out-of-place version of smart_reduce_warp, with zero initial value
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param fn The reduction function
 * @return The fragment of x after the reduction
 */
CUTE_DEVICE auto smart_reduce_warp(auto& cfg, auto& rX_frg, auto&& fn) {
    auto rx_frg = thread_reduce(cfg.thread_reduce, fn, rX_frg); // every thread performs a local reduction
    warp_reduce(cfg.warp_reduce, fn, rx_frg); // then the warp reduces as much as possible
    return rx_frg;
}

/**
 * @brief Performs warp reduce and then CTA reduce
 * @param cfg The configuration of the smart reduce
 * @param rx_acc_frg The fragment of x to accumulate the result
 * @param sx The shared memory tensor to accumulate the result
 * @param fn The reduction function
 */
CUTE_DEVICE void smart_reduce_cta(auto& cfg, auto& rx_acc_frg, auto& sx, auto&& fn) {
    warp_reduce(cfg.warp_reduce, fn, rx_acc_frg); // then the warp reduces as much as possible
    reduce_cta(cfg, rx_acc_frg, sx, fn);
}

/**
 * @brief Performs thread reduce, warp reduce and then CTA reduce
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param rx_acc_frg The fragment of x to accumulate the result
 * @param sx The shared memory tensor to accumulate the result
 * @param fn The reduction function
 * @note This function is the main entry point for smart reduction
 */
CUTE_DEVICE void smart_reduce(auto& cfg, auto& rX_frg, auto& rx_acc_frg, auto& sx, auto&& fn) {
    smart_reduce_warp(cfg, rX_frg, rx_acc_frg, fn);
    reduce_cta(cfg, rx_acc_frg, sx, fn);
}

/**
 * @brief Out-of-place version of smart_reduce, with zero initial value
 * @param cfg The configuration of the smart reduce
 * @param rX_frg The fragment of X to reduce
 * @param sx The shared memory tensor to accumulate the result
 * @param fn The reduction function
 * @return The fragment of x after the reduction
 */
CUTE_DEVICE auto smart_reduce(auto& cfg, auto& rX_frg, auto& sx, auto&& fn) {
    auto rx_frg = smart_reduce_warp(cfg, rX_frg, fn);
    reduce_cta(cfg, rx_frg, sx, fn);
    return rx_frg;
}

// -------------- Helpers --------------
struct SumCallable {
    template<typename Ta, typename Tb> CUTE_HOST_DEVICE
    auto operator()(Ta a, Tb b) {
        return a + b;
    }
};
struct MaxCallable {
    template<typename Ta, typename Tb> CUTE_HOST_DEVICE
    auto operator()(Ta a, Tb b) {
        return a > b ? a : b;
    }
};


} // namespace vidrial
