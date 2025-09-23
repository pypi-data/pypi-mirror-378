import torch as th
from math import comb, factorial, sqrt, prod

def tprod(*xs) -> th.Tensor:
    batch_dims = tuple(xs[0].shape[:-1])
    for xi in xs:
        assert xi.shape[:-1] == batch_dims, f"batch_dims of xi={xi.shape[:-1]} do not match batch_dims={batch_dims}"
    y_shape = batch_dims + tuple([xi.shape[-1] for xi in xs])
    y = th.ones(y_shape, device=xs[0].device, dtype=xs[0].dtype)
    batch_slice = [slice(None)] * len(batch_dims)
    for i in range(len(xs)):
        feature_bcast: List[Union[None, slice]] = [None] * len(xs)
        feature_bcast[i] = slice(None)
        y *= xs[-i-1][batch_slice + feature_bcast]
    return y

def tpow(x, power: int) -> th.Tensor:
    return tprod(*([x]*power))

def tprod_bcast(x, power, dim) -> th.Tensor:
    batch_dims = tuple(x.shape[:-1])
    batch_slice = [slice(None)] * len(batch_dims)
    feature_bcast: List[Union[None, slice]] = [None] * power
    feature_bcast[dim] = slice(None)
    x_bcast = x[batch_slice + feature_bcast]
    return x_bcast

def tprod_bwd(xis, zgrad, power):
    b_dims = len(zgrad.shape) - power
    xigrads = []
    for i in range(power):
        v = zgrad.clone()
        for j in range(power):
            if j != i: v = v * tprod_bcast(xis[-j-1], power, j)
        reduce_dims = [j+b_dims for j in range(power) if j != i]
        xigrad_delta = th.sum(v, dim=tuple(reduce_dims))
        xigrads.append(xigrad_delta)
    return xigrads

def tpow_shape(x_shape, power):
    return th.Size(tuple(x_shape[:-1]) + (x_shape[-1],) * power)

def default_d_tile(d, power):
    """
    Returns the default d_tile for a given d and power.
    """
    default_d_tiles = {
        16: {
            2: 4,
            3: 4,
            4: 2,
        },
        32: {
            2: 8,
            3: 4,
            4: 2
        },
        64: {
            2: 8,
            3: 4,
            4: 2
        }
    }
    try:
        return default_d_tiles[d][power]
    except KeyError:
        return 1
