#include "../sympow_bwd/sympow_bwd.cuh"

namespace vidrial {

/* Cfg where the expanded object is C along the M dimension
X = c
*/
template<typename _T, int _pow, typename MmaAtom, typename MNKAtomPlacement, typename _MNKPSlabShape, typename MNKTileShape,
         int _d, int _d_tile, typename _GASlab, typename _GBSlab, typename _GcSlab, typename SmemAccI, typename _PerfCfg = DefaultPerfCfg>
struct SympowCMmaCfg {
    using T = _T;
    using acc_T = float;
    static constexpr int pow = _pow;
    static constexpr int d = _d;
    static constexpr int d_tile = _d_tile;
    using PerfCfg = _PerfCfg;
    static constexpr PerfCfg perf{};
    using GASlab = decltype(static_tree_cast<int64_t>(_GASlab{}));
    using GBSlab = decltype(static_tree_cast<int64_t>(_GBSlab{}));
    using GcSlab = decltype(static_tree_cast<int64_t>(_GcSlab{}));
    using MNKAtomLayout = Layout<Shape<_1,_1,_1>>; // generic layouts not implemented
    using MNKPSlabShape = decltype(static_tree_cast<int64_t>(_MNKPSlabShape{}));
    static constexpr long M=size<0>(MNKPSlabShape{}),N=size<1>(MNKPSlabShape{}),K=size<2>(MNKPSlabShape{}),P=size<3>(MNKPSlabShape{}); 
    static constexpr long M_tile=get<0>(MNKTileShape{}),N_tile=get<1>(MNKTileShape{}),K_tile=get<2>(MNKTileShape{}); 
    static constexpr int D = get<0>(MNKPSlabShape{});
    static constexpr int D_tile = static_pow<pow>(d_tile);
    static_assert(D == sympow_dim<pow, d, d_tile>());
    static_assert(D_tile == get<0>(MNKTileShape{}), "D_tile mismatch with M_tile");
    static constexpr int D_tile_num = sympow_dim<pow, d/d_tile>();
    using CSlabShape = decltype(ABC_get_MNKP(C_t{}, MNKPSlabShape{}));
    using CTileShape = decltype(ABC_get_MNK(C_t{}, MNKTileShape{}));
    using cSlabShape = Shape<Int<d>,Int<N>,Int<P>>; // similar to XSlabShape = [d,[N,P]]
    using XSlabShape = Shape<Int<d>,Shape<Int<N>,Int<P>>>;
    using cTileShape = Shape<Int<d_tile>,Int<N_tile>>; // same as XTileShape
    using XTileShape = cTileShape; // same as XTileShape
    using c2XSlab = Layout<XSlabShape>; // [d,N,P] -> [d,[N,P]]
    using X2cSlab = decltype(group<1,3>(Layout<cSlabShape>{})); // [d,[N,P]] -> [d,N,P]
    using c2XTile = Layout<XTileShape>; // [d_tile,N_tile] -> [d_tile,N_tile]
    using C2ZTile = Layout<CTileShape>; // [D_tile,N_tile] -> [d_tile^p,N_tile]
    using ZSlabShape = decltype(static_tree_cast<int64_t>(Shape<Int<D>,Shape<Int<N>,Int<P>>>{})); // [D,[N,P]]
    using C2ZSlab = decltype(flatten(Layout<ZSlabShape>{})); // [D,N,P] -> [D,[N,P]]
    using ZTileShape = decltype(tpow_shape<pow>(XTileShape{}));
    using GXSlab = decltype(GcSlab{}.compose(X2cSlab{})); // gX_slab is a view of gc_slab
    using GZSlab = decltype(make_layout(static_tree_cast<int64_t>(sympow_shape<pow,d_tile>(XSlabShape{})))); // virtual
    using GCSlab = decltype(GZSlab{}.compose(C2ZSlab{})); // virtual
    GXSlab gXSlab;
    static_assert(size(GZSlab{}) == size(GCSlab{}));
    using MmaCfg = decltype(make_mma_cfg<T, PerfCfg, MmaAtom, MNKAtomPlacement>(MNKTileShape{}, MmaAtom{}, MNKAtomPlacement{}, GASlab{}, GBSlab{}, GCSlab{}));
    static constexpr MmaCfg mma{};
    MmaAtom mma_Atom{};
    decltype(mma.A) A;
    decltype(mma.B) B;
    decltype(mma.C) C;
    using FrgTypeA = typename MmaCfg::FrgTypeA;
    using FrgTypeB = typename MmaCfg::FrgTypeB;
    using FrgTypeC = typename MmaCfg::FrgTypeC;
    static constexpr int thread_num = mma.thread_num;
    static_assert(size(ZTileShape{}) == size(decltype(C){}.tileShape));
    using _ZMmaFrgThr = decltype(C2ZTile{}.compose(C.mma_FrgThr));
    using _ZTprodFrgThr = decltype(colayout(ZTileShape{}, get<0>(_ZMmaFrgThr{}))); // colayout transforms the mma_frg layout into a format compatible with tprod
    using ZTprodFrgThr = decltype(make_layout(_ZTprodFrgThr{}, get<1>(_ZMmaFrgThr{})));
    static_assert(size(ZTprodFrgThr{}) == size(ZTileShape{}));
    using CTprodFrgThr_Frg = decltype(left_inverse(C2ZTile{}).compose(get<0>(ZTprodFrgThr{}))); // maps tprod_frg_coords -> C_coords
    using ZTprod__2__CMma__frg = decltype(left_inverse(get<0>(C.mma_FrgThr)).compose(CTprodFrgThr_Frg{})); // C_tprod_frg_coords -> Y_tprod_frg_coords
    ZTprod__2__CMma__frg Z_tprod_frg__2__C_mma_frg;
    using SZTile = Layout<ZTileShape>; // virtual (we don't even store the expansions in smem)
    using Sympow = SympowCfg<T, pow, XSlabShape, XTileShape, ZTprodFrgThr, GZSlab, GXSlab, SZTile>;
    using SympowBwd = SympowBwdCfg<Sympow, SmemAccI>;
    Sympow sympow;
    SympowBwd sympow_bwd;
    using SympowCoords = typename Sympow::SympowCoords;
    using Xi_t = decltype(typename Sympow::Xi_t{});
    Xi_t Xi;
    Sympow::XBatching X;
    Sympow::Z_t Z;
    using Xi_size_t = decltype(transform(Xi_t{}, [](auto const& x) { return size(x.sTile); }));
    using Xi_offset_t = decltype(get<1>(fold(Xi_size_t{}, make_tuple(_0{},make_tuple()),
            [](auto const& carry, auto const& Xi_size) {
                    auto [current, offsets] = carry;
                    return make_tuple(current+Xi_size, append(offsets, current)); })));
    using X_size_t = decltype(fold(Xi_size_t{}, _0{}, [](auto const& a, auto const& b) { return a + b; }));
    static constexpr Xi_size_t Xi_smem_size{};
    static constexpr Xi_offset_t Xi_smem_offset{};
    static constexpr X_size_t X_smem_size{};
    static int smem_size() {
        using X_SBatch = decltype(X)::SXBatch;
        using A_STile = decltype(A)::STile;
        using B_STile = decltype(B)::STile;
        constexpr static int smempipe = static_min(perf.smempipe, mma.K_tile_num * mma.M_tile_num);
        constexpr static int smem_size = Allocator<16>::total<T, T, T, T>(
            int(cosize(X_SBatch{})), // X_smem
            int(cosize(X_SBatch{})), // Xgrd_smem
            int(size(A_STile{}) * smempipe), // A_smem
            int(size(B_STile{}) * smempipe)  // B_smem
        );
        return smem_size;
    }
};


}