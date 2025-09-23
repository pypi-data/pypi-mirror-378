from vidrial.kernels.sympow.dimensions import sympow_dim, sympow_shape

def problem_shape(A_shape, B_shape, C_shape, dim, power, d_tile):
    ndim = len(A_shape)
    batches, M, N, K, d = tuple(C_shape[:-2]), C_shape[-2], C_shape[-1], B_shape[-2], A_shape[dim]
    assert len(batches) >= 1
    D = sympow_dim(d, power, d_tile)
    eA_shape = sympow_shape(A_shape, power, d_tile, dim)
    assert dim % ndim - ndim in [-1,-2], f"expand_dim={dim} must corrsepond M or K (-2 or -1)"
    assert eA_shape == batches + (M, K), f"eA_shape={eA_shape} != batches + (M, K)={batches + (M, K)}"
    tmp = list(eA_shape)
    tmp[dim] = d
    assert A_shape == tuple(tmp)
    assert B_shape == batches + (K, N)
    assert C_shape == batches + (M, N)
    return batches, M, N, K, d, D

def op_output_shape(A_shape, B_shape, expand_dim, power, d_tile) -> tuple[int, int, int]:
    ndim = len(A_shape)
    batches, K, N = tuple(B_shape[:-2]), B_shape[-2], B_shape[-1]
    d = A_shape[expand_dim]
    expand_M = expand_dim%ndim-ndim == -2
    M = sympow_dim(d, power, d_tile) if expand_M  else A_shape[-2]
    C_shape = batches+(M, N)
    problem_shape(A_shape, B_shape, C_shape, expand_dim, power, d_tile) # Check that the shape is valid
    return C_shape
