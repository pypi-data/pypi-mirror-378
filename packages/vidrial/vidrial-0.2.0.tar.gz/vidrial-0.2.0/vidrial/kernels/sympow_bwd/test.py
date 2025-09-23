import pytest
import torch as th
from vidrial.kernels.sympow.dimensions import op_output_shape as fwd_op_output_shape
from vidrial.kernels.sympow.op import op_reference as fwd_op_reference
from vidrial.kernels.sympow_bwd.binding import binding
from vidrial.kernels.sympow_bwd.op import op, op_reference
from vidrial.py_utils.test_utils import  PERMUTATIONS_OF_STRIDES_UP_TO_4D, create_permuted_strides_layout
from vidrial.jit.static.types import Shape, Layout, Int
from vidrial.py_utils.test_utils import diff

XSHAPES_AND_POWERS_AND_TILES = [
    ((1, 4), 2, 1),
    ((1, 4), 3, 1),
    ((1, 4), 3, 2),
    ((1, 8), 3, 2),
    ((1, 8), 3, 4),
    ((1, 8), 4, 4),
    ((4, 4), 3, 1),
    ((4, 4), 3, 2),
    ((4, 8), 3, 2),
    ((4, 8), 3, 4),
    ((1, 4), 2, 4),
    ((1, 8), 2, 4),
    ((1, 4), 3, 2),
    ((16, 32), 2, 4),
    ((2, 16, 32), 2, 4),
    ((16, 32), 3, 4),
    ((16, 32), 4, 4),
    ((128, 64), 2, 4),
]

def test_call_binding():
    X = th.randn(8, 64, device='cuda')
    Zgrad = th.randn(fwd_op_output_shape(X.shape, 2, 8), device='cuda')
    Xgrad = th.empty(X.shape, device='cuda')
    binding(X, Zgrad, Xgrad, 2, 8, True, 1,
            ZFrgShape=Shape(Shape(Int(8), Int(1)), Int(1)),
            SZTileLayout=Layout(Shape(Shape(Int(8), Int(8)), Int(1))),
            smem_acc=[True, True])

@pytest.mark.parametrize("X_shape, power, d_tile", XSHAPES_AND_POWERS_AND_TILES)
@pytest.mark.parametrize("duplicate_correction", [True, False])
def test_binding_autotuned(X_shape, power, d_tile, duplicate_correction):
    Z_shape = fwd_op_output_shape(X_shape, power, d_tile)
    X = th.randn(X_shape, device="cuda")
    Zgrad = th.randn(Z_shape, device="cuda" )
    Xgrad = th.zeros(X_shape, device="cuda")
    binding(X, Zgrad, Xgrad, power, d_tile, duplicate_correction)

@pytest.mark.parametrize("X_shape, power, d_tile", XSHAPES_AND_POWERS_AND_TILES)
@pytest.mark.parametrize("duplicate_correction", [True])
def test_op_vs_ref(X_shape, power, d_tile, duplicate_correction):
    Z_shape = fwd_op_output_shape(X_shape, power, d_tile)
    X = th.randn(X_shape, device="cuda")
    Zgrad = th.randn(Z_shape, device="cuda" )
    Xgrad = op(X, Zgrad, power, d_tile, duplicate_correction)
    Xgrad_ref = op_reference(X, Zgrad, power, d_tile, duplicate_correction)
    diff(Xgrad, Xgrad_ref)

@pytest.mark.parametrize("X_shape, power, d_tile", XSHAPES_AND_POWERS_AND_TILES)
@pytest.mark.parametrize("perm", PERMUTATIONS_OF_STRIDES_UP_TO_4D)
def test_op_generic_strides(X_shape, power, d_tile, perm):
    X = th.randn(X_shape, device="cuda")
    Zgrad = th.randn(fwd_op_output_shape(X_shape, power, d_tile), device="cuda")
    X = create_permuted_strides_layout(X, perm)
    Zgrad = create_permuted_strides_layout(Zgrad, perm)
    # Compare op with op_reference
    Xgrad = op(X, Zgrad, power, d_tile, True)
    Xgrad_ref = op_reference(X, Zgrad, power, d_tile, True)
    diff(Xgrad, Xgrad_ref)

@pytest.mark.parametrize("X_shape, power, d_tile", XSHAPES_AND_POWERS_AND_TILES)
@pytest.mark.parametrize("duplicate_correction", [True, False])
def test_op_vs_fwd_ref_bwd(X_shape, power, d_tile, duplicate_correction):
    """Compares op_reference against the autograd of fwd_op_reference """
    Z_shape = fwd_op_output_shape(X_shape, power, d_tile)
    X = th.randn(X_shape, device="cuda", requires_grad=True)
    Zgrad = th.randn(Z_shape, device="cuda" )
    Z = fwd_op_reference(X, power, d_tile, duplicate_correction)
    Z.backward(Zgrad)
    Xgrad_ref = X.grad.clone()
    Xgrad = op(X, Zgrad, power, d_tile, duplicate_correction)
    diff(Xgrad, Xgrad_ref)