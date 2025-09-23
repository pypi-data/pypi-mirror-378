import pytest
import torch as th
from math import sqrt
from vidrial.kernels.sympow.dimensions import sympow_dim
from vidrial.jit.static import Shape, Layout, Int, Tuple
from vidrial.kernels.mma_sympow_bwd.binding import binding
from vidrial.kernels.mma_sympow_bwd.interface import interface, interface_reference
from vidrial.py_utils.test_utils import diff
from vidrial.jit import settings, PickAny

def test_binding():
    d, power, d_tile = 64, 2, 8
    D = sympow_dim(d, power, d_tile)
    M, N, K, batches = D, 16, 32, (1, 1)
    A = th.randn(batches + (M, K), device="cuda", dtype=th.float16)
    B = th.randn(batches + (K, N), device="cuda", dtype=th.float16)
    c = th.randn(batches + (d, N), device="cuda", dtype=th.float16)
    c_dot = th.empty(batches + (d, N), device="cuda", dtype=th.float16)

    binding(
        A, B, c, c_dot, -2, power, d_tile, 1.0,
        duplicate_correction=True,
        MNKTileShape=Shape(Int(64), Int(16), Int(32)), 
        MNKAtomPlacement=Shape(Int(1), Int(1), Int(1)), 
        Atom="SM80_16x8x8_F16F16F16F16_TN", 
        smempipe=1, 
        regpipe=2, 
        use_ldsm=True, 
        swizzle=0,
        SmemAccI=Tuple(*[Int(1) for i in range(power)])
    )

def test_call_interface_expand_M():
    d, power, d_tile = 64, 2, 8
    D = sympow_dim(d, power, d_tile)
    M, N, K, P = D, 16, 32, 8
    A = th.randn((P, M, K), device="cuda")
    B = th.randn((P, K, N), device="cuda")
    c = th.randn((P, d, N), device="cuda")
    c_dot = interface(A, B, c, -2, power, d_tile)

def test_call_interface_expand_N():
    d, power, d_tile = 64, 2, 8
    D = sympow_dim(d, power, d_tile)
    M, N, K, P = 16, D, 32, 8
    A = th.randn((P, M, K), device="cuda")
    B = th.randn((P, K, N), device="cuda")
    c = th.randn((P, M, d), device="cuda")
    c_dot = interface(A, B, c, -1, power, d_tile)

@pytest.mark.parametrize("d, power, d_tile, N, K, batches, dtype", [
    (4, 2, 4, 8, 4, (1,), th.float32),
    (64, 2, 8, 64, 128, (4,2), th.float32),
    (64, 2, 1, 64, 1, (128,2,1), th.float32),
    (4, 2, 4, 8, 8, (1,), th.bfloat16),
    (64, 2, 8, 64, 128, (4,2), th.bfloat16),
    (64, 2, 1, 64, 1, (128,2,1), th.bfloat16),
    (4, 2, 4, 8, 8, (1,), th.float16),
    (64, 2, 8, 64, 128, (4,2), th.float16),
    (64, 2, 1, 64, 1, (128,2,1), th.float16)
])
def test_interface_matches_reference(d, power, d_tile, N, K, batches, dtype):
    M = sympow_dim(d, power, d_tile)
    th.manual_seed(42)
    A = th.randn(batches + (M, K), device="cuda", dtype=dtype) / sqrt(M + K)
    B = th.randn(batches + (K, N), device="cuda", dtype=dtype) / sqrt(K + N)
    c = th.randn(batches + (d, N), device="cuda", dtype=dtype) / sqrt(d + N)
    with settings.set(policy=PickAny, allow_failure=False, verbose=True):
        c_dot = interface(A, B, c, -2, power, d_tile)
    c_dot_ref = interface_reference(A, B, c, -2, power, d_tile)
    tol = 1e-1 if dtype == th.bfloat16 else 1e-3
    print(tol, dtype)
    diff(c_dot, c_dot_ref, atol=tol, rtol=tol, verbose=True)
