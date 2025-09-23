from typing import Dict, Any
from dataclasses import dataclass
from math import prod, log2
import torch as th
import logging
from vidrial.jit.static.types import Shape, Layout, Int
from vidrial.jit.static.util import layout_from_shape_stride, torch_dtype_to_c
from vidrial.py_utils.test_utils import diff
from vidrial.kernels.mma_configurator import advanced_configurator
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.binding import make_binding
from vidrial.jit.jit import jit, render
from vidrial.kernels.sympow_mma.dimensions import problem_shape

logger = logging.getLogger(__name__)


# ------------------- Source Code -------------------

@dataclass
class SourceCode:
    T: str
    MNKPSlabShape: Shape
    MNKTileShape: Shape
    d: int
    d_tile: int
    pow: int
    expand_K: bool
    GaSlab: Layout
    GBSlab: Layout
    GCSlab: Layout
    duplicate_correction: bool
    smempipe: int
    regpipe: int
    use_ldsm: bool
    swizzle: int
    Atom: str
    MNKAtomPlacement: Shape
    scale_A: bool
    @property
    def template(self):
        return """
#include <cuda.h>
#include <cuda_runtime.h>
#include <iostream>
#include "cute/tensor.hpp"
#include "kernels/sympow_mma/kernel.cuh"

using namespace cute;
using namespace vidrial;

extern "C" int launch(void* __raw_A, void* __raw_B, void* __raw_C, float sA) {
    using T = {T};
    using MNKPSlabShape = decltype(static_tree_cast<int64_t>({MNKPSlabShape}{}));
    using MNKTileShape = decltype(static_tree_cast<int64_t>({MNKTileShape}{}));
    constexpr int d = {d}, d_tile = {d_tile};
    constexpr int pow = {pow};
    constexpr bool expand_K = {expand_K};
    using GaSlab = decltype(static_tree_cast<int64_t>({GaSlab}{}));
    using GBSlab = decltype(static_tree_cast<int64_t>({GBSlab}{}));
    using GCSlab = decltype(static_tree_cast<int64_t>({GCSlab}{}));
    constexpr bool duplicate_correction = {duplicate_correction};
    using PerfCfg = PerfCfg<{smempipe}, {regpipe}, {use_ldsm}, {swizzle}>;
    using Atom = MMA_Atom<{Atom}>;
    using MNKAtomPlacement = decltype(static_tree_cast<int64_t>({MNKAtomPlacement}{}));
    using Cfg = SympowMmaKernelCfg<T, pow, Atom, MNKAtomPlacement, MNKPSlabShape, MNKTileShape, d, d_tile, expand_K, GaSlab, GBSlab, GCSlab, PerfCfg>;
    auto A = reinterpret_cast<T*>(__raw_A);
    auto B = reinterpret_cast<T*>(__raw_B);
    auto C = reinterpret_cast<T*>(__raw_C);
    return launch_sympow_mma_kernel<duplicate_correction, {scale_A}>(Cfg{}, A, B, C, sA);
}"""
    def __str__(self):
        return render(self.template, self.__dict__)


# ------------------- Binding -------------------

