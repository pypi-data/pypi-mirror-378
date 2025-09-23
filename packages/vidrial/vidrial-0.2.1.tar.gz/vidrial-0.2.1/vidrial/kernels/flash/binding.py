from dataclasses import dataclass
import math
from typing import Any
import torch
from vidrial.jit.static.types import Shape, Layout, Int
from vidrial.jit.static.util import layout_from_shape_stride, torch_dtype_to_c
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.binding import make_binding
from vidrial.jit.jit import jit, render
from vidrial.kernels.flash.configurator import base_configurator, advanced_configurator


# ------------------- Source Code -------------------

@dataclass
class SourceCode:
    T: str
    LT: str
    Atom1: str
    Atom2: str
    MNKTileShape1: Shape
    NTile2: Int
    MNKAtomPlacement1: Shape
    GQSlab: Layout
    GKSlab: Layout
    GVSlab: Layout
    GOSlab: Layout
    GLSlab: Layout
    smempipe1: int
    smempipe2: int
    regpipe1: int
    regpipe2: int
    use_ldsm1: bool
    use_ldsm2: bool
    swizzle1: int
    swizzle2: int
    q_in_reg: bool
    @property
    def template(self):
        return """
#include <cuda.h>
#include <cuda_runtime.h>
#include <iostream>
#include "cute/tensor.hpp"
#include "kernels/flash/kernel.cuh"

using namespace cute;
using namespace vidrial;

extern "C" int launch(void* __raw_Q, void* __raw_K, void* __raw_V, void* __raw_O, void* __raw_l, float softmax_scale) {
    using T = {T};
    using LT = {LT};
    using Atom1 = MMA_Atom<{Atom1}>;
    using Atom2 = MMA_Atom<{Atom2}>;
    using MNKTileShape_1 = decltype(static_tree_cast<int64_t>({MNKTileShape1}{}));
    using NTile2 = decltype(static_tree_cast<int64_t>({NTile2}{}));
    using MNKAtomPlacement_1 = decltype(static_tree_cast<int64_t>({MNKAtomPlacement1}{}));
    using GQSlab = decltype(static_tree_cast<int64_t>({GQSlab}{}));
    using GKSlab = decltype(static_tree_cast<int64_t>({GKSlab}{}));
    using GVSlab = decltype(static_tree_cast<int64_t>({GVSlab}{}));
    using GOSlab = decltype(static_tree_cast<int64_t>({GOSlab}{}));
    using GLSlab = decltype(static_tree_cast<int64_t>({GLSlab}{}));
    using PerfCfg1 = FlashPerfCfg<{smempipe1}, {regpipe1}, {use_ldsm1}, {swizzle1}, {q_in_reg}>;
    using PerfCfg2 = PerfCfg<{smempipe2}, {regpipe2}, {use_ldsm2}, {swizzle2}>;
    auto cfg = make_FlashKernelCfg<T, LT, Atom1, MNKTileShape_1, MNKAtomPlacement_1, Atom2, NTile2, GQSlab, GKSlab, GVSlab, GOSlab, GLSlab, PerfCfg1, PerfCfg2>();
    auto Q = reinterpret_cast<T*>(__raw_Q);
    auto K = reinterpret_cast<T*>(__raw_K);
    auto V = reinterpret_cast<T*>(__raw_V);
    auto O = reinterpret_cast<T*>(__raw_O);
    auto l = reinterpret_cast<LT*>(__raw_l);
    return launch_flash_attention_kernel(cfg, Q, K, V, O, l, softmax_scale);
}"""
    def __str__(self):
        return render(self.template, self.__dict__)


# ------------------- Binding -------------------

