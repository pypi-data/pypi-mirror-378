#pragma once
#include <cute/tensor.hpp>
#include <cute/numeric/integral_constant.hpp> 
#include "frg_copy.cuh"
#include "utilities.cuh"


namespace vidrial {
  using namespace cute;

// ----- New API -----

/*
* Given a frgThr layout, we want to know for one round of copy operation,
* what's the largest contiguous strip of indices to be copied across a warp.
*/
template<typename FrgThr>
static constexpr auto warp_contiguous_strip(FrgThr frgThr) {
    using SrcFrg = decltype(get<0>(frgThr));
    using SrcThr = decltype(get<1>(frgThr));
    using SrcWarp = decltype(get<0>(size_divide<32>(SrcThr{})));
    using ValWarp = decltype(make_layout(get<0>(SrcFrg{}), SrcWarp{}));
    return largest_contiguous_cosize(ValWarp{});
}

/*
* Given a copy trait, extract the number of bytes to be copied
*/
template<typename Struct>
static constexpr auto copy_size(Copy_Traits<Struct>) {
    return sizeof(typename Struct::DRegisters{});
}

/**
 * @brief Make a swizzle info struct, a frgthr should correspond to one swizzle info struct.
 * @tparam v_size_      The number of elements touched by a single copy atom. This determines the M parameter of the swizzle as it needs to be contiguous and thus not touched by swizzle.
 * @tparam warp_v_size_ The number of indices (in the codomain of a sTile∘frgThr) touched by a single warp. This helps determine the S parameter of the swizzle as we want to know the number of banks touched by a single warp.
 */
template<int v_size_, int warp_v_size_>
struct SwizzleInfo {
    static constexpr int v_size = v_size_;
    static constexpr int warp_v_size = warp_v_size_;
};

/**
 * @brief Determine the swizzle info struct for a given frgthr, sTile, and copy atom.
 * @tparam is_load_ Whether the frgthr is for loading or storing.
 * @tparam T         The element type of the data being copied.
 * @tparam STile     The sTile layout.
 * @tparam FrgThr    The frgThr layout.
 * @tparam CopyAtom  The copy atom to use for loading or storing.
 */
template<bool is_load, typename T, typename STile, typename FrgThr, typename CopyAtom>
constexpr auto make_swizzle_info() {
    constexpr auto atom_bytes = copy_size(typename CopyAtom::Traits{});
    constexpr auto v_size = atom_bytes / sizeof(T);
    static_assert(v_size > 0, "v_size must be positive, copy atom too small");

    using RetiledFrgThr = decltype(retile_frgthr<is_load, FrgThr, CopyAtom>());
    using Stile_o_FrgThr = decltype(composition(STile{}, RetiledFrgThr{}));
    constexpr auto warp_v_size = size(warp_contiguous_strip(Stile_o_FrgThr{}));
    return SwizzleInfo<v_size, warp_v_size>{};
}

/**
 * @brief Determine the swizzle based on 2 swizzle info structs.
 * @tparam T         The element type of the data being copied.
 * @tparam STile     The sTile layout.
 * @tparam v_size_1 The number of elements touched by a single copy atom for the first swizzle info struct.
 * @tparam v_size_2 The number of elements touched by a single copy atom for the second swizzle info struct.
 * @tparam warp_v_size_1 The number of indices (in the codomain of a sTile∘frgThr) touched by a single warp for the first swizzle info struct.
 * @tparam warp_v_size_2 The number of indices (in the codomain of a sTile∘frgThr) touched by a single warp for the second swizzle info struct.
 */
template<typename T, typename STile, int v_size_1, int v_size_2, int warp_v_size_1, int warp_v_size_2>
constexpr auto make_swizzle(SwizzleInfo<v_size_1, warp_v_size_1> info_1, SwizzleInfo<v_size_2, warp_v_size_2> info_2) {
    constexpr auto M = static_log2<static_max(static_max(info_1.v_size, info_2.v_size), 1)>();
    constexpr auto bank_groups = 128 / sizeof(T);
    constexpr auto S_max = static_log2<static_max(bank_groups, 1)>() - M;
    constexpr auto S_1 = static_min(S_max, static_log2<static_max(info_1.warp_v_size, 1)>() - M);
    constexpr auto S_2 = static_min(S_max, static_log2<static_max(info_2.warp_v_size, 1)>() - M);
    constexpr auto S = static_max(static_max(S_1, S_2), 0);
    constexpr auto B = static_max(static_min(static_log2<size(STile{})>() - S - M, S), 0);
    return Swizzle<Int<B>{}, Int<M>{}, Int<S>{}>{};
}

/**
 * @brief Determine a swizzle based a sTile layout, a write frgthr, a read frgthr, a write atom, and an optional read atom. The end result is a swizzle that:
 * 1. Ensures both write and read atoms and frgthr are still compatible with the Swizzle∘sTile layout.
 * 2. Reduces bank conflicts as much as possible.
 * @tparam T         The element type of the data being copied.
 * @tparam STile     The sTile layout.
 * @tparam WriteFrgThr The frgThr for writing.
 * @tparam ReadFrgThr The frgThr for reading.
 * @tparam WriteAtom The write atom to use for writing.
 */
template<typename T, typename STile, typename WriteFrgThr, typename ReadFrgThr, typename WriteAtom, typename ReadAtom=decltype(infer_copy_atom<true, false, T, ReadFrgThr, STile>())>
constexpr auto make_swizzle_g2s2r() {
    constexpr auto write_info = make_swizzle_info<true, T, STile, WriteFrgThr, WriteAtom>();
    constexpr auto read_info = make_swizzle_info<false, T, STile, ReadFrgThr, ReadAtom>();
    constexpr auto swizzle = make_swizzle<T, STile>(write_info, read_info);
    constexpr auto swizzled_stile = composition(swizzle, STile{});
    static_assert(is_compatible<true, false, T, ReadAtom, ReadFrgThr, decltype(swizzled_stile)>(), "swizzled_stile is not compatible with ReadAtom and ReadFrgThr");
    return swizzle;
}

// ----- Old API -----

/*
 * Given an sTile layout, convert it into a swizzled sTile layout. Here we make the following assumptions:
 * 1. The sTile layout is a row-major 2D layout (usually the case for A_Tile and B_Tile in cute)
 * 
 * 
 * 2^S cell per row─────────────────┐              
 * 2^M element per cell────┐        │              
 *                         ▼        ▼              
 *                       ┌───┐───┐───┐───┐───────┐ 
 *                       └───┘───┘───┘───┘       │ 
 *                       │                       │ 
 * 2^B rows per unit ◄── │                       │ 
 *                       │     Swizzle Unit      │ 
 *                       │                       │ 
 *                       │                       │ 
 *                       └───────────────────────┘ 
 * 
 */
template<typename G2SCfg_, typename STile_, typename FrgThr_, int swizzle_mode=1>
struct SwizzleCfg {
    /*
     * Find compatible copy atom to use
     */
    template<typename STile, typename FrgThr>
    static constexpr auto find_compatible_copy_atom() {
        if constexpr (is_ldsm_compatible<T>(STile{}, FrgThr{})) {
            return compatible_ldsm_atom<T>(STile{}, FrgThr{});
        } else {
            return DefaultCopy{};
        }
    }

