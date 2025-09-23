from dataclasses import dataclass
from functools import lru_cache
import torch as th
from math import prod
from vidrial.jit.static.types import Shape, Layout, Int
from vidrial.jit.static.util import torch_dtype_to_c
from vidrial.jit.static.util import layout_from_shape_stride, nested_constructor
from vidrial.jit.jit import jit, render
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.binding import make_binding
from vidrial.kernels.mma_configurator import dtype_to_bytes


# ------------------- Source Code -------------------
@dataclass
class SourceCode:
    T: str
    fn_str: str # c++ for the reduction function
    GXSlab: Layout
    GxSlab: Layout
    thread_num: int
    XTileShape: Shape
    @property
    def template(self):
        return """
# include <cuda.h>
# include <cuda_runtime.h>
#include <cute/tensor.hpp>
#include "kernels/reduce/kernel.cuh"
#include "kernels/reduce/reduce_utils.cuh"
using namespace cute;
using namespace vidrial;
using T = {T};
struct Fn {
    template<typename Ta, typename Tb> CUTE_HOST_DEVICE
    auto operator()(Ta a, Tb b) {
        {fn_str}
    }
};
extern "C" void launch(void* _X, void* _x) {
    auto X = reinterpret_cast<T*>(_X);
    auto x = reinterpret_cast<T*>(_x);
    auto cfg = ReduceKernelCfg<T, {thread_num}, {XTileShape}, {GXSlab}, {GxSlab}>{};
    launch_reduce_kernel(cfg, X, x, Fn{});
}
"""
    def __str__(self):
        return render(self.template, self.__dict__)

# ------------------- Binding -------------------
@dataclass
class BindingCfg:
    fn_str: str
    reduce_dims: tuple[int, ...]
    X_shape: tuple[int, ...]
    x_shape: tuple[int, ...] # Same dims as X_shape but with the reduce_dim removed
    X_stride: tuple[int, ...]
    x_stride: tuple[int, ...]
    X_tile_shape: tuple[int, ...]
    thread_num: int
    dtype: th.dtype
    @classmethod
    def from_args(cls, X, x, fn, reduce_dims, X_tile_shape, thread_num):
        assert X.device.type == x.device.type == 'cuda', f"Invalid {X.device}, {x.device}."
        assert X.dtype == x.dtype
        dtype = X.dtype
        return cls(fn, reduce_dims, X.shape, x.shape, X.stride(), x.stride(), X_tile_shape, thread_num, dtype)
    @property
    def source(self):
        n = len(self.X_shape)
        reduce_dims = [i for i in range(n) if i in self.reduce_dims]
        batch_dims = [i for i in range(n) if i not in self.reduce_dims]
        X_dims = (reduce_dims, batch_dims)
        GXSlab = layout_from_shape_stride(self.X_shape, self.X_stride, X_dims)
        GxSlab = layout_from_shape_stride(self.x_shape, self.x_stride)
        XTileShape = nested_constructor(X_dims)(self.X_tile_shape, Shape)
        sc = SourceCode(
            T=torch_dtype_to_c(self.dtype),
            fn_str=self.fn_str,
            GXSlab=GXSlab,
            GxSlab=GxSlab,
            thread_num=self.thread_num,
            XTileShape=XTileShape,
        )
        return sc

def configurations(binding_args: dict) -> list[dict]:
    """ Given any args to binding, 
    Currently returns a single reasonable configuration.
    TODO: Return a better configuration sweep
    """
    rest_args = {}
    if 'X_tile_shape' not in binding_args:
        X_tile_shape = [min(x, 16) for x in binding_args['X'].shape]
        rest_args['X_tile_shape'] = X_tile_shape
    if 'thread_num' not in binding_args:
        rest_args['thread_num'] = 32
    return [rest_args]

def sweep_key(binding_args: dict) -> str:
    X, x, reduce_dims = binding_args['X'], binding_args['x'], binding_args['reduce_dims']
    msg = f"X:shape={X.shape},stride={X.stride()}-"
    msg += f"x:shape={x.shape},stride={x.stride()}-"
    msg += f"reduce_dims={reduce_dims}"
    return msg

@make_binding(cache=ConfigTimingCache('reduce', sweep_key),
          sweep=configurations)
def binding(X, x, fn, reduce_dims, X_tile_shape, thread_num):
    binding_cfg = BindingCfg.from_args(X, x, fn, reduce_dims, X_tile_shape, thread_num)
    jit(name = "reduce",
        code = str(binding_cfg.source),
    )(X, x)