@dataclass
class BindingCfg:
    batches: tuple[int, ...]
    M: int
    N: int
    D: int
    E: int
    Q_shape: tuple[int, ...]
    K_shape: tuple[int, ...]
    V_shape: tuple[int, ...]
    O_shape: tuple[int, ...]
    l_shape: tuple[int, ...]
    Q_stride: tuple[int, ...]
    K_stride: tuple[int, ...]
    V_stride: tuple[int, ...]
    O_stride: tuple[int, ...]
    l_stride: tuple[int, ...]
    Atom1: str
    Atom2: str
    MNKTileShape1: tuple[int, ...]
    NTile2: int
    MNKAtomPlacement1: tuple[int, ...]
    smempipe1: int
    smempipe2: int
    regpipe1: int
    regpipe2: int
    use_ldsm1: bool
    use_ldsm2: bool
    swizzle1: int
    swizzle2: int
    q_in_reg: bool
    dtype: torch.dtype
    acc_dtype: torch.dtype
    @classmethod
    def from_args(cls, Q, K, V, O, l, Atom1, Atom2, MNKTileShape1, NTile2, MNKAtomPlacement1, smempipe1, smempipe2, regpipe1, regpipe2, use_ldsm1, use_ldsm2, swizzle1, swizzle2, q_in_reg):
        assert Q.device.type == K.device.type == V.device.type == O.device.type == l.device.type == 'cuda', f"Invalid {Q.device}, {K.device}, {V.device}, {O.device}, {l.device}."
        assert Q.dtype == K.dtype == V.dtype == O.dtype, f"Invalid {Q.dtype}, {K.dtype}, {V.dtype}, {O.dtype},  Q, K, V, O must have the same dtype"
        batches, M, N, D, E = Q.shape[:-2], Q.shape[-2], K.shape[-2], K.shape[-1], V.shape[-1]
        assert K.shape[:-2] == batches, f"Invalid {K.shape}, K must be of shape ({', '.join(str(b) for b in batches)}, {K.shape[-2]}, {K.shape[-1]})"
        assert V.shape[:-2] == batches, f"Invalid {V.shape}, V must be of shape ({', '.join(str(b) for b in batches)}, {V.shape[-2]}, {V.shape[-1]})"
        assert O.shape == (*batches, M, E), f"Invalid {O.shape}, O must be of shape ({', '.join(str(b) for b in batches)}, {M}, {E})"
        assert l.shape == (*batches, M), f"Invalid {l.shape}, l must be of shape ({', '.join(str(b) for b in batches)}, {M})"

        return cls(batches, M, N, D, E, Q.shape, K.shape, V.shape, O.shape, l.shape, Q.stride(), K.stride(), V.stride(), O.stride(), l.stride(), Atom1, Atom2, MNKTileShape1, NTile2, MNKAtomPlacement1, smempipe1, smempipe2, regpipe1, regpipe2, use_ldsm1, use_ldsm2, swizzle1, swizzle2, q_in_reg, Q.dtype, l.dtype)

    @property
    def source(self):
        """ Conversion between the different variable name and shape conventions
                Python                        c++
            Q_shape=[P,M1,K1]      ->      GQSlabShape=[M1,K1,P]
            K_shape=[P,N1,K1]      ->      GKSlabShape=[N1,K1,P]
            V_shape=[P,K2,N2]      ->      GVSlabShape=[N2,K2,P]
            O_shape=[P,M2,N2]      ->      GO_slabShape=[M2,N2,P]
            l_shape=[P,M2]      ->      GL_slabShape=[M2,P]
        """
        batch_inds = tuple(range(len(self.batches)))
        GQslab = layout_from_shape_stride(self.Q_shape, self.Q_stride, (-2, -1, batch_inds))
        GKslab = layout_from_shape_stride(self.K_shape, self.K_stride, (-2, -1, batch_inds))
        GVslab = layout_from_shape_stride(self.V_shape, self.V_stride, (-1, -2, batch_inds))
        GOslab = layout_from_shape_stride(self.O_shape, self.O_stride, (-2, -1, batch_inds))
        GLslab = layout_from_shape_stride(self.l_shape, self.l_stride, (-1, batch_inds))
        return SourceCode(
            T=torch_dtype_to_c(self.dtype),
            LT=torch_dtype_to_c(self.acc_dtype),
            Atom1=self.Atom1,
            Atom2=self.Atom2,
            MNKTileShape1=Shape(*[Int(x) for x in self.MNKTileShape1]),
            NTile2=Int(self.NTile2),
            MNKAtomPlacement1=Shape(*[Int(x) for x in self.MNKAtomPlacement1]),
            GQSlab=GQslab,
            GKSlab=GKslab,
            GVSlab=GVslab,
            GOSlab=GOslab,
            GLSlab=GLslab,
            smempipe1=self.smempipe1,
            smempipe2=self.smempipe2,
            regpipe1=self.regpipe1,
            regpipe2=self.regpipe2,
            use_ldsm1=self.use_ldsm1,
            use_ldsm2=self.use_ldsm2,
            swizzle1=self.swizzle1,
            swizzle2=self.swizzle2,
            q_in_reg=self.q_in_reg,
        )

# ---------------------- Autotune --------------------------------

def make_mma_configurator(smempipe=None, regpipe=None, use_ldsm=None, swizzle=None):
    def mma_configurator(args: dict) -> list[dict[str, Any]]:
        Q, K, V = args['Q'], args['K'], args['V']
        batches, M, N, D, E = Q.shape[:-2], Q.shape[-2], K.shape[-2], K.shape[-1], V.shape[-1]
        return advanced_configurator(MNDEP=(M, N, D, E, batches), dtype=Q.dtype, acc_dtype=torch.float32, smempipe=smempipe, regpipe=regpipe, use_ldsm=use_ldsm, swizzle=swizzle, random_seed=42)
    return mma_configurator

def hash_fn(args: dict) -> str:
    Q, K, V, O, l = args['Q'], args['K'], args['V'], args['O'], args['l']
    batches, M, N, D, E = Q.shape[:-2], Q.shape[-2], K.shape[-2], K.shape[-1], V.shape[-1]
    Q_major = 'K_major' if Q.stride(-1) == 1 else 'M_major'
    K_major = 'N_major' if K.stride(-1) == 1 else 'K_major'
    V_major = 'N_major' if V.stride(-1) == 1 else 'K_major'
    P = math.prod(batches)
    return f"{Q.dtype}-{K.dtype}-{V.dtype}-{O.dtype}-{l.dtype}-M_{M}-N_{N}-D_{D}-E_{E}-P_{P}-{Q_major}-{K_major}-{V_major}"

@make_binding(cache=ConfigTimingCache('flash_attn', hash_fn),
          sweep=make_mma_configurator(smempipe=(1,2,3), regpipe=(1,2,4), use_ldsm=True, swizzle=1))
def binding(Q, K, V, O, l, softmax_scale, Atom1, Atom2, MNKTileShape1, NTile2, MNKAtomPlacement1, smempipe1, smempipe2, regpipe1, regpipe2, use_ldsm1, use_ldsm2, swizzle1, swizzle2, q_in_reg):
    binding_cfg = BindingCfg.from_args(Q, K, V, O, l, Atom1, Atom2, MNKTileShape1, NTile2, MNKAtomPlacement1, smempipe1, smempipe2, regpipe1, regpipe2, use_ldsm1, use_ldsm2, swizzle1, swizzle2, q_in_reg)
    jit(name = "flash_attn",
        code = str(binding_cfg.source)
    )(Q, K, V, O, l, softmax_scale)
