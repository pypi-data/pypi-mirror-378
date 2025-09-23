#pragma once
#include <cute/tensor.hpp>
#include <iostream>
#include "../cuda_utils/tprod.cuh"
#include "../cuda_utils/ABC_utils.cuh"
#include "../cuda_utils/allocator.cuh"
#include "../copy/copy_cfg.cuh"
#include "../cuda_utils/perf_cfg.cuh"
#include "../cuda_utils/swizzle_cfg.cuh"
#include "../cuda_utils/frg_copy.cuh"
namespace vidrial {

/*
 * MmaMNKCoords is a helper class that slices a tensor into tiles.
 * It is used to slice the A, B, and C tensors into tiles.
 * It is also used to step along the M, N, K, and P dimensions.
 * It is also used to check if the current coords have reached the end of the tensor.
 * It works with slabs of data that have a batch dimension at the end (eg A is [M,K,P])
 * The sliced tiles do not have a batch dimension.
 */
template<typename MNKTileShape>
struct MmaMNKCoords {
    static_assert(rank(MNKTileShape{}) == 3, "MNKTileShape must be 3D");
    static constexpr MNKTileShape MNK_tile_shape{};
    tuple<int,int,int,int> MNKP_coords {0, 0, 0, 0};
    CUTE_HOST_DEVICE MmaMNKCoords(MNKTileShape MNK_tile_shape) : MNKP_coords(0,0,0,0) {}
    // get the current coords
    CUTE_HOST_DEVICE auto M_coord() { return get<0>(MNKP_coords); }
    CUTE_HOST_DEVICE auto N_coord() { return get<1>(MNKP_coords); }
    CUTE_HOST_DEVICE auto K_coord() { return get<2>(MNKP_coords); }
    CUTE_HOST_DEVICE auto P_coord() { return get<3>(MNKP_coords); }
    // Use the current coords to slice A,B,C tiles 
    template<auto... Is>
    CUTE_HOST_DEVICE auto _slice_tile(auto& tensor) {
        auto tile_shape = make_tuple(get<Is>(MNK_tile_shape)..., _1{});
        auto tiled_tensor = zipped_divide(tensor, tile_shape);
        auto tile_with_batch = slice_rest(tiled_tensor, select<Is...,3>(MNKP_coords));
        if constexpr (sizeof...(Is) == 2)
            return tile_with_batch(_,_,_0{}); // slice out the batch dimension (of size 1)
        else
            return tile_with_batch(_,_0{}); // slice out the batch dimension (of size 1)
    }
    CUTE_HOST_DEVICE auto slice_A_tile(auto& A_tensor) { return _slice_tile<0,2>(A_tensor); } // MKP
    CUTE_HOST_DEVICE auto slice_B_tile(auto& B_tensor) { return _slice_tile<1,2>(B_tensor); } // NKP
    CUTE_HOST_DEVICE auto slice_C_tile(auto& C_tensor) { return _slice_tile<0,1>(C_tensor); } // MNP
    CUTE_HOST_DEVICE auto slice_L_tile(auto& L_tensor) { return _slice_tile<0>(L_tensor); } // MP
    // Step the coordinates along any dimension
    CUTE_HOST_DEVICE void step_M(int step = 1) { get<0>(MNKP_coords) += step; }
    CUTE_HOST_DEVICE void step_N(int step = 1) { get<1>(MNKP_coords) += step; }
    CUTE_HOST_DEVICE void step_K(int step = 1) { get<2>(MNKP_coords) += step; }
    CUTE_HOST_DEVICE void step_P(int step = 1) { get<3>(MNKP_coords) += step; }
    // Check if the current coords have reached the end of the tensor
    CUTE_HOST_DEVICE bool valid_M_tile(int M) { return get<0>(MNKP_coords) * get<0>(MNKTileShape{}) < M; }
    CUTE_HOST_DEVICE bool valid_N_tile(int N) { return get<1>(MNKP_coords) * get<1>(MNKTileShape{}) < N; }
    CUTE_HOST_DEVICE bool valid_K_tile(int K) { return get<2>(MNKP_coords) * get<2>(MNKTileShape{}) < K; }
    CUTE_HOST_DEVICE bool valid_P_tile(int P) { return get<3>(MNKP_coords) < P; }
    // Reset the coordinates 0
    CUTE_HOST_DEVICE void reset() { MNKP_coords = make_tuple(0,0,0,0); }
    CUTE_HOST_DEVICE void reset_M(int idx=0) { get<0>(MNKP_coords) = idx; }
    CUTE_HOST_DEVICE void reset_N(int idx=0) { get<1>(MNKP_coords) = idx; }
    CUTE_HOST_DEVICE void reset_K(int idx=0) { get<2>(MNKP_coords) = idx; }
    CUTE_HOST_DEVICE void reset_P(int idx=0) { get<3>(MNKP_coords) = idx; }
    CUTE_HOST_DEVICE auto M_tile() { return get<0>(MNKTileShape{});}
    CUTE_HOST_DEVICE auto N_tile() { return get<1>(MNKTileShape{});}
    CUTE_HOST_DEVICE auto K_tile() { return get<2>(MNKTileShape{});}
};



template<typename _T, typename _ABC_t, typename _MmaAtom,
         typename _MNKTileShape, typename _MNKAtomPlacement, 
         typename _GSlab, typename _PerfCfg = DefaultPerfCfg, typename _PermutationMNK = Tile<Underscore,Underscore,Underscore>>
struct ABC_MmaCfg {
    using T = _T;
    using ABC_t = _ABC_t;
    using MmaAtom = _MmaAtom;
    using MNKAtomPlacement = _MNKAtomPlacement;
    using GSlab = _GSlab;
    using PerfCfg = _PerfCfg;
    static constexpr PerfCfg perf{};
    GSlab gSlab{};
    using TileShape = decltype(ABC_get_MNK(ABC_t{}, _MNKTileShape{}));
    static_assert(rank(TileShape{}) == Int<2>{}, "TileShape must be 2D");
    static_assert(evenly_divides(LayoutShape(GSlab){}, TileShape{}), "TileShape must divide the GSlab");
    TileShape tileShape;
    // ---------- MMA Op ----------
    MmaAtom mma_Atom;
    using AtomShape_t = decltype(ABC_get_MNK(ABC_t{}, typename MmaAtom::Shape_MNK{}));
    AtomShape_t AtomShape{};
    static_assert(get<2>(MNKAtomPlacement{}) == _1{}, "AtomPlacement K != 1 is tricky to implement. You need to accumulate the C registers. Remove assert only if your kernel supposrts it.");
    using AtomPlacement = decltype(ABC_get_MNK(ABC_t{}, MNKAtomPlacement{}));
    using VMNKThreads = decltype(tiled_product(typename MmaAtom::ThrID{}, Layout<MNKAtomPlacement>{}));
    static constexpr VMNKThreads Threads{};
    static constexpr int thread_num = size(Threads);
    using OpShape_t = decltype(elem_scale(AtomShape_t{}, AtomPlacement{}));
    static_assert(evenly_divides(TileShape{}, OpShape_t{}), "OpShape must divide the tileShape");
    static auto get_MmaOpFrgThr() {
        /* The Mma Op might use multiple atom placement (for CTAs with more threads than the atom) */
        auto AtomTV = ABC_get_TV_layout(ABC_t{}, MmaAtom{});
        auto AtomFrgThr = select<1,0>(AtomTV); // FrgThr layouts is just the transpose of ThrVal layouts
        auto OpLayoutMN = zipped_divide(make_layout(OpShape_t{}), AtomShape_t{});
        auto RestThreads = ABC_project_MNK(ABC_t{}, MNKAtomPlacement{});
        auto OpLayout_FT_MN = OpLayoutMN.compose(AtomFrgThr, RestThreads);
        auto OpLayoutF = get<0,0>(OpLayout_FT_MN);
        auto OpLayoutT = append(get<0,1>(OpLayout_FT_MN), get<1>(OpLayout_FT_MN));
        auto OpLayoutFT = make_layout(OpLayoutF, OpLayoutT);
        return OpLayoutFT;
    }
    using MmaOpFrgThr_t = decltype(get_MmaOpFrgThr());
    static auto get_MmaFrgThr() {
        /* The Tile Shape might be larger than the OpShape. The mma_FrgThr needs to tile*/
        auto tileLayout = make_layout(TileShape{});
        auto OpMN_RestMN= zipped_divide(tileLayout, OpShape_t{});
        auto OpFrgThr_RestMN = OpMN_RestMN.compose(MmaOpFrgThr_t{}, _); //  ((frg_v, tid), (tile_m, tile_n))
        auto OpFrgRestMN = prepend(get<1>(OpFrgThr_RestMN), get<0,0>(OpFrgThr_RestMN)); // (frg_v, tile_m, tile_n)
        auto OpFrgThr = make_layout(OpFrgRestMN, get<0,1>(OpFrgThr_RestMN)); // ((frg_v, tile_m, tile_n), tid)
        return OpFrgThr;
    }
    using MmaFrgThr = decltype(get_MmaFrgThr());
    using MmaFrg = decltype(make_layout(get<0>(MmaFrgThr{}.shape())));
    MmaFrgThr mma_FrgThr{};
    MmaFrg mma_Frg{};
    // ---------- G2S Copy ----------
    using TileCopy = decltype(make_TileCopyCfg<T, thread_num>(TileShape{}, GSlab{}));
    using STile_ = typename TileCopy::STile;
    // ---------- Swizzle ----------
    using UnswizzledSTile = STile_;
    using SwizzleCfg_t = decltype(make_swizzle_cfg<TileCopy, STile_, MmaFrgThr, perf.swizzle>(STile_{}, MmaFrgThr{}));
    using STile = std::conditional_t<
        std::is_same_v<ABC_t, C_t>,
        STile_, // no swizzling for C
        typename SwizzleCfg_t::SwizzledSTile
    >;
    using Permutation = decltype(ABC_get_MNK(ABC_t{}, _PermutationMNK{}));
    // ---------- Frg Copy ----------
    using FrgCopyCfg = decltype(make_smem_FrgCopyCfg<T, STile, MmaFrgThr, MmaFrg>());
    
