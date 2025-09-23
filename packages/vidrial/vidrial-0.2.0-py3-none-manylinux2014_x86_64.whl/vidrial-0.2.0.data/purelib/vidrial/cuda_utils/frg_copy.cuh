#pragma once
#include <cute/tensor.hpp>
#include "utilities.cuh"

namespace vidrial {
    using namespace cute;

// ----- SFINAE for universal copy -----
template<typename T>
struct is_universal_copy : std::false_type {};
template<typename S, typename D>
struct is_universal_copy<UniversalCopy<S, D>> : std::true_type {};
template<int MaxVecBits>
struct is_universal_copy<AutoVectorizingCopyWithAssumedAlignment<MaxVecBits>> : std::true_type {};

// ----- SFINAE for zipped_divide -----
template<typename L1, typename L2>
constexpr bool is_zipped_dividable_v = cute::is_valid([](auto l1, auto l2) -> decltype(zipped_divide(l1, l2)) {})(L1{}, L2{});


// Convenience variable template
template<typename T>
inline constexpr bool is_universal_copy_v = is_universal_copy<T>::value;

/*
 * Retile a frg (arbitrary layout) to be compatible with the copy atom [V, Rest...]
 */
template<bool is_load, typename CopyAtom, typename FrgThr, typename Frg>
CUTE_HOST_DEVICE auto retile_frg(Frg &&frg) {
    if constexpr (is_universal_copy_v<CopyAtom>) {
        return make_tensor(frg.data(), frg.layout());
    } else {
        using AtomNumThr = std::conditional_t<is_load,
                                decltype(size<0>(typename CopyAtom::ValLayoutRef{})),
                                decltype(size<0>(typename CopyAtom::ValLayoutSrc{}))>;
        using AtomNumVal = std::conditional_t<is_load,
                                decltype(size<1>(typename CopyAtom::ValLayoutRef{})),
                                decltype(size<1>(typename CopyAtom::ValLayoutSrc{}))>;
        // Note that this zipped_divide assumes that we tile the frgthr contiguously, which constrains the possible ways to retile the frgthr. Empirically this is fine.
        auto copy_frgthr = zipped_divide(FrgThr{}, make_shape(AtomNumVal{}, AtomNumThr{}));
        // ((copy_frg, copy_thr), (rest_frg, rest_thr)) -> coord
        auto coord2frgthr = right_inverse(FrgThr{});
        // (coord) -> (frg, thr)
        auto frgthr2frgthr = coord2frgthr.compose(copy_frgthr);
        // ((copy_frg, copy_thr), (rest_frg, rest_thr)) -> (frg, thr)
        auto frgthr_frgthr = zip(frgthr2frgthr);
        // ((copy_frg, rest_frg), (copy_thr, rest_thr)) -> (frg, thr)
        auto copyfrg2frg = get<0>(frgthr_frgthr);
        // (copy_frg, rest_frg) -> frg
        auto dst_frg = make_tensor(frg.data(), frg.layout().compose(copyfrg2frg));
        return dst_frg;
    }
}

/*
 * Retile a frgThr (arbitrary layout) to be compatible with the copy atom [[V, Rest...], Thr]
 */
template<bool is_load, typename FrgThr, typename CopyAtom>
CUTE_HOST_DEVICE constexpr auto retile_frgthr() {
    if constexpr (is_universal_copy_v<CopyAtom>) {
        return FrgThr{};
    } else {
        using AtomNumThr = decltype(size<0>(typename CopyAtom::ValLayoutRef{}));
        using AtomNumVal = decltype(size<1>(typename CopyAtom::ValLayoutRef{}));
        using AtomLayoutSrc = decltype(select<1,0>(typename CopyAtom::ValLayoutSrc{}));
        using AtomLayoutDst = decltype(select<1,0>(typename CopyAtom::ValLayoutDst{}));
        using AtomLayoutRef = decltype(select<1,0>(typename CopyAtom::ValLayoutRef{}));
        if constexpr (is_load) { // frgthr is the ref frgthr, need to retile it to [[src_atom_frg, rest_frg], [src_atom_thr, rest_thr]] -> coord
            auto src2ref = right_inverse(AtomLayoutRef{}).compose(AtomLayoutSrc{});
            // (src_atom_frg, src_atom_thr) -> (ref_atom_frg, ref_atom_thr)
            auto ref_frgthr_tiled = zipped_divide(FrgThr{}, make_shape(AtomNumVal{}, AtomNumThr{}));
#if 0
            print("ref_frgthr_tiled: "); print(ref_frgthr_tiled); printf("\n");
#endif
            // ((atom_frg, atom_thr), (rest_frg, rest_thr)) -> coord
            auto src_frgthr_tiled = ref_frgthr_tiled.compose(src2ref, _);
            // ((src_atom_frg, src_atom_thr), (rest_frg, rest_thr)) -> coord
            auto src_frgthr = coalesce(zip(src_frgthr_tiled), Shape<Shape<_1,_1>,_1>{});
            return src_frgthr;
        } else { // frgthr is the ref frgthr, need to retile it to [[dst_atom_frg, rest_frg], [dst_atom_thr, rest_thr]] -> coord
            auto dst2ref = right_inverse(AtomLayoutRef{}).compose(AtomLayoutDst{});
            // (dst_atom_frg, dst_atom_thr) -> (ref_atom_frg, ref_atom_thr)
            auto ref_frgthr_tiled = zipped_divide(FrgThr{}, make_shape(AtomNumVal{}, AtomNumThr{}));
            // ((atom_frg, atom_thr), (rest_frg, rest_thr)) -> coord
            auto dst_frgthr_tiled = ref_frgthr_tiled.compose(dst2ref, _);
            // ((dst_atom_frg, dst_atom_thr), (rest_frg, rest_thr)) -> coord
            auto dst_frgthr = coalesce(zip(dst_frgthr_tiled), Shape<Shape<_1,_1>,_1>{});
            return dst_frgthr;
        }
    }
}

// ----- SFINAE for retile_frgthr -----
template<bool is_load, typename FrgThr, typename CopyAtom>
constexpr bool can_retile_frgthr_v = cute::is_valid([](auto) -> 
    decltype(retile_frgthr<is_load, FrgThr, CopyAtom>()){})(int{});

//
// Safe copy checking functions that return false instead of static_assert
//

/**
 * Mirror of copy_unpack that returns false instead of static assertions
 */
template <class AnyCPYTraits,
          class SEngine, class SLayout,
          class DEngine, class DLayout>
constexpr
bool
can_copy_unpack(AnyCPYTraits            const&,
            Tensor<SEngine,SLayout>     const& src,
            Tensor<DEngine,DLayout>     const& dst)
{
    using CopyOp       = typename CPY_Op<AnyCPYTraits>::type;  
    using RegistersSrc = typename CopyOp::SRegisters;
    using RegistersDst = typename CopyOp::DRegisters;
    using RegTypeSrc   = typename remove_extent<RegistersSrc>::type;
    using RegTypeDst   = typename remove_extent<RegistersDst>::type;
    constexpr int RegNumSrc = extent<RegistersSrc>::value;
    constexpr int RegNumDst = extent<RegistersDst>::value;

    using rS_t = decltype(recast<RegTypeSrc>(src));
    using rD_t = decltype(recast<RegTypeDst>(dst));

#if 0
    printf("RegistersSrc = %s\n", typeid(RegistersSrc).name());
    printf("RegistersDst = %s\n", typeid(RegistersDst).name());
    printf("RegNumSrc = %d\n", RegNumSrc);
    printf("RegNumDst = %d\n", RegNumDst);
    printf("src = \n"); print(src); printf("\n");
    printf("dst = \n"); print(dst); printf("\n");
    printf("sizeof(RegTypeSrc) = %zu\n", sizeof(RegTypeSrc));
    printf("sizeof(RegTypeDst) = %zu\n", sizeof(RegTypeDst));
    print("rS_t: "); print(rS_t{}); printf("\n");
    print("rD_t: "); print(rD_t{}); printf("\n");
    printf("size(rS_t{}) = %d, RegNumSrc = %d\n", static_cast<int>(size(rS_t{})), RegNumSrc);
    printf("size(rD_t{}) = %d, RegNumDst = %d\n", static_cast<int>(size(rD_t{})), RegNumDst);
#endif
    if constexpr (size(rS_t{}) != Int<RegNumSrc>{}) {
    return false;
    }
    if constexpr (size(rD_t{}) != Int<RegNumDst>{}) {
    return false;
    }
    return true;
}

/**
 * Mirror of Copy_Atom::call that returns false instead of static assertions
 */
template <class... Args, class CopyInternalType,
          class SEngine, class SLayout,
          class DEngine, class DLayout>
constexpr
bool
can_call_copy_atom(Copy_Atom<Copy_Traits<Args...>, CopyInternalType> const& copy_atom,
                   Tensor<SEngine,SLayout> const& src,
                   Tensor<DEngine,DLayout> const& dst)
{
    using Traits = Copy_Traits<Args...>;
    // Check rank requirements (replaces static_assert)
    if constexpr (SLayout::rank != 1 || DLayout::rank != 1) {
        return false;
    } else {
        // Mirror the Copy_Atom::call logic exactly
        using CopyAtomType = Copy_Atom<Copy_Traits<Args...>, CopyInternalType>;
        constexpr int NumValSrc = CopyAtomType::NumValSrc;
        constexpr int NumValDst = CopyAtomType::NumValDst;

#if 0
        print("NumValSrc: "); print(NumValSrc); printf("\n");
        print("NumValDst: "); print(NumValDst); printf("\n");
        print("src: "); print(src); printf("\n");
        print("dst: "); print(dst); printf("\n");
#endif

        if constexpr (is_constant<NumValSrc, decltype(size(src))>::value ||
                    is_constant<NumValDst, decltype(size(dst))>::value) {
            // Dispatch to can_copy_unpack instead of copy_unpack
            return can_copy_unpack(Traits{}, src, dst);
        } else if constexpr (is_tuple<decltype(shape(src))>::value &&
                            is_tuple<decltype(shape(dst))>::value) {
            // Recurse on peeled tensors
            return can_call_copy_atom(copy_atom, tensor<0>(src), tensor<0>(dst));
        } else {
            return false; // "CopyAtom: Src/Dst partitioning does not match the instruction requirement."
        }
    }
}

/**
 * Mirror of copy function that returns false instead of static assertions
 */
template <class... CopyArgs,
          class SrcEngine, class SrcLayout,
          class DstEngine, class DstLayout>
constexpr
bool
can_copy(Copy_Atom<CopyArgs...> const& copy_atom,
         Tensor<SrcEngine, SrcLayout> const& src,
         Tensor<DstEngine, DstLayout> const& dst)
{
    // Check rank compatibility (replaces static_assert)
    if constexpr (SrcLayout::rank != DstLayout::rank) {
        return false;
    } else {
        if constexpr (SrcLayout::rank == 1) {
            // Dispatch the copy check
            return can_call_copy_atom(copy_atom, src, dst);
        } else {
            // Loop over all but the first mode
            constexpr int R = SrcLayout::rank;
            using src_v_t = decltype(group_modes<1,R>(src));
            using dst_v_t = decltype(group_modes<1,R>(dst));

#if 0
            print("SrcLayout: "); print(SrcLayout{}); printf("\n");
            print("DstLayout: "); print(DstLayout{}); printf("\n");
            print("src_v_t: "); print(src_v_t{}); printf("\n");
            print("dst_v_t: "); print(dst_v_t{}); printf("\n");
#endif

            if constexpr (is_static<decltype(shape(src_v_t{}))>::value && is_static<decltype(shape(dst_v_t{}))>::value) {
                // Check size compatibility (replaces CUTE_STATIC_ASSERT_V)
                constexpr bool sizes_match = decltype(size<1>(src_v_t{}) == size<1>(dst_v_t{}))::value;
                if constexpr (!sizes_match) {
                    return false;
                }

                // AutoFilter on the Rest-mode
                using dst_null_t = decltype(nullspace(layout<1>(dst_v_t{})));
                using dst_n_t = decltype(zipped_divide(dst_v_t{}, make_tile(shape<0>(dst_v_t{}), dst_null_t{})));
                using src_n_t = decltype(zipped_divide(src_v_t{}, make_tile(shape<0>(src_v_t{}), dst_null_t{})));

                // Check all the conditions that would be static assertions
                constexpr bool size1_match = decltype(size<1>(src_n_t{}) == size<1>(dst_n_t{}))::value;
                constexpr bool cosize_dst_ok = decltype(cosize<0,1>(dst_n_t{}.layout()) == Int<1>{})::value;
                constexpr bool cosize_src_ok = decltype(cosize<0,1>(src_n_t{}.layout()) == Int<1>{})::value;
                constexpr bool size10_dst_ok = decltype(size<1,0>(dst_n_t{}) == Int<1>{})::value;
                constexpr bool size10_src_ok = decltype(size<1,0>(src_n_t{}) == Int<1>{})::value;

                if constexpr (!size1_match || !cosize_dst_ok || !cosize_src_ok || !size10_dst_ok || !size10_src_ok) {
                    return false;
                }

                using dst_c_t = decltype(dst_n_t{}(make_coord(_,Int<0>{}),make_coord(Int<0>{},_)));
                using src_c_t = decltype(src_n_t{}(make_coord(_,Int<0>{}),make_coord(Int<0>{},_)));

                constexpr bool final_size_match = decltype(size<1>(src_c_t{}) == size<1>(dst_c_t{}))::value;
                constexpr bool final_shape0_dst = decltype(shape<0>(dst_c_t{}) == shape<0>(dst_v_t{}))::value;
                constexpr bool final_shape0_src = decltype(shape<0>(src_c_t{}) == shape<0>(src_v_t{}))::value;

                if constexpr (!final_size_match || !final_shape0_dst || !final_shape0_src) {
                    return false;
                }

#if 0
                print("src_c_t: "); print(src_c_t{}); printf("\n");
                print("dst_c_t: "); print(dst_c_t{}); printf("\n");
#endif
                using src_c_0_t = decltype(src_c_t{}(_,Int<0>{}));
                using dst_c_0_t = decltype(dst_c_t{}(_,Int<0>{}));
                return can_call_copy_atom(copy_atom, src_c_0_t{}, dst_c_0_t{});
            } else {
                using src_c_0_t = decltype(src_v_t{}(_,Int<0>{}));
                using dst_c_0_t = decltype(dst_v_t{}(_,Int<0>{}));
                return can_call_copy_atom(copy_atom, src_c_0_t{}, dst_c_0_t{});
            }
        }
    }
}

template <int MaxVecBits, class... Args,
          class SrcEngine, class SrcLayout,
          class DstEngine, class DstLayout>
CUTE_HOST_DEVICE constexpr
bool
can_copy(AutoVectorizingCopyWithAssumedAlignment<MaxVecBits> const&,
     Tensor<SrcEngine, SrcLayout>                        const& src,
     Tensor<DstEngine, DstLayout>                        const& dst)
{
  constexpr int common_elem = CUTE_STATIC_V(max_common_vector(src, dst));
  constexpr int align_bits  = CUTE_STATIC_V(gcd(max_alignment(src), max_alignment(dst), Int<MaxVecBits>{}));
  if constexpr (align_bits < MaxVecBits) {
    return false;
  }
  if constexpr (!is_integral<decltype(Int<common_elem>{} * sizeof_bits_v<typename SrcEngine::value_type>)>::value) {
    return false;
  } else {
    constexpr int vec_bits    = gcd(common_elem * sizeof_bits_v<typename SrcEngine::value_type>, align_bits);

    if constexpr (common_elem > 1 && ((vec_bits % 8) == 0)) {
        // If more than one element vectorizes to 8bits or more, then recast and copy
        using VecType = uint_bit_t<vec_bits>;
        // Preserve volatility
        using SrcVecType = conditional_t<is_volatile_v<typename SrcEngine::element_type>, VecType const volatile, VecType const>;
        using DstVecType = conditional_t<is_volatile_v<typename DstEngine::element_type>, VecType       volatile, VecType      >;

        // Recast
        using src_v_t = decltype(recast<SrcVecType>(src));
        using dst_v_t = decltype(recast<DstVecType>(dst));
#if 0
        print("SrcLayout: "); print(SrcLayout{}); printf("\n");
        print("DstLayout: "); print(DstLayout{}); printf("\n");
        print("common_elem: "); print(common_elem); printf("\n");
        print("align_bits: "); print(align_bits); printf("\n");
        print("vec_bits: "); print(vec_bits); printf("\n");
        print("src_v_t: "); print(src_v_t{}); printf("\n");
        print("dst_v_t: "); print(dst_v_t{}); printf("\n");
#endif
        if constexpr (is_same_v<decltype(shape(src_v_t{})), decltype(shape(dst_v_t{}))>) {
            return true;
        } else {
            return false;
        }
    } else {
        if constexpr (is_same_v<decltype(shape(SrcLayout{})), decltype(shape(DstLayout{}))>) {
            return true;
        } else {
            return false;
        }
    }
  }
}

// ----- LDSM atoms -----
template<typename _T>
using LDSM__ATOMS = std::conditional_t<sizeof(_T) == 2,
    std::tuple<
        Copy_Atom<SM75_U16x8_LDSM_T, _T>,
        Copy_Atom<SM75_U16x4_LDSM_T, _T>,
        Copy_Atom<SM75_U16x2_LDSM_T, _T>,
        Copy_Atom<SM75_U32x4_LDSM_N, _T>,
        Copy_Atom<SM75_U32x2_LDSM_N, _T>,
        Copy_Atom<SM75_U32x1_LDSM_N, _T>
    >,
    std::tuple<>
>;

// ----- Vectorizing copy atoms -----
using VECTORIZING__ATOMS = std::tuple<
    AutoVectorizingCopyWithAssumedAlignment<128>,
    AutoVectorizingCopyWithAssumedAlignment<64>,
    AutoVectorizingCopyWithAssumedAlignment<32>,
    AutoVectorizingCopyWithAssumedAlignment<16>,
>;

// ----- Load For Gmem -----
using LOAD_GMEM_ATOMS = VECTORIZING__ATOMS;

// ----- Load For Smem -----
template<typename _T>
using LOAD_SMEM_ATOMS = decltype(merge(LDSM__ATOMS<_T>{}, VECTORIZING__ATOMS{}));

// ----- Store For Gmem -----
using STORE_GMEM_ATOMS = VECTORIZING__ATOMS;

// ----- Store For Smem -----
// TODO: add stsm here
using STORE_SMEM_ATOMS = VECTORIZING__ATOMS;

// ----- Store Atoms -----
template<bool is_gmem>
using STORE_ATOMS = std::conditional_t<is_gmem, STORE_GMEM_ATOMS, STORE_SMEM_ATOMS>;

// ----- Load Atoms -----
template<bool is_gmem, typename T>
using LOAD_ATOMS = std::conditional_t<is_gmem, LOAD_GMEM_ATOMS, LOAD_SMEM_ATOMS<T>>;

// ----- All atoms -----
template<bool is_load, bool is_gmem, typename T>
using ALL_ATOMS = std::conditional_t<is_load, LOAD_ATOMS<is_gmem, T>, STORE_ATOMS<is_gmem>>;

/**
 * @brief Check if a given atom is compatible with a given frgthr and a tile
 * @tparam is_load   Whether to load or store
 * @tparam is_gmem   Whether it's gmem or smem
 * @tparam T         The element type of the data being copied
 * @tparam CopyAtom  The copy atom to check
 * @tparam FrgThr    The layout of the frgthr
 * @tparam Tile      The tile layout to use
 * @tparam Frg       The layout of the frg
 * @return Whether the atom is compatible with the frgthr and tile
 */
template<bool is_load, bool is_gmem, typename T, typename CopyAtom, typename FrgThr, typename Tile, typename Frg=decltype(make_layout(get<0>(shape(FrgThr{}))))>
constexpr bool is_compatible() {
    if constexpr (can_retile_frgthr_v<is_load, FrgThr, CopyAtom>) {
        using retiled_frgthr_t = decltype(retile_frgthr<is_load, FrgThr, CopyAtom>());
        // Here we make assumptions about the frg layout
        using DummyFrg = decltype(make_tensor<T>(Frg{}));
        using DummyTile = std::conditional_t<is_gmem,
            decltype(make_tensor(make_gmem_ptr(static_cast<T*>(nullptr)), Tile{})),
            decltype(make_tensor(make_smem_ptr(static_cast<T*>(nullptr)), Tile{}))>;
        
        if constexpr (is_load) { // retiled_frgthr is the src frgthr, need to check everything vectorizes correctly
            if constexpr (!any_of(LOAD_ATOMS<is_gmem, T>{}, [&](auto atom) {
                return is_same_v<decltype(atom), CopyAtom>;
            })) {
                return false;
            } else {
                using src_frg_t = decltype(slice_rest(DummyTile{}, retiled_frgthr_t{}, Int<0>{}));
                using dst_frg_t = decltype(retile_frg<is_load, CopyAtom, FrgThr>(DummyFrg{}));
#if 0
                print("DummyTile: "); print(DummyTile{}); printf("\n");
                print("DummyFrg: "); print(DummyFrg{}); printf("\n");
                print("retiled_frgthr_t: "); print(retiled_frgthr_t{}); printf("\n");
                print("src_frg_t: "); print(src_frg_t{}); printf("\n");
                print("dst_frg_t: "); print(dst_frg_t{}); printf("\n");
#endif
                // Use our safe can_copy function instead of cute::is_valid with copy
                return can_copy(CopyAtom{}, src_frg_t{}, dst_frg_t{});
            }
        } else { // retiled_frgthr is the dst frgthr
            if constexpr (!any_of(STORE_ATOMS<is_gmem>{}, [&](auto atom) {
                return is_same_v<decltype(atom), CopyAtom>;
            })) {
                return false;
            } else {
                using src_frg_t = decltype(retile_frg<is_load, CopyAtom, FrgThr>(DummyFrg{}));
                using dst_frg_t = decltype(slice_rest(DummyTile{}, retiled_frgthr_t{}, Int<0>{}));
#if 0
                print("DummyTile: "); print(DummyTile{}); printf("\n");
                print("DummyFrg: "); print(DummyFrg{}); printf("\n");
                print("retiled_frgthr_t: "); print(retiled_frgthr_t{}); printf("\n");
                print("src_frg_t: "); print(src_frg_t{}); printf("\n");
                print("dst_frg_t: "); print(dst_frg_t{}); printf("\n");
#endif
                // Use our safe can_copy function instead of cute::is_valid with copy
                return can_copy(CopyAtom{}, src_frg_t{}, dst_frg_t{});
            }
        }
    } else {
        return false;
    }
}

/**
 * @brief Infer the copy atom based on the tile layout and frgthr. It goes through a fixed list of atoms and returns the first one that is compatible.
 * @tparam is_load   Whether to load or store
 * @tparam is_gmem   Whether it's gmem or smem
 * @tparam T         The element type of the data being copied
 * @tparam FrgThr    The frgthr to use
 * @tparam Tile      The tile layout to use
 * @return The copy atom to use
 */
template<bool is_load, bool is_gmem, typename T, typename FrgThr, typename Tile, typename Frg=decltype(make_layout(get<0>(shape(FrgThr{}))))>
CUTE_HOST_DEVICE constexpr auto infer_copy_atom() {
    constexpr auto idx = find_if(ALL_ATOMS<is_load, is_gmem, T>{}, [&](auto atom) {
        if constexpr (is_compatible<is_load, is_gmem, T, decltype(atom), FrgThr, Tile, Frg>()) {
            return std::true_type{};
        } else {
            return std::false_type{};
        }
    });
    if constexpr (idx >= 0 && idx < tuple_size<ALL_ATOMS<is_load, is_gmem, T>>::value) {
        return get<idx>(ALL_ATOMS<is_load, is_gmem, T>{});
    } else {
        return DefaultCopy{};
    }
}


/**
 * @brief Infer the frgthr that has minimum bank conflicts when interacting with the tile (basically a strided frgthr)
 * @tparam thread_num  The number of threads intended to use
 * @tparam T           The element type of the data being copied
 * @tparam STile       The smem tile layout
 * @return The recommended frgthr
 */
template<int thread_num, typename T, typename Tile>
CUTE_HOST_DEVICE constexpr auto infer_frgthr() {
    using Inverse = decltype(left_inverse(Tile{})); // coord -> logical coord
    constexpr int bank_capacity = 128; // 128 bytes distributed across 32 banks

    constexpr int min_total = static_min(bank_capacity / sizeof(T), size(Tile{})); // minimum number of elements accessed per round
    constexpr int v_size = static_max(min_total / thread_num, 1); // v_size
    constexpr int threads = static_min(size(Tile{}) / v_size, thread_num); // actual number of threads
    constexpr int v_rest = static_max(size(Tile{}) / (v_size * threads), 1); // rest_size

    using Frgthr_1 = decltype(make_layout(Shape<Shape<Int<v_size>, Int<v_rest>>, Shape<Int<threads>>>{},
                                          Stride<Stride<_1, Int<v_size * threads>>, Stride<Int<v_size>>>{}));
    using Frgthr_2 = decltype(Inverse{}.compose(Frgthr_1{}));
    return Frgthr_2{};
}


/**
 * @brief A copy config that encompasses multiple copy atoms and desired frgThr
 * @tparam T_           The element type of the data being copied
 * @tparam FrgThr_      The logical frgThr to use. It doesn't need to have the first mode equal in size to the copy atom's NumValDst, as long as it can be retiled to be compatible with the copy atom.
 * @tparam LoadAtom_    The copy atom to use for loading
 * @tparam StoreAtom_   The copy atom to use for storing
 * @tparam LoadFrgThr_  The frgThr to use for loading, should be compatible with LoadAtom_
 * @tparam StoreFrgThr_ The frgThr to use for storing, should be compatible with StoreAtom_
 */
template <typename T_, typename FrgThr_, typename Frg_, typename LoadAtom_, typename StoreAtom_, typename LoadFrgThr_, typename StoreFrgThr_>
struct FrgCopyCfg {
    using T = T_;
    using FrgThr = FrgThr_;
    using Frg = Frg_;
    using LoadAtom = LoadAtom_;
    using StoreAtom = StoreAtom_;
    using LoadFrgThr = LoadFrgThr_;
    using StoreFrgThr = StoreFrgThr_;
    static constexpr int thread_num = size<1>(FrgThr{});

