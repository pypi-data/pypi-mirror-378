#pragma once
#include <iostream>
#include "utilities.cuh"

namespace vidrial {
using namespace cute;

template<typename _FrTh_t, typename _frg_slicer, typename _Re2ThKey, typename _Th2ThKey, typename _tile_FrTh>
struct FrgThrTilingCfg {
    using FrTh_t = _FrTh_t;
    FrTh_t FrTh{};
    _frg_slicer frg_slicer{};
    _Re2ThKey Re2ThKey{};
    _Th2ThKey Th2ThKey{};
    _tile_FrTh tile_FrTh{};
};


template<typename _FrTh, typename _frg_slicer, typename _Re2ThKey, typename _Th2ThKey, typename _tile_FrTh>
void print_cfg(FrgThrTilingCfg<_FrTh, _frg_slicer, _Re2ThKey, _Th2ThKey, _tile_FrTh> const& cfg, std::string prefix = "") {
    std::cout << "FrgThrTilingCfg:\n";
    std::cout << prefix << "  FrTh: "; print(cfg.FrTh); std::cout << "\n";
    std::cout << prefix << "  frg_slicer: "; print(cfg.frg_slicer); std::cout << "\n";
    std::cout << prefix << "  Re2ThKey: "; print(cfg.Re2ThKey); std::cout << "\n";
    std::cout << prefix << "  Th2ThKey: "; print(cfg.Th2ThKey); std::cout << "\n";
    std::cout << prefix << "  tile_FrTh: "; print(cfg.tile_FrTh); std::cout << "\n";
}


template<typename TileRest, typename _FrgThr>
CUTE_HOST_DEVICE auto make_FrgThrTilingCfg(TileRest TiRe, _FrgThr _FrTh) {
    auto FrTh = coalesce(_FrTh, make_tuple(_0{}, _0{}));
    using FrgThr = decltype(FrTh);
    // Shapes
    auto TiReShape = make_shape(size<0>(TiRe), size<1>(TiRe));
    auto FrThrShape = make_shape(size<0>(FrTh), size<1>(FrTh));
    // Convert between the two partition layouts 
    auto TiRe2FrTh = left_inverse(FrTh).compose(TiRe);
    auto FrTh2TiRe = left_inverse(TiRe).compose(FrTh);
    // Projections
    auto FrTh2Fr = make_layout(FrThrShape, make_stride(_1{}, _0{}));
    auto FrTh2Th = make_layout(FrThrShape, make_stride(_0{}, _1{}));
    auto TiRe2Ti = make_layout(TiReShape, make_stride(_1{}, _0{}));
    auto TiRe2Re = make_layout(TiReShape, make_stride(_0{}, _1{}));
    // Slice the big fragment into the tile fragment
    auto Re2Fr = FrTh2Fr.compose(get<1>(TiRe2FrTh));
    auto tile_Fr = complement(Re2Fr, size<0>(FrTh));
    auto frg_slicer = make_layout(tile_Fr, Re2Fr);
    // Key function for thread and rest so we know which threads are active on each tile
    auto Re2Th = FrTh2Th.compose(get<1>(TiRe2FrTh));
    auto Th2Re = TiRe2Re.compose(get<1>(FrTh2TiRe));
    auto Th2ThKey = Re2Th.compose(Th2Re);
    auto Re2ThKey = FrTh2Th.compose(get<1>(TiRe2FrTh));
    // tile_FrgThr might not be an injective layout because of the Th dimension (even if FrThr is injective)
    auto FrThr2Ti = TiRe2Ti.compose(FrTh2TiRe);
    auto tile_FrTh = FrThr2Ti.compose(tile_Fr, _);
    return FrgThrTilingCfg<FrgThr, decltype(frg_slicer), decltype(Re2ThKey), decltype(Th2ThKey), decltype(tile_FrTh)>{};
}

CUTE_HOST_DEVICE void FrgThr_store_tile(auto& cfg, auto& A_frg, auto& B, auto& tile_idx) {
    if (threadIdx.x < size<1>(cfg.tile_FrTh)
       && cfg.Th2ThKey(threadIdx.x) == cfg.Re2ThKey(tile_idx)) {
        auto B_frg_src = slice_rest(A_frg, cfg.frg_slicer, tile_idx);
        auto B_frg_dst = slice_rest(B, cfg.tile_FrTh, threadIdx.x);
        copy(B_frg_src, B_frg_dst);
    }
}

CUTE_HOST_DEVICE void FrgThr_load_tile(auto& cfg, auto& A_frg, auto& B, auto& tile_idx) {
    if (threadIdx.x < size<1>(cfg.tile_FrTh)
       && cfg.Th2ThKey(threadIdx.x) == cfg.Re2ThKey(tile_idx)) {
        auto B_frg_src = slice_rest(B, cfg.tile_FrTh, threadIdx.x);
        auto B_frg_dst = slice_rest(A_frg, cfg.frg_slicer, tile_idx);
        copy(B_frg_src, B_frg_dst);
    }
}

}