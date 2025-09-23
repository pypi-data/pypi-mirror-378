import torch as th
from vidrial.kernels.sympow.interface import interface_reference as sympow_reference
from vidrial.kernels.sympow.dimensions import sympow_shape
from vidrial.kernels.mma_sympow_bwd.interface import interface as mma_sympow_bwd
from vidrial.kernels.sympow_mma.binding import binding
from vidrial.kernels.sympow_mma.dimensions import op_output_shape

@th.library.custom_op("vidrial::sympow_mma", mutates_args=())
def op(A: th.Tensor, B: th.Tensor, expand_dim: int, power: int, d_tile: int = 1, scale_A: float = 1.0, duplicate_correction: bool = True) -> th.Tensor:
    """ Compute sympow(A,power,d_tile,expand_dim) @ B

    Input shapes:
        A: [P, M, d] or [P, d, K] - Left matrix
        B: [P, K, N] - Right matrix
        expand_dim: int - Dimension to expand in A (-1 for expand K, -2 for expand M)
        power: int - Power of the symmetric power
        d_tile: int - Tile size for the operation
        duplicate_correction: bool - Whether to correct for duplicate elements

    Output shape:
        C: [P, M, N] - Result of expanded A @ B
    """
    C_shape = op_output_shape(A.shape, B.shape, expand_dim, power, d_tile)
    C = th.empty(C_shape, device=A.device, dtype=A.dtype)
    binding(A, B, C, expand_dim, power, d_tile, scale_A, duplicate_correction) # type: ignore
    return C

@op.register_fake
def op_fake(A: th.Tensor, B: th.Tensor, expand_dim: int, power: int, d_tile: int, scale_A: float = 1.0, duplicate_correction: bool = True):
    eA_shape = sympow_shape(A.shape, power, d_tile, expand_dim%A.ndim)
    return th.empty((*A.shape[:-2], eA_shape[-2], B.shape[-1]), device=A.device, dtype=A.dtype)


# ------------- Backward Implementation -------------

def op_setup(ctx, inputs, output):
    A, B, expand_dim, power, d_tile, scale_A, duplicate_correction = inputs
    ctx.save_for_backward(A, B)
    ctx.expand_dim = expand_dim
    ctx.power = power
    ctx.d_tile = d_tile
    ctx.scale_A = scale_A
    ctx.duplicate_correction = duplicate_correction
def bwd_dA(A, B, dC, expand_dim, power, d_tile, scale_A, duplicate_correction):
    A, B, c = dC, B.transpose(-1, -2), A
    return mma_sympow_bwd(A, B, c, expand_dim, power, d_tile, scale_A, duplicate_correction)
def bwd_dB(A, B, dC, expand_dim, power, d_tile, scale_A, duplicate_correction):
    expand_dim = {-1: -2, -2: -1}[expand_dim%A.ndim-A.ndim]
    A = A.transpose(-1, -2)
    return op(A, dC, expand_dim, power, d_tile, scale_A, duplicate_correction)
def op_backward(ctx, dC):
    A, B = ctx.saved_tensors
    dA = bwd_dA(A, B, dC, ctx.expand_dim, ctx.power, ctx.d_tile, ctx.scale_A, ctx.duplicate_correction)
    dB = bwd_dB(A, B, dC, ctx.expand_dim, ctx.power, ctx.d_tile, ctx.scale_A, ctx.duplicate_correction)
    assert dA.shape == A.shape
    assert dB.shape == B.shape
    return dA, dB, None, None, None, None
th.library.register_autograd("vidrial::sympow_mma", op_backward, setup_context=op_setup)


# ------------- Reference Implementation -------------

def op_reference(A: th.Tensor, B: th.Tensor, dim, power, d_tile=1, scale_A=1.0, duplicate_correction=True):
    eA = sympow_reference(A, power, d_tile, dim, duplicate_correction)
    eA = eA * scale_A
    return eA @ B