    Frg frg;
    FrgThr frgthr; // logical frgthr: [logical_frg, Thr] -> logical coord
    LoadAtom load_atom;
    StoreAtom store_atom;
    LoadFrgThr load_frgthr; // frgThr compatible with load_atom: [[V_src, Rest...], Thr] -> src coord
    StoreFrgThr store_frgthr; // frgThr compatible with store_atom: [[V_dst, Rest...], Thr] -> dst coord
};

/**
 * @brief Make a frg copy config with load and store atoms
 * @tparam T           The element type of the data being copied
 * @tparam FrgThr      The frgThr to use
 * @tparam LoadAtom    The copy atom to use for loading, default to DefaultCopy
 * @tparam StoreAtom   The copy atom to use for storing, default to DefaultCopy
 * @tparam Frg         The frg to use, default to make_layout(get<0>(shape(FrgThr{})))
 */
template<typename T, typename FrgThr, typename LoadAtom=DefaultCopy, typename StoreAtom=DefaultCopy, typename Frg=decltype(make_layout(get<0>(shape(FrgThr{}))))>
CUTE_HOST_DEVICE constexpr auto make_FrgCopyCfg() {
    using LoadFrgThr = decltype(retile_frgthr</*is_load*/true, FrgThr, LoadAtom>());
    using StoreFrgThr = decltype(retile_frgthr</*is_load*/false, FrgThr, StoreAtom>());
    return FrgCopyCfg<T, FrgThr, Frg, LoadAtom, StoreAtom, LoadFrgThr, StoreFrgThr>{Frg{}, FrgThr{}, LoadAtom{}, StoreAtom{}, LoadFrgThr{}, StoreFrgThr{}};
}

/**
 * @brief Make a frg copy config based on STile, atoms are inferred as the user doesn't care about them
 * @tparam T           The element type of the data being copied
 * @tparam STile       The smem tile layout
 * @tparam FrgThr      The frgThr
 * @tparam Frg         The frg to use, default to make_layout(get<0>(shape(FrgThr{})))
 * @return The frg copy config
 */
template<typename T, typename STile, typename FrgThr, typename Frg=decltype(make_layout(get<0>(shape(FrgThr{}))))>
CUTE_HOST_DEVICE constexpr auto make_smem_FrgCopyCfg() {
    using LoadAtom = decltype(infer_copy_atom</*is_load*/true, /*is_gmem*/false, T, FrgThr, STile, Frg>());
    using StoreAtom = decltype(infer_copy_atom</*is_load*/false, /*is_gmem*/false, T, FrgThr, STile, Frg>());
    return make_FrgCopyCfg<T, FrgThr, LoadAtom, StoreAtom, Frg>();
}

/**
 * @brief Make a frg copy config based on GTile, atoms are inferred as the user doesn't care about them
 * @tparam T           The element type of the data being copied
 * @tparam GTile       The gmem tile layout
 * @tparam FrgThr      The frgThr
 * @tparam Frg         The frg to use, default to make_layout(get<0>(shape(FrgThr{})))
 * @return The frg copy config
 */
template<typename T, typename GTile, typename FrgThr, typename Frg=decltype(make_layout(get<0>(shape(FrgThr{}))))>
CUTE_HOST_DEVICE constexpr auto make_gmem_FrgCopyCfg() {
    using LoadAtom = decltype(infer_copy_atom</*is_load*/true, /*is_gmem*/true, T, FrgThr, GTile, Frg>());
    using StoreAtom = decltype(infer_copy_atom</*is_load*/false, /*is_gmem*/true, T, FrgThr, GTile, Frg>());
    return make_FrgCopyCfg<T, FrgThr, LoadAtom, StoreAtom, Frg>();
}

/**
 * @brief Make a frg copy config based on STile alone, the atoms and frgthr are all inferred
 * @tparam T           The element type of the data being copied
 * @tparam STile       The smem tile layout
 * @tparam thread_num  The number of threads intended to use, note that it's not guaranteed to be the same as the thread_num in the frgthr
 */
template<typename T, typename STile, int thread_num>
CUTE_HOST_DEVICE constexpr auto make_smem_FrgCopyCfg() {
    using FrgThr = decltype(infer_frgthr<thread_num, T, STile>());
    return make_smem_FrgCopyCfg<T, STile, FrgThr>();
}

/**
 * @brief Make a frg copy config based on GTile alone, the atoms and frgthr are all inferred
 * @tparam T           The element type of the data being copied
 * @tparam GTile       The gmem tile layout
 * @tparam thread_num  The number of threads intended to use, note that it's not guaranteed to be the same as the thread_num in the frgthr
 */
template<typename T, typename GTile, int thread_num>
CUTE_HOST_DEVICE constexpr auto make_gmem_FrgCopyCfg() {
    using FrgThr = decltype(infer_frgthr<thread_num, T, GTile>());
    return make_gmem_FrgCopyCfg<T, GTile, FrgThr>();
}

/**
 * @brief Load from source memory tile to fragment, in-place
 * @tparam Cfg       The copy config, should be a FrgCopyCfg
 * @tparam S_tile    The source memory tile (can be in smem or gmem)
 * @tparam fragment  The fragment to load to, of layout cfg.frg
 */
CUTE_DEVICE auto load(auto &cfg, auto& S_tile, auto& fragment) {
    if (threadIdx.x < cfg.thread_num) {
        copy(cfg.load_atom, slice_rest(S_tile, cfg.load_frgthr, threadIdx.x), retile_frg</*is_load*/true, decltype(cfg.load_atom), decltype(cfg.frgthr)>(fragment));
    }
}

/**
 * @brief Load from source memory tile to fragment, out of place
 * @tparam Cfg       The copy config, should be a FrgCopyCfg
 * @tparam S_tile    The source memory tile (can be in smem or gmem)
 * @return The loaded fragment, of layout cfg.frg
 */
CUTE_DEVICE auto load(auto &cfg, auto& S_tile) {
    using T = std::decay_t<decltype(cfg)>::T;
    auto fragment = make_tensor<T>(cfg.frg);
    load(cfg, S_tile, fragment);
    return fragment;
}

/**
 * @brief Store from fragment to destination memory tile
 * @tparam Cfg       The copy config, should be a FrgCopyCfg
 * @tparam fragment  The fragment to store from, of layout cfg.frg
 * @tparam D_tile    The destination memory tile (can be in smem or gmem)
 */
CUTE_DEVICE auto store(auto &cfg, auto& fragment, auto& D_tile) {
    if (threadIdx.x < cfg.thread_num) {
        copy(cfg.store_atom, retile_frg</*is_load*/false, decltype(cfg.store_atom), decltype(cfg.frgthr)>(fragment), slice_rest(D_tile, cfg.store_frgthr, threadIdx.x));
    }
}


} // namespace vidrial