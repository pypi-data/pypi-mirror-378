import pytest
import torch as th
from math import prod
from vidrial.kernels.reduce.binding import binding
from vidrial.py_utils.test_utils import diff

class SumReduce:
    str = "return a + b;"
    reference = lambda X, reduce_dims: th.sum(X, dim=reduce_dims)

class MaxReduce:
    str = "return a > b ? a : b;"
    @staticmethod
    def reference(X, reduce_dims):
        for i in reversed(sorted(reduce_dims)):
            X = th.max(X, dim=i).values
        return X

@pytest.mark.parametrize(
    ["dtype", "reduce_fn", "X_shape", "reduce_dims", "X_tile_shape", "thread_num"],
    [
        (int, SumReduce, (4, 8), (0,), None, 1),
        (int, SumReduce, (4, 8), (0,), (1,1), 1),
        (int, SumReduce, (4, 8), (1,), None, 2),
        (int, SumReduce, (4, 8, 16), (2,), None, 4),
        # (int, SumReduce, (4, 8), (0, 1), None, 8), # TODO: support reducing all the dimensions
        (th.int32, SumReduce, (4, 8, 16), (0,2), None, 16),
        (th.int32, SumReduce, (128, 32), (0,), None, 64),
        (th.int32, SumReduce, (128, 32), (0,), None, 32),
        (th.int32, SumReduce, (128, 32), (0,), (32, 32), 32),
        (th.int32, SumReduce, (16, 8), (0,), None, 32),
        (th.int32, SumReduce, (4, 8), (0,), None, 32),
        (th.int32, SumReduce, (128, 1024), (0,), (128, 32), 32),
        (th.int32, SumReduce, (128, 32), (0,), (128, 32), 32),
        (th.int32, SumReduce, (128, 64), (0,), (128, 32), 32),
        (th.float, SumReduce, (256, 1024), (1,), (4, 1024), 32),
        (th.float, SumReduce, (256, 1024), (0,), (4, 1024), 32),
        (th.float16, SumReduce, (128, 1024), (0,), (128, 32), 32),
        (int, MaxReduce, (4, 8), (0,), None, 1),
        (int, MaxReduce, (4, 8), (1,), None, 2),
        (int, MaxReduce, (4, 8, 16), (2,), None, 4),
        (th.uint8, MaxReduce, (4, 8, 16), (0,1), None, 16),
        (th.int32, MaxReduce, (128, 32), (0,), None, 64),
        (th.int32, MaxReduce, (128, 32), (0,), (64, 32), 64),
        (th.int32, MaxReduce, (128, 32), (0,), (16, 16), 32),
        (th.int32, MaxReduce, (16, 8), (0,), None, 32),
    ]
)
def test_binding(dtype, reduce_fn, X_shape, reduce_dims, X_tile_shape, thread_num):
    X_tile_shape = X_shape if X_tile_shape is None else X_tile_shape
    x_shape = [X_shape[i] for i in range(len(X_shape)) if i not in reduce_dims]
    X = th.randn(X_shape, device='cuda').to(dtype)
    x = th.empty(x_shape, device='cuda', dtype=dtype)
    binding(X, x, reduce_fn.str, reduce_dims, X_tile_shape, thread_num)
    x_ref = reduce_fn.reference(X, reduce_dims)
    tol = 1e-1 if dtype == th.float16 else 1e-4
    diff(x, x_ref, atol=tol, rtol=tol)