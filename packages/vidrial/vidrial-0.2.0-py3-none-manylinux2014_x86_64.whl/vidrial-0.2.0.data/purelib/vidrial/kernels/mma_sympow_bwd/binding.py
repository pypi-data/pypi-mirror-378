from typing import Dict, Any
import torch as th
from dataclasses import dataclass
from functools import partial
import logging
from vidrial.kernels.sympow.dimensions import sympow_dim
from vidrial.jit.static import Shape, Layout, Int, Tuple
from vidrial.jit.static.util import layout_from_shape_stride, torch_dtype_to_c
from vidrial.kernels.mma_configurator import make_configurator as create_configurator, dtype_to_bytes, ADVANCED_FILTERS, safe_filter, Config, CudaDType
from vidrial.jit.jit import jit, render
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.binding import make_binding
from vidrial.kernels.mma_sympow_bwd.dimensions import canonical_inputs, dimensions

# ------------------- Source Code -------------------
@dataclass
class SourceCode:
    T: str
    MNKPSlabShape: Shape
    d: int
    d_tile: int
    pow: int
    GASlab: Layout
    GBSlab: Layout
    GcSlab: Layout
    duplicate_correction: bool
    MNKTileShape: Shape
    MNKAtomPlacement: Shape
    Atom: str
    smempipe: int
    regpipe: int
    use_ldsm: bool
    swizzle: bool
    SmemAccI: Tuple
    scale_A: bool
    @property
    def template(self):
        return """
#include <cuda.h>
#include <cuda_runtime.h>
#include <iostream>
#include "cute/tensor.hpp"
#include "kernels/mma_sympow_bwd/kernel.cuh"
using namespace cute;
using namespace vidrial;
extern "C" int launch(void* __raw_A, void* __raw_B, void* __raw_c, void* __raw_c_dot, float sA) {
    using T = {T};
    using MNKPSlabShape = decltype(static_tree_cast<int64_t>({MNKPSlabShape}{}));
    using MNKTileShape = decltype(static_tree_cast<int64_t>({MNKTileShape}{}));
    constexpr int d = {d}, d_tile = {d_tile};
    constexpr int pow = {pow};
    constexpr int expand_dim = -2;
    using GASlab = decltype(static_tree_cast<int64_t>({GASlab}{}));
    using GBSlab = decltype(static_tree_cast<int64_t>({GBSlab}{}));
    using GcSlab = decltype(static_tree_cast<int64_t>({GcSlab}{}));
    constexpr bool duplicate_correction = {duplicate_correction};
    using PCfg = PerfCfg<{smempipe}, {regpipe}, {use_ldsm}, {swizzle}>;
    using Atom = MMA_Atom<{Atom}>;
    using MNKAtomPlacement = decltype(static_tree_cast<int64_t>({MNKAtomPlacement}{}));
    using SmemAccI = {SmemAccI};
    using KernelCfg = SympowCMmaCfg<T, pow, Atom, MNKAtomPlacement, MNKPSlabShape, MNKTileShape, d, d_tile, GASlab, GBSlab, GcSlab, SmemAccI, PCfg>;
    auto A = reinterpret_cast<T*>(__raw_A);
    auto B = reinterpret_cast<T*>(__raw_B);
    auto c = reinterpret_cast<T*>(__raw_c);
    auto c_dot = reinterpret_cast<T*>(__raw_c_dot);
    return launch_mma_sympow_bwd_kernel<duplicate_correction, {scale_A}>(KernelCfg{}, A, B, c, c_dot, sA);
}
"""
    def __str__(self):
        return render(self.template, self.__dict__)