    /*
     * Convert a frgThr layout into srcFrgThr layout
     */
    template<typename FrgThr, typename CopyAtom>
    static constexpr auto frgThr2srcFrgThr(std::false_type /* is_universal_copy */, FrgThr frgThr, CopyAtom) {
        using AtomNumVal = decltype(size<1>(typename CopyAtom::ValLayoutRef{}));
        using AtomNumThr = decltype(size<0>(typename CopyAtom::ValLayoutRef{}));
        using AtomLayoutSrc = typename CopyAtom::ValLayoutSrc; // (src_thr,src_val) -> offset
        using AtomLayoutDst = typename CopyAtom::ValLayoutDst; // (dst_thr,dst_val) -> offset
        constexpr auto src2dst = decltype(right_inverse(select<1,0>(AtomLayoutDst{})).compose(select<1,0>(AtomLayoutSrc{}))){};
        // (src_frg, rest_frg) -> (dst_frg, rest_frg)
        // assuming the trg2dst is contiguous within atom boundary
        constexpr auto trg_frgthr_tiled = zipped_divide(frgThr, make_shape(AtomNumVal{}, AtomNumThr{}));
        // ((atom_frg, atom_thr), (rest_frg, rest_thr)) -> coord
        constexpr auto src_frgthr_tiled = trg_frgthr_tiled.compose(src2dst, _);
        // ((atom_src_frg, atom_src_thr), (rest_frg, rest_thr)) -> coord
        constexpr auto src_frgthr = coalesce(zip(src_frgthr_tiled), Shape<Shape<_1,_1>,_1>{});
        // (src_frg, src_thr) -> coord
        return src_frgthr;
    }

    template<typename FrgThr, typename CopyAtom>
    static constexpr auto frgThr2srcFrgThr(std::true_type /* is_universal_copy */, FrgThr frgThr, CopyAtom) {
        return frgThr;
    }


