// 2D masking
#pragma once
#include <limits>
#include <type_traits>
#include <iostream>
#include <cute/tensor.hpp>
#include <cute/numeric/integral_constant.hpp> 

namespace vidrial {
using namespace cute;

// ---------- Mask States (runtime) ----------
/**
 * @brief Generic causal mask state. It contains the runtime information required for generic causal masking.
 * @tparam r The number of rows in a mask cell
 * @tparam w The number of cols in a mask cell
 */
template <int r_=1, int w_=1>
struct CausalMaskState {
    static constexpr int r = r_;
    static constexpr int w = w_;

    int row_base;
    int col_base;

    CUTE_HOST_DEVICE CausalMaskState(int row_base, int col_base, int total_rows, int total_cols)
    : row_base(row_base + total_cols / w - total_rows / r), col_base(col_base) {}
};

/**
 * @brief Causal mask predicate. Check if a coordinate is valid for causal masking.
 * @param state The mask state
 * @param coord The coordinate to check
 */
struct CausalMask {
    // return true if the coordinate is valid, false otherwise
    template <typename Coord>
    CUTE_HOST_DEVICE bool operator()(CausalMaskState<> const& state, Coord const& coord) const {
        return (get<0>(coord) / state.r + state.row_base) >= (get<1>(coord) / state.w + state.col_base);
    }
};

/**
 * @brief Sliding window mask state. It contains the runtime information required for sliding window masking.
 */
struct SlidingWindowMaskState {
    int row_base;       // base row index (global X)
    int col_base;       // base col index (global Y)
    int left;           // allowed window to the left of col (inclusive)
    int right;          // allowed window to the right of col (inclusive)
};

/**
 * @brief Sliding window mask predicate. It checks if a coordinate is valid for sliding window masking.
 */
struct SlidingWindowMask {
    template <typename Coord>
    CUTE_HOST_DEVICE bool operator()(SlidingWindowMaskState const& state, Coord const& coord) const {
        return (get<1>(coord) + state.col_base) < (get<0>(coord) + state.row_base - state.left) || (get<1>(coord) + state.col_base) > (get<0>(coord) + state.row_base + state.right);
    }
};

// Mask-State Specialization
namespace detail {
    template <typename>
    struct MaskStateMap;
    
    template <>
    struct MaskStateMap<CausalMask> { using type = CausalMaskState<>; };
    
    template <>
    struct MaskStateMap<SlidingWindowMask> { using type = SlidingWindowMaskState; };
} // namespace detail
    
template <typename Mask>
using MaskState = typename detail::MaskStateMap<Mask>::type;


// ---------- Mask Ops ----------
struct OpZero { template<typename U> CUTE_HOST_DEVICE U operator()(U &x) const { return U(0); } };

struct OpPosInf { template<typename U> CUTE_HOST_DEVICE U operator()(U &x) const { return std::numeric_limits<U>::infinity(); } };

struct OpNegInf { template<typename U> CUTE_HOST_DEVICE U operator()(U &x) const { return -std::numeric_limits<U>::infinity(); } };


// ---------- Mask Space Projection ----------
/**
 * @brief Make a frgthr coord layout from a tile shape and a frgthr
 * @tparam TileShape The shape of the tile
 * @tparam FrgThr The frgthr to use
 * @return The frgthr coord layout: (frg, thr) -> (coord as tuple)
 */
template <typename TileShape, typename FrgThr>
CUTE_HOST_DEVICE constexpr auto make_frgthr_coord() {
    using IdentityLayout = decltype(make_identity_layout(TileShape{}));
    using FrgThrCoord = decltype(composition(IdentityLayout{}, FrgThr{}));
    return FrgThrCoord{};
}


// ---------- MaskCfg ----------
/**
 * @brief Mask config. It contains the static information required for masking.
 * @tparam T_           The element type of the data in the tile
 * @tparam FrgThrCoord_    The frg coord layout: (frg, thr) -> (coord as tuple)
 * @tparam Predicate_   The predicate to check if a coordinate is valid
 * @tparam Op_          The operation to apply to the data
 */
template <typename T_, typename FrgThrCoord_, typename Predicate_, typename Op_>
struct MaskCfg {
    using T = T_;
    using FrgThrCoord = FrgThrCoord_;
    using Predicate = Predicate_;
    using Op = Op_;

    FrgThrCoord frgthr_coord; // frg coord layout: (frg, thr) -> (coord as tuple)
    Predicate pred; // predicate to check if a coordinate is valid
    Op op; // operation to apply to the data
};

template<typename T_, typename FrgThrCoord_, typename Predicate_, typename Op_>
void print_cfg(MaskCfg<T_, FrgThrCoord_, Predicate_, Op_> const& cfg, std::string prefix = "") {
    std::cout << "MaskCfg:\n";
    std::cout << prefix << "  frgthr_coord: "; print(cfg.frgthr_coord); std::cout << "\n";
    if constexpr(std::is_same_v<Predicate_, CausalMask>) {
        std::cout << prefix << "  pred: CausalMask\n";
    } else if constexpr(std::is_same_v<Predicate_, SlidingWindowMask>) {
        std::cout << prefix << "  pred: SlidingWindowMask\n";
    }
    if constexpr(std::is_same_v<Op_, OpZero>) {
        std::cout << prefix << "  op: OpZero\n";
    } else if constexpr(std::is_same_v<Op_, OpPosInf>) {
        std::cout << prefix << "  op: OpPosInf\n";
    } else if constexpr(std::is_same_v<Op_, OpNegInf>) {
        std::cout << prefix << "  op: OpNegInf\n";
    }
}

/**
 * @brief Make a mask config
 * @tparam T        The element type of the data in the tile
 * @tparam TileShape     The tile shape
 * @tparam FrgThr   The frgthr to use
 * @tparam Pred     The predicate to use, default to CausalMask
 * @tparam Op       The operation to apply to the data, default to OpZero
 * @return The mask config
 */
template <typename T, typename TileShape, typename FrgThr, typename Predicate=CausalMask, typename Op=OpZero>
constexpr auto make_mask_cfg() {
    using FrgThrCoord = decltype(make_frgthr_coord<TileShape, FrgThr>());
    return MaskCfg<T, FrgThrCoord, Predicate, Op>{};
}

/**
 * @brief Make a mask state
 * @tparam MaskCfg The mask config
 * @tparam Args The arguments to pass to the constructor of the mask state
 * @return The mask state
 */
template <typename MaskCfg, typename... Args>
CUTE_HOST_DEVICE auto make_mask_state(MaskCfg const& cfg, Args&&... args) {
    return MaskState<typename MaskCfg::Predicate>{std::forward<Args>(args)...};
}

/**
 * @brief Apply a mask to a frg
 * @param cfg The mask config
 * @param state The runtime state for masking, containing all dynamic information required
 * @param fragment The fragment to mask
 */
CUTE_DEVICE auto mask_frg(auto const& cfg, auto&& state, auto &frg) {
    CUTE_UNROLL
    for (int i = 0; i < size(frg); ++i) {
        if (!cfg.pred(state, cfg.frgthr_coord(i, threadIdx.x))) {
            frg[i] = cfg.op(frg[i]);
        }
    }
}

} // namespace vidrial