# ------------------- Binding -------------------
@dataclass
class BindingCfg:
    """ The main methods:
          from_args: constructs a BindingCfg with the binding arguments themselves
          source: the source code object that the binding relies upon
          canonical_args: preprocesses the arguments into the form accepted by the source code
    """
    batches: tuple[int, ...]
    M: int
    N: int
    K: int
    d: int
    D: int
    dtype: th.dtype
    A_shape: tuple[int, ...]
    B_shape: tuple[int, ...]
    c_shape: tuple[int, ...]
    A_stride: tuple[int, ...]
    B_stride: tuple[int, ...]
    c_stride: tuple[int, ...]
    expand_dim: int  # TODO: Currently only expand_dim=-1 (D=N) is supported
    power: int
    d_tile: int
    scale_A: bool
    duplicate_correction: bool
    MNKTileShape: Shape
    MNKAtomPlacement: Shape
    Atom: str
    smempipe: int
    regpipe: int
    use_ldsm: bool
    swizzle: bool
    SmemAccI: Tuple
    @classmethod
    def from_args(cls, A, B, c, c_dot, expand_dim, power, d_tile, scale_A, duplicate_correction, MNKTileShape, MNKAtomPlacement, Atom, smempipe, regpipe, use_ldsm, swizzle, SmemAccI):
        assert A.device.type == B.device.type == c.device.type == c_dot.device.type == 'cuda', f"Invalid {A.device}, {B.device}, {c.device}, {c_dot.device}."
        assert A.dtype == B.dtype == c.dtype
        assert c.shape == c_dot.shape and c.stride() == c_dot.stride() and c.dtype == c_dot.dtype, "c and c_dot should have same shape, stride and dtype"
        assert expand_dim == -2, "Currently only expand_dim=-2 is supported"
        dtype = A.dtype
        A, B, c, c_dot, expand_dim = canonical_inputs(A, B, c, c_dot, expand_dim)
        batches, M, K, N, d = dimensions(A.shape, B.shape, c.shape, power, d_tile)
        D = sympow_dim(d, power, d_tile)
        assert M == D, f"N={N} must be equal to sympow_dim(d, power, d_tile)={D}"
        A_shape, B_shape, c_shape = tuple(A.shape), tuple(B.shape), tuple(c.shape)
        A_stride, B_stride, c_stride = A.stride(), B.stride(), c.stride()
        return cls(batches, M, N, K, d, D, dtype,
                   A_shape, B_shape, c_shape, A_stride, B_stride, c_stride,
                   expand_dim, power, d_tile, scale_A != 1.0, duplicate_correction,
                   MNKTileShape, MNKAtomPlacement, Atom,
                   smempipe, regpipe, use_ldsm, swizzle, SmemAccI)
    @property
    def source(self):
        """ Conversion between the different variable name and shape conventions
                M = D = sympow_dim(d, power, d_tile)
                    Python                     c++
                A_shape=[P,M,K]      ->      aSlabShape=[M,K,P]
                B_shape=[P,K,N]      ->      BSlabShape=[N,K,P]
                c_shape=[P,d,N]      ->      CSlabShape=[d,N,P]
        """
        batch_inds = tuple(range(len(self.batches)))
        PShape = Shape(*[Int(b) for b in self.batches])
        return SourceCode(
            T=torch_dtype_to_c(self.dtype),
            MNKPSlabShape=Shape(Int(self.M), Int(self.N), Int(self.K), PShape),
            d=self.d,
            d_tile=self.d_tile,
            pow=self.power,
            GASlab=layout_from_shape_stride(self.A_shape, self.A_stride, (-2, -1, batch_inds)),
            GBSlab=layout_from_shape_stride(self.B_shape, self.B_stride, (-1, -2, batch_inds)),
            GcSlab=layout_from_shape_stride(self.c_shape, self.c_stride, (-2, -1, batch_inds)),
            duplicate_correction=self.duplicate_correction,
            MNKTileShape=self.MNKTileShape,
            MNKAtomPlacement=self.MNKAtomPlacement,
            Atom=self.Atom,
            smempipe=self.smempipe,
            regpipe=self.regpipe,
            use_ldsm=self.use_ldsm,
            swizzle=self.swizzle,
            SmemAccI=self.SmemAccI,
            scale_A=self.scale_A,
        )