    FrgCopyCfg frg_copy{};
    Permutation perm{};
    SwizzleCfg_t swizzle_cfg{};
    UnswizzledSTile unswizzled_sTile{};
    STile sTile{};
    TileCopy tile_copy;
    CUTE_HOST_DEVICE auto make_mma_frg() const {
        using FrgType = typename ABC_FrgType<ABC_t, MmaAtom>::type;
        return make_tensor<FrgType>(mma_Frg);
    }
};

template<typename _T, typename _MmaAtom,
         typename _MNKTileShape, typename _MNKAtomPlacement, 
         typename GASlab, typename GBSlab, typename GCSlab, typename _PerfCfg = DefaultPerfCfg, typename _PermutationMNK = Tile<Underscore,Underscore,Underscore>>
struct MmaKernelCfg {
    using T = _T;
    using MmaAtom = _MmaAtom;
    using MNKTileShape = _MNKTileShape;
    // using MNKPTileShape = decltype(append(MNKTileShape{}, _1{}));
    static_assert(is_static_v<MNKTileShape>, "MNKTileShape must be static");
    static constexpr MNKTileShape MNK_tile_shape{};
    // static constexpr MNKPTileShape MNKP_tile_shape{};
    MmaAtom mma_Atom;
    using MNKAtomPlacement = _MNKAtomPlacement;
    using ACfg = ABC_MmaCfg<T, A_t, MmaAtom, MNKTileShape, _MNKAtomPlacement, GASlab, _PerfCfg, _PermutationMNK>;
    using BCfg = ABC_MmaCfg<T, B_t, MmaAtom, MNKTileShape, _MNKAtomPlacement, GBSlab, _PerfCfg, _PermutationMNK>;
    using CCfg = ABC_MmaCfg<T, C_t, MmaAtom, MNKTileShape, _MNKAtomPlacement, GCSlab, _PerfCfg, _PermutationMNK>;   
    using PerfCfg = _PerfCfg;
    static constexpr PerfCfg perf{};
    ACfg A;
    BCfg B;
    CCfg C;
    using FrgTypeA = typename MmaAtom::FrgTypeA;
    using FrgTypeB = typename MmaAtom::FrgTypeB;
    using FrgTypeC = typename MmaAtom::FrgTypeC;
    typename ACfg::VMNKThreads Threads{};
    static constexpr int thread_num = ACfg{}.thread_num;
    static constexpr int M = size<0>(typename ACfg::GSlab{});
    static constexpr int N = size<0>(typename BCfg::GSlab{});
    static constexpr int K = size<1>(typename ACfg::GSlab{});
    static constexpr int P = size<2>(typename ACfg::GSlab{});
    static constexpr int M_tile = size<0>(typename ACfg::TileShape{});
    static constexpr int N_tile = size<0>(typename BCfg::TileShape{});
    static constexpr int K_tile = size<1>(typename ACfg::TileShape{});
    static constexpr int M_tile_num = M/M_tile;
    static constexpr int N_tile_num = N/N_tile;
    static constexpr int K_tile_num = K/K_tile;
    static constexpr int P_tile_num = P;

