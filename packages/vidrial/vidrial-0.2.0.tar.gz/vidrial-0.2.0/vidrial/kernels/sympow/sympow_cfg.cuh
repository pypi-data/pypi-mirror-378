#pragma once
#include "../copy/copy_cfg.cuh"
#include "../cuda_utils/sympow.cuh"
#include "../cuda_utils/perf_cfg.cuh"

namespace vidrial {

template<typename Cfg>
struct SympowCoords {
    static constexpr auto d = Cfg::d; // feature dim
    static constexpr auto b = Cfg::b; // batch dim
    static constexpr auto d_tile = Cfg::d_tile; // size of the tile d
    static constexpr auto b_tile = Cfg::b_tile; // size of the tile b
    static constexpr auto power = Cfg::p;
    using ZSlabShape = typename Cfg::ZSlabShape;
    using ZTileShape = typename Cfg::ZTileShape;
    // The two iterators for the d,b dimensions
    using DTileSeq = NonIncSeq<d/d_tile, power>;
    DTileSeq D_tile_iter{};
    int b_tile_idx = 0;
    // Number of tiles along the D
    static constexpr auto D_tile_num = DTileSeq::num_elements;
    CUTE_HOST_DEVICE auto slice_Z_tile(auto& Z) {
        auto tile_coord = make_coord(D_tile_iter.idx, b_tile_idx);
        return slice_rest(zipped_divide(Z, Cfg{}.Z.tile_copy.TileShape), tile_coord);
    }
    /* Slices out all the features and a tile of the batch
    output shape = [d, b_tile]. */
    template<int i>
    CUTE_HOST_DEVICE auto slice_X_tile(auto& X) {
        auto coord = make_coord(get<i>(D_tile_iter.seq), b_tile_idx);
        auto X_tiled = zipped_divide(X, Cfg{}.X_TileShape);
        return slice_rest(X_tiled, coord);
    }
    template<int i>
    CUTE_HOST_DEVICE auto slice_X_tile_from_batch(auto& X) {
        auto tile_coord = make_coord(get<i>(D_tile_iter.seq), _0{});
        auto X_tiled = zipped_divide(X, Cfg{}.X_TileShape);
        return slice_rest(X_tiled, tile_coord);
    }
    CUTE_HOST_DEVICE auto slice_X_tile_from_batch(auto& X, int d_tile_idx) {
        auto tile_coord = make_coord(d_tile_idx, _0{});
        auto X_tiled = zipped_divide(X, Cfg{}.X_TileShape);
        return slice_rest(X_tiled, tile_coord);
    }
    /* Slices out all the features and a tile of the batch
    output shape = [d, b_tile]. */
    CUTE_HOST_DEVICE auto slice_X_batch(auto& X) {
        auto X_batch_shape = make_shape(Int<d>{}, Int<b_tile>{});
        auto X_tiled = zipped_divide(X, X_batch_shape);
        return slice_rest(X_tiled, make_coord(_0{},b_tile_idx));
    }
    CUTE_HOST_DEVICE float scale_correction() {
        return sqrtf(D_tile_iter.duplicate_count());
    }
    CUTE_HOST_DEVICE auto D_coord() {return D_tile_iter.idx; }
    CUTE_HOST_DEVICE auto b_coord() { return b_tile_idx; }
    CUTE_HOST_DEVICE void step_D(int step = 1) { D_tile_iter += step; }
    CUTE_HOST_DEVICE void step_b(int step = 1) { b_tile_idx += step; }
    CUTE_HOST_DEVICE bool valid_D_tile() { return D_tile_iter.idx < D_tile_num; }
    CUTE_HOST_DEVICE bool valid_b_tile(int b) { return b_tile_idx * b_tile < b; }
    CUTE_HOST_DEVICE void reset_D() { D_tile_iter.reset(); }
    CUTE_HOST_DEVICE void reset_b() { b_tile_idx = 0; }
    CUTE_HOST_DEVICE void reset() { reset_D(); reset_b(); }
    template<int Is>
    CUTE_HOST_DEVICE bool store_dim() {
        return D_tile_iter.template store_dim<Is>();
    }
};

/* This class combines TprodM + SymmetricCoords to perform all the computations on
data of the shape of ZSympowCfg.
    - Z: [[td,td,...],r],b] where r=size(sym_coords)  Y is basically a list of cubes
    - X_batch_copy to move all the features of a batch [[d],bk]
    - Y: [[d,d],b] you most likely only want to work with tiles of Y
    - X0,X1: the factors of the tprod Y
*/
template <typename _T, int _p, typename _XSlabShape, typename _XTileShape, typename _ZFrgThr, 
          typename GZSlab, typename GXSlab, typename SZTile, typename _PerfCfg = DefaultPerfCfg>
struct SympowCfg {
    using T = _T;
    static constexpr int p = _p;
    using XSlabShape = _XSlabShape; // [d, b]
    static constexpr int d = size<0>(XSlabShape{});
    static constexpr int b = size<1>(XSlabShape{});
    using XTileShape = _XTileShape; // [d_tile, b_tile]
    XTileShape X_TileShape;
    static constexpr int d_tile = size<0>(XTileShape{});
    static constexpr int b_tile = size<1>(XTileShape{});
    using YShape = decltype(static_tree_cast<int64_t>(tpow_shape<p>(XSlabShape{}))); // [[d, d, ...], b]
    using ZTileShape = decltype(tpow_shape<p>(XTileShape{})); // [[d_tile, d_tile, ...], b_tile]
    using ZFrgThr = _ZFrgThr;
    using YSlab = Layout<YShape>; // the virtual tensor that should not be materialized // [[d, d, ...], b]
    static constexpr int thread_num = size<1>(ZFrgThr{});