# ------------------- Autotuned -------------------
def smem_estimate(d, power, d_tile, mma_config: Config):
    smempipe = mma_config.smempipe
    M_tile, N_tile, K_tile = mma_config.MNKTileShape
    dtype_bytes = dtype_to_bytes(mma_config.dtype)
    X_smem = N_tile * d * dtype_bytes
    X_grad_smem = X_smem
    A_smem, B_smem = M_tile * K_tile * smempipe * dtype_bytes, K_tile * N_tile * smempipe * dtype_bytes
    return X_smem + X_grad_smem + A_smem + B_smem

@safe_filter
def smem_filter(d, power, d_tile, configs):
    return [c for c in configs if smem_estimate(d, power, d_tile, c) <= c.max_smem]

def make_configurator(smempipe: tuple[int, int], regpipe: tuple[int, int], use_ldsm: bool, swizzle: int):
    """ returns function that constCreates a set of promising configurations for the MMA kernel
        The functional arguments are A,B,c,c_dot,expand_dim,power,d_tile,duplicate_correction
        The rest are performance arguments MNKTileShape, MNKAtomPlacement, Atom, smempipe, regpipe, use_ldsm, swizzle  """
    def configurator(args: dict) -> list[Dict[str, Any]]:
        A, B, c, c_dot, expand_dim = canonical_inputs(args['A'], args['B'], args['c'], args['c_dot'], args['expand_dim'])
        batches, M, K, N, d = dimensions(A.shape, B.shape, c.shape, args['power'], args['d_tile'])
        power, d_tile = args['power'], args['d_tile']
        D_tile = d_tile ** power
        configs = []
        mma_sympow_bwd_configurator = create_configurator(ADVANCED_FILTERS + [partial(smem_filter, d, power, d_tile)])
        cfgs = mma_sympow_bwd_configurator((M, N, K, batches), A.dtype, th.float32, D_tile, None, None, smempipe=smempipe, regpipe=regpipe, use_ldsm=use_ldsm, swizzle=swizzle)
        configs += cfgs
        SmemAccI = Tuple(*[Int(1) for i in range(power)])
        for cfg in configs:
            cfg['SmemAccI'] = SmemAccI
        return configs
    return configurator

def hash_fn(args: dict) -> str:
    A, B, c, c_dot, expand_dim = canonical_inputs(args['A'], args['B'], args['c'], args['c_dot'], args['expand_dim'])
    M, N, K, d = A.shape[-2], B.shape[-2], B.shape[-1], c.shape[-2]
    key = f"{A.dtype}-{B.dtype}-{c.dtype}-M_mod128_{M % 128}-N_mod128_{N % 128}-K_mod128_{K % 128}-d{d}-{expand_dim}-{args['power']}-{args['d_tile']}"
    return key

@make_binding(cache=ConfigTimingCache('mma_sympow_bwd', hash_fn),
          sweep=make_configurator(smempipe=(1,2), regpipe=(0,1), use_ldsm=True, swizzle=1))
def binding(A, B, c, c_dot, expand_dim, power, d_tile, scale_A, duplicate_correction, MNKTileShape, MNKAtomPlacement, Atom, smempipe, regpipe, use_ldsm, swizzle, SmemAccI):
    binding_cfg = BindingCfg.from_args(A, B, c, c_dot, expand_dim, power, d_tile, scale_A, duplicate_correction, MNKTileShape, MNKAtomPlacement, Atom, smempipe, regpipe, use_ldsm, swizzle, SmemAccI)
    name = "mma_sympow_bwd"
    logging.debug(f"Calling {name} with binding_cfg={binding_cfg}")
    return_code = jit(name=name, code=str(binding_cfg.source))(A, B, c, c_dot, scale_A)
    if return_code != 0:
        raise RuntimeError(f"Error during kernel execution. Failed with error code: {return_code}")