    static int smem_size() {
        using AT = typename ACfg::T;
        using BT = typename BCfg::T;
        using CT = typename CCfg::T;
        using A_STile = typename ACfg::STile;
        using B_STile = typename BCfg::STile;
        using C_STile = typename CCfg::STile;
        int ab_smem_size = Allocator<16>::total<AT, BT>(size(A_STile{}) * perf.smempipe, size(B_STile{}) * perf.smempipe);
        int c_smem_size = Allocator<16>::total<CT>(size(C_STile{}));
        return static_max(ab_smem_size, c_smem_size);
    }
};


template<typename _T, typename _MmaAtom,
typename _MNKTileShape, typename _MNKAtomPlacement, 
typename GASlab, typename GBSlab, typename GCSlab, typename _PerfCfg, typename _PermutationMNK>
void print_cfg(MmaKernelCfg<_T, _MmaAtom, _MNKTileShape, _MNKAtomPlacement, GASlab, GBSlab, GCSlab, _PerfCfg, _PermutationMNK> const& cfg, std::string prefix = "") {
    std::cout << "MmaKernelCfg:\n";
    std::cout << prefix << "  mma_Atom: "; print(cfg.mma_Atom); std::cout << "\n";
    std::cout << prefix << "  MNKAtomPlacement: "; print(_MNKAtomPlacement{}); std::cout << "\n";
    std::cout << prefix << "  MNK_tile_shape: "; print(cfg.MNK_tile_shape); std::cout << "\n";
    std::cout << prefix << "  A.tile_copy: "; print_cfg(cfg.A.tile_copy, prefix + "  A.tile_copy: "); std::cout << "\n";
    std::cout << prefix << "  B.tile_copy: "; print_cfg(cfg.B.tile_copy, prefix + "  B.tile_copy: "); std::cout << "\n";
    std::cout << prefix << "  C.tile_copy: "; print_cfg(cfg.C.tile_copy, prefix + "  C.tile_copy: "); std::cout << "\n";
    std::cout << prefix << "  A.mma_FrgThr: "; print(cfg.A.mma_FrgThr); std::cout << "\n";
    std::cout << prefix << "  B.mma_FrgThr: "; print(cfg.B.mma_FrgThr); std::cout << "\n";
    std::cout << prefix << "  C.mma_FrgThr: "; print(cfg.C.mma_FrgThr); std::cout << "\n";
    std::cout << prefix << "  A.sTile: "; print(cfg.A.sTile); std::cout << "\n";
    std::cout << prefix << "  B.sTile: "; print(cfg.B.sTile); std::cout << "\n";
    std::cout << prefix << "  C.sTile: "; print(cfg.C.sTile); std::cout << "\n";
    std::cout << prefix << "  perf: "; print_cfg(cfg.perf, prefix + "  perf: "); std::cout << "\n";
}

// -------------- Make MmaCfg --------------

template<typename T>
auto default_MMA_atom() {
    if constexpr(std::is_same_v<T, float>) {
        return MMA_Atom<SM80_16x8x8_F32TF32TF32F32_TN>{};
    } else if constexpr(std::is_same_v<T, half_t>) {
        return MMA_Atom<SM80_16x8x8_F32F16F16F32_TN>{};
    } else if constexpr(std::is_same_v<T, bfloat16_t>) {
        return MMA_Atom<SM80_16x8x8_F32BF16BF16F32_TN>{};
    } else {
        return UniversalFMA<T>{};
    }
}
// TODO: make a proper automatic system to pick MMA instructions, tileShapes and atom placements
template<typename T, typename _PerfCfg=DefaultPerfCfg, typename Atom, typename MNKAtomPlacement, typename MNKTileShape, 
         typename ASlab, typename BSlab, typename CSlab>
auto make_mma_cfg(MNKTileShape, Atom, MNKAtomPlacement, ASlab, BSlab, CSlab) {
    return MmaKernelCfg<T, Atom, MNKTileShape, MNKAtomPlacement, ASlab, BSlab, CSlab, _PerfCfg>{};
}
template<typename T, typename _PerfCfg=DefaultPerfCfg, typename Atom, typename MNKTileShape, 
         typename ASlab, typename BSlab, typename CSlab>
auto make_mma_cfg(MNKTileShape, Atom, ASlab, BSlab, CSlab) {
    using MNKAtomPlacement = Shape<_1,_1,_1>;
    return MmaKernelCfg<T, Atom, MNKTileShape, MNKAtomPlacement, ASlab, BSlab, CSlab, _PerfCfg>{};
}
template<typename T, typename _PerfCfg=DefaultPerfCfg, typename MNKTileShape, 
         typename ASlab, typename BSlab, typename CSlab>
auto make_mma_cfg(MNKTileShape, ASlab, BSlab, CSlab) {
    auto atom = default_MMA_atom<T>();
    return make_mma_cfg<T, _PerfCfg>(MNKTileShape{}, atom, ASlab{}, BSlab{}, CSlab{});
}
template<typename T, typename MNKAtomPlacement=Shape<_1,_1,_1>, typename _PerfCfg=DefaultPerfCfg,
         typename ASlab, typename BSlab, typename CSlab>
auto make_mma_cfg(ASlab, BSlab, CSlab) {
    using MNKTileShape = Shape<_16,_16,_16>;
    return make_mma_cfg<T, _PerfCfg>(MNKTileShape{}, ASlab{}, BSlab{}, CSlab{});
}

} // namespace vidrial