@dataclass
class BindingCfg:
    batches: tuple[int, ...]
    M: int
    N: int
    K: int
    d: int
    d_tile: int
    scale_A: bool
    pow: int
    expand_dim: int 
    A_shape: tuple[int, ...]
    B_shape: tuple[int, ...]
    C_shape: tuple[int, ...]
    A_stride: tuple[int, ...]
    B_stride: tuple[int, ...]
    C_stride: tuple[int, ...]
    duplicate_correction: bool
    smempipe: int
    regpipe: int
    use_ldsm: bool
    swizzle: int
    Atom: str
    MNKTileShape: Shape 
    MNKAtomPlacement: Shape
    dtype: th.dtype
    def is_valid(self):
        assert self.M % self.MNKTileShape[0].value == 0 # type: ignore
        assert self.N % self.MNKTileShape[1].value == 0 # type: ignore
        assert self.K % self.MNKTileShape[2].value == 0 # type: ignore

    @classmethod
    def from_args(cls, A: th.Tensor, B: th.Tensor, C: th.Tensor, expand_dim: int, power: int, d_tile: int, scale_A: float, duplicate_correction: bool,
                  smempipe: int, regpipe: int, use_ldsm: bool, swizzle: int, Atom: str, MNKTileShape: Shape, MNKAtomPlacement: Shape) -> 'BindingCfg':
        assert A.device.type == B.device.type == C.device.type == 'cuda', f"Invalid {A.device}, {B.device}, {C.device}."
        assert A.dtype == B.dtype == C.dtype, f"Invalid {A.dtype}, {B.dtype}, {C.dtype}. Kernel currently assumes all input tensors have the same dtype"
        dtype = A.dtype
        batches, M, N, K, d, D = problem_shape(A.shape, B.shape, C.shape, expand_dim, power, d_tile)
        self = cls(batches=batches, M=M, N=N, K=K, d=d, d_tile=d_tile, pow=power, expand_dim=expand_dim, scale_A=(scale_A != 1.0), duplicate_correction=duplicate_correction, 
                   A_shape=A.shape, B_shape=B.shape, C_shape=C.shape,
                   A_stride=A.stride(), B_stride=B.stride(), C_stride=C.stride(),
                   smempipe=smempipe, regpipe=regpipe, use_ldsm=use_ldsm, swizzle=swizzle,
                   Atom=Atom, MNKTileShape=MNKTileShape, MNKAtomPlacement=MNKAtomPlacement, dtype=dtype)
        self.is_valid()
        logger.debug("BindingCfg: %s", self)
        return self

    @property
    def source(self):
        """ Conversion between the different variable name and shape conventions
                     Python                       c++
                A                    ->      a
                eA                   ->      A
                A_shape=[P,M,d]      ->      aSlabShape=[M,d,P]    if expand_K
                A_shape=[P,d,K]      ->      aSlabShape=[d,K,P]    if not expand_K
                B_shape=[P,K,N]      ->      BSlabShape=[N,K,P]
                C_shape=[P,M,N]      ->      CSlabShape=[M,N,P]
        """
        batch_inds = tuple(range(len(self.batches)))
        PShape = Shape(*[Int(b) for b in self.batches])
        source = SourceCode(
            T=torch_dtype_to_c(self.dtype),
            MNKPSlabShape=Shape(Int(self.M), Int(self.N), Int(self.K), PShape),
            d=self.d,
            d_tile=self.d_tile,
            pow=self.pow,
            expand_K=True if self.expand_dim%3 == 2 else False,
            GaSlab=layout_from_shape_stride(self.A_shape, self.A_stride, (-2, -1, batch_inds)),
            GBSlab=layout_from_shape_stride(self.B_shape, self.B_stride, (-1, -2, batch_inds)),
            GCSlab=layout_from_shape_stride(self.C_shape, self.C_stride, (-2, -1, batch_inds)),
            duplicate_correction=self.duplicate_correction,
            smempipe=self.smempipe,
            regpipe=self.regpipe,
            use_ldsm=self.use_ldsm,
            swizzle=self.swizzle,
            Atom=self.Atom,
            MNKTileShape=self.MNKTileShape,
            scale_A=self.scale_A,
            MNKAtomPlacement=self.MNKAtomPlacement)
        return source

# ---------------------- Autotune --------------------------------

def make_configurator(smempipe: tuple[int, int], regpipe: tuple[int, int], use_ldsm: bool, swizzle: int):
    def configurator(args: dict) -> list[Dict[str, Any]]:
        A, B, C, expand_dim, power, d_tile, duplicate_correction = args['A'], args['B'], args['C'], args['expand_dim'], args['power'], args['d_tile'], args['duplicate_correction']
        batches, M, N, K, d, D = problem_shape(A.shape, B.shape, C.shape, expand_dim, power, d_tile)
        D_tile = d_tile ** power
        if expand_dim % 3 == 2: # expand K
            M_tile, N_tile, K_tile = None, None, D_tile 
        else: # expand M
            M_tile, N_tile, K_tile = D_tile, None, None
        configs = advanced_configurator((M, N, K, batches), A.dtype, th.float32, M_tile, N_tile, K_tile, smempipe=smempipe, regpipe=regpipe, use_ldsm=use_ldsm, swizzle=swizzle)
        return configs
    return configurator

def hash_fn(args: dict) -> str:
    P, M, N, K, d, D = problem_shape(args['A'].shape, args['B'].shape, args['C'].shape, args['expand_dim'], args['power'], args['d_tile'])
    A, B, C = args['A'], args['B'], args['C']
    key = f"M_{int(log2(M))}-N_{int(log2(N))}-K_{int(log2(K))}-"
    key += f"{A.dtype}-{args['expand_dim'] % A.ndim}-{args['power']}-{args['d_tile']}-"
    find_major_dim = lambda x: [i for i, s in enumerate(x.stride()) if s == 1][0]
    key += f"{find_major_dim(A)}-{find_major_dim(B)}-{find_major_dim(C)}"
    return key


@make_binding(cache=ConfigTimingCache('sympow_mma', hash_fn), 
          sweep=make_configurator(smempipe=(1,2), regpipe=(0,1), use_ldsm=True, swizzle=1))
def binding(A, B, C, expand_dim, power, d_tile, scale_A, duplicate_correction, smempipe, regpipe, use_ldsm, swizzle, Atom, MNKTileShape, MNKAtomPlacement):
    binding_cfg = BindingCfg.from_args(A, B, C, expand_dim, power, d_tile, scale_A, duplicate_correction, smempipe, regpipe, use_ldsm, swizzle, Atom, MNKTileShape, MNKAtomPlacement)
    jit(name = "sympow_mma",
        code = str(binding_cfg.source)
    )(A, B, C, scale_A)