    template<int component>
    struct Xi_t_ {
        using TprodFrgThr_t = decltype(tprod_factor_project<component>(ZTileShape{}, ZFrgThr{}));
        using TprodFrg_t = decltype(make_layout(get<0>(TprodFrgThr_t{}.shape())));
        TprodFrgThr_t tprod_FrgThr;
        TprodFrg_t Frg;
        using TileCopy = decltype(make_TileCopyCfg<T,thread_num>(XTileShape{}, GXSlab{}));
        TileCopy tile_copy;
        typename TileCopy::STile sTile;
    };
    template<auto... Is>
    static constexpr auto get_Xi_t(index_sequence<Is...> seq) { return make_tuple(Xi_t_<Is>{}...);}
    using Xi_t = decltype(get_Xi_t(make_index_sequence<p>{}));
    Xi_t Xi;

    using ZSlabShape = decltype(sympow_shape<p, d_tile>(XSlabShape{})); // [[[d_tile, d_tile, ...], N_sympow], b]
    struct Z_t{
        // The tile shapes need to be padded with 1 along the tile_num dimension
        using CopyTileShape = decltype(make_shape(make_shape(get<0>(ZTileShape{}), _1{}), get<1>(ZTileShape{})));
        using CopySTile= decltype(make_layout(make_layout(get<0>(SZTile{}), Layout<_1>{}), get<1>(SZTile{})));
        using TileCopy = decltype(make_TileCopyCfg<T,thread_num>(CopyTileShape{}, GZSlab{}, CopySTile{}));
        using Frg_t = decltype(make_layout(get<0>(ZFrgThr{}.shape())));
        TileCopy tile_copy;
        ZFrgThr tprod_FrgThr;
        Frg_t Frg;
        GZSlab gSlab;
        SZTile sTile;
        ZTileShape TileShape;
    };
    Z_t Z;
    using PerfCfg = _PerfCfg;
    static constexpr PerfCfg perf{};
    using SympowCoords = NonIncSeq<d/d_tile, p>;
    static constexpr int d_tile_num = SympowCoords::num_elements;
    static constexpr int b_tile_num = b/b_tile;
    static_assert(d_tile_num==size<0,1>(GZSlab{}));
    using XBatchShape = decltype(make_shape(get<0>(XSlabShape{}), get<1>(XTileShape{}))); // [d, b_tile]
    XBatchShape X_BatchShape;
    struct XBatching { // used to move batches of X (containing all the features)
        using XBatchCopy = decltype(make_TileCopyCfg<T,thread_num>(XBatchShape{}, GXSlab{}));
        using SXBatch = typename XBatchCopy::STile;
        GXSlab gSlab;
        SXBatch sBatch;
        XBatchCopy batch_copy;
    };
    XBatching X;
};

template <typename T, int p>
auto make_sympow_kernel_cfg(auto Z_frg_shape, auto X_tile_shape, auto gZ_slab, auto gX_slab, auto sZ_tile) {
    static_assert(rank(gZ_slab)==2 && rank<0>(gZ_slab)==2 && rank<0,0>(gZ_slab)==p);
    static_assert(size<0,0,0>(gZ_slab)==size<0>(X_tile_shape)); // feature dims match
    static_assert(size<1>(gZ_slab)==size<1>(gX_slab)); // batch dims match
    auto Z_tile_shape = tpow_shape<p>(X_tile_shape);
    using ZFrgThr = decltype(zipped_divide(make_layout(Z_tile_shape), Z_frg_shape));
    auto cfg = SympowCfg<T, p, decltype(gX_slab.shape()), decltype(X_tile_shape), ZFrgThr,
                         decltype(gZ_slab), decltype(gX_slab), decltype(sZ_tile)>{};
    return cfg;
}

// --------------- Utilities for the sympow config ---------------

template<auto... Is, typename Cfg> CUTE_DEVICE
auto sympow_load_Xi_frgs(Cfg& cfg, auto& sympow_tile_coords, auto& sX_batch) {
    // TODO: Could be optimized by only loading the Xi fragment when the index has changed
    // this would require passing it rXi_frg and returning void
    using T = typename Cfg::T;
    auto rXi_tprod_frg = make_tuple(make_tensor<T>(get<Is>(cfg.Xi).Frg)...);
    (..., [&]() { // s2r load of Xi_tprod_frg.
        auto sXi_tile = sympow_tile_coords.slice_X_tile_from_batch<Is>(sX_batch);
        auto sXi_tprod_frg = slice_rest(sXi_tile, get<Is>(cfg.Xi).tprod_FrgThr, threadIdx.x);
        copy(sXi_tprod_frg, get<Is>(rXi_tprod_frg));
    }());
    return rXi_tprod_frg;
}



} // namespace vidrial