    template<typename T, typename STile, typename SrcFrgThr, typename WriteAtom, bool write_optimized>
    static constexpr auto swizzled_sTile(STile sTile, SrcFrgThr read_FrgThr, WriteAtom write_atom){
        static_assert(rank(sTile) == 2, "sTile must be a 2D layout");
        static_assert(depth(sTile) == 1, "sTile must be a simple depth-1 stile to be swizzled");
        static_assert(has_major_dim<STile>(), "sTile must have a major dim");
        using TileShape = decltype(sTile.shape());
        constexpr auto write_bytes = copy_size(typename WriteAtom::Traits{});
        constexpr auto major_dim = flat_major_dim(STile{});
    
        // ---- Compute M
        // 2^M is the smallest un-swizzled sub-unit, so it matches the contiguous size of a single source fragment
        constexpr auto read_frg_major_mode = major_mode(get<0>(coalesce(read_FrgThr, Shape<Shape<_1,_1>,_1>{})));
        constexpr auto read_frg_contiguous_size = static_max(1, get<0>(read_frg_major_mode.shape()));
        constexpr auto write_size = write_bytes / sizeof(T);
        constexpr auto M = static_log2<static_max(read_frg_contiguous_size, write_size)>();

        // ---- Compute S
        // 2^(M+S) is the first index where swizzle starts, so it needs to cover, as contiguous as
        // possible, the first round of copy operation generated by all threads in a warp, subject 
        // to the limit that all 32 banks are fully utilized (128 bytes in total)
        constexpr auto read_warp_contiguous_size = size(warp_contiguous_strip(read_FrgThr));
        constexpr auto optimal_read_S = static_max(0, static_min(static_log2<static_max(128/sizeof(T), 1)>() - M, static_log2<static_max(read_warp_contiguous_size, 1)>() - M));
        constexpr auto optimal_write_S = static_max(0, static_log2<128/sizeof(T)>() - M);
        constexpr auto S = static_max(write_optimized ? optimal_write_S : optimal_read_S, 0);

        // ---- Compute B
        // 2^B is simply the number of times the warp_contiguous_strip needs to be tiled to cover
        // the entire sTile, subject to the limit that B <= M. If B is negative, we set it to 0 because
        // the tile is too small to be swizzled.
        constexpr auto B = static_max(static_min(static_log2<size(sTile)>() - S - M, S), 0);

        return Swizzle<Int<B>{}, Int<M>{}, Int<S>{}>{};
    }
    
    using G2SCfg = G2SCfg_;
    using T = typename G2SCfg::T;
    using STile = STile_;
    using FrgThr = FrgThr_;
    static constexpr bool write_optimized = swizzle_mode == 1;
    using ReadAtom = decltype(find_compatible_copy_atom<STile, FrgThr>());
    using WriteAtom = typename G2SCfg::G2SCopyAtom;
    ReadAtom read_atom{};
    WriteAtom write_atom{};

    using SrcFrgThr = decltype(frgThr2srcFrgThr(
            std::integral_constant<bool, is_universal_copy_v<ReadAtom>>(), 
            FrgThr{}, ReadAtom{}));
    static constexpr FrgThr frgThr{};
    static constexpr SrcFrgThr srcFrgThr{};
    static constexpr auto srcfrg_major_mode = major_mode(get<0>(coalesce(srcFrgThr, Shape<Shape<_1,_1>,_1>{})));
    static constexpr auto srcfrg_contiguous_size = static_max(1, get<0>(srcfrg_major_mode.shape()));
    static constexpr auto M = static_log2<srcfrg_contiguous_size>();
    using Swizzle_t = decltype(swizzled_sTile<T, STile, SrcFrgThr, WriteAtom, write_optimized>(STile{}, SrcFrgThr{}, write_atom));
    using SwizzledSTile = decltype(composition(Swizzle_t{}, STile{}));
    Swizzle_t swizzle{};
};

template<typename G2SCfg_, typename STile_, typename FrgThr_>
struct NoSwizzle {
    using G2SCfg = G2SCfg_;
    using T = typename G2SCfg::T;
    using STile = STile_;
    using FrgThr = FrgThr_;
    using SwizzledSTile = STile;
    using Swizzle_t = Swizzle<Int<0>{}, Int<0>{}, Int<0>{}>;
    Swizzle_t swizzle{};
};


template<typename G2SCfg, typename STile, typename FrgThr, int swizzle_mode = 1,
         typename std::enable_if<(swizzle_mode == 1), int>::type = 0>
constexpr auto make_swizzle_cfg(STile sTile, FrgThr frgThr) {
    return SwizzleCfg<G2SCfg, STile, FrgThr, swizzle_mode>{};
}

template<typename G2SCfg, typename STile, typename FrgThr, int swizzle_mode = 0,
         typename std::enable_if<(swizzle_mode == 0), int>::type = 0>
constexpr auto make_swizzle_cfg(STile sTile, FrgThr frgThr) {
    return NoSwizzle<G2SCfg, STile, FrgThr>{};
}



// Primary template for types without layout_b()
template<typename Layout, typename = void>
struct NonSwizzledImpl {
    static constexpr auto apply(Layout layout) {
        return layout;
    }
};

// Specialization for types with layout_b()
template<typename Layout>
struct NonSwizzledImpl<Layout, std::void_t<decltype(Layout{}.layout_b())>> {
    static constexpr auto apply(Layout layout) {
        return layout.layout_b();
    }
};

// Single function that uses the implementation struct
template<typename Layout>
constexpr auto non_swizzled(Layout layout) {
    return NonSwizzledImpl<Layout>::apply(layout);
}


}// namespace vidrial

