import pytest
import torch as th
from vidrial.kernels.sympow.dimensions import sympow_dim
from vidrial.py_utils.test_utils import diff, PERMUTATIONS_OF_STRIDES_UP_TO_4D, create_permuted_strides_layout
from vidrial.kernels.sympow.interface import interface as sympow
from vidrial.kernels.sympow.interface import interface_reference as sympow_reference
from vidrial.kernels.sympow_mma.binding import binding
from vidrial.kernels.sympow_mma.op import op, op_reference

import logging

logging.basicConfig(level=logging.DEBUG) 


PROBLEM_SHAPES = [
    ((3,2), 16, 64, 32, 2, 8, False),
    ((1,), 16, 64, 32, 2, 8, False),
    ((1,1), 16, 64, 32, 2, 8, True),
    ((10,), 16, 1, 32, 2, 8, True),
    ((2,), 16, 64, 1, 2, 8, True),
    ((2,3,4), 32, 10, 4, 3, 4, True),
    ((6,), 64, 1, 128, 2, 8, True),
]

def setup(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction):
    D = sympow_dim(d, p, d_tile)
    M, K = {-2: (D, R), -1: (R, D)}[expand_dim]
    A_shape = batch_dims+{-2:(d, K), -1:(M, d)}[expand_dim]
    A = th.randn(A_shape, device="cuda")
    B = th.randn(batch_dims+(K, N), device="cuda")
    C = th.randn(batch_dims+(M, N), device="cuda")
    return A, B, C

@pytest.mark.parametrize("batch_dims,d,N,R,p,d_tile,duplicate_correction", PROBLEM_SHAPES)
@pytest.mark.parametrize("expand_dim", [-1, -2 ])
def test_binding_autotuned(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction):
    A, B, C = setup(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction)
    binding(A, B, C, expand_dim, p, d_tile, 1., duplicate_correction) # type: ignore
    eA_ref = sympow_reference(A, p, d_tile, expand_dim, duplicate_correction)
    C_ref = eA_ref @ B
    diff(C, C_ref, atol=1e-1, rtol=1e-1)

@pytest.mark.parametrize("batch_dims,d,N,R,p,d_tile,duplicate_correction", PROBLEM_SHAPES)
@pytest.mark.parametrize("expand_dim", [-1, -2 ])
def test_op(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction):
    A, B, dC = setup(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction)
    A.requires_grad, B.requires_grad = True, True
    C = op(A, B, expand_dim, p, d_tile, duplicate_correction)
    C.backward(dC)
    assert A.grad is not None and B.grad is not None
    dA, dB = A.grad.clone(), B.grad.clone()
    A.grad, B.grad = None, None

    C_ref = op_reference(A, B, expand_dim, p, d_tile, duplicate_correction)
    C_ref.backward(dC)
    assert A.grad is not None and B.grad is not None
    dA_ref, dB_ref = A.grad.clone(), B.grad.clone()
    A.grad, B.grad = None, None

    diff(C, C_ref, atol=1e-1, rtol=1e-1)
    diff(dA, dA_ref, atol=1e-1, rtol=1e-1)
    diff(dB, dB_ref, atol=1e-1, rtol=1e-1)

def test_non_standard_strides(batch_dims=(2,3,4), d=16, N=16, R=32, p=2, d_tile=16, expand_dim=-1, duplicate_correction=True):
    A, B, C = setup(batch_dims, d, N, R, p, d_tile, expand_dim, duplicate_correction)
    non_standard_stride = lambda X: X.transpose(2, 1).contiguous().transpose(2, 1)
    A, B, C = non_standard_stride(A), non_standard_stride(B), non_standard_stride(C)
    binding(A, B, C, expand_dim, p, d_tile, 1., duplicate_correction) # type: ignore
    eA_ref = sympow_reference(A, p, d_tile, expand_dim, duplicate_correction)
    C_ref = eA_ref @ B
    diff(C, C_ref, atol=1e-1, rtol=1e-1)
