
from vidrial.kernels.sympow_mma.op import op, op_reference

""" Functional interface """
def sympowA_mm(A, B, dim, power, d_tile):
    return op(A, B, dim, power, d_tile)
def sympowA_mma(A, B, C, dim, power, d_tile):
    return C + sympowA_mm(A, B, dim, power, d_tile)
def sympowA_gemm(α, A, B, β, C, dim, power, d_tile):
    return β * C + α * sympowA_mm(A, B, dim, power, d_tile)

def sympowA_mm_reference(A, B, dim, power, d_tile):
    return op_reference(A, B, dim, power, d_tile)
def sympowA_mma_reference(A, B, C, dim, power, d_tile):
    """ A, B, C -> D = C + A @ B """
    return C + sympowA_mm_reference(A, B, dim, power, d_tile)
def sympowA_gemm_reference(α, A, B, β, C, dim, power, d_tile):
    """ α, A, B, β, C -> D = β * C + α * A @ B """
    return β * C + α * sympowA_mm_reference(A, B, dim, power, d_tile)


""" Inplace interface """
# def sympowA_mm_(A, B, D, dim, power, d_tile):
#     D[:] = sympowA_mm(A, B, dim, power, d_tile)
def sympowA_mma_(A, B, C, dim, power, d_tile):
    C[:] = sympowA_mma(A, B, C, dim, power, d_tile)
def sympowA_gemm_(α, A, B, β, C, dim, power, d_tile):
    C[:] = sympowA_gemm(α, A, B, β, C, dim, power, d_tile)

def sympowA_mm_reference_(A, B, C, dim, power, d_tile):
    C[:] = sympowA_mm_reference(A, B, dim, power, d_tile)
def sympowA_mma_reference_(A, B, C, dim, power, d_tile):
    C[:] = sympowA_mma_reference(A, B, C, dim, power, d_tile)
def sympowA_gemm_reference_(α, A, B, β, C, dim, power, d_tile):
    C[:] = sympowA_gemm_reference(α, A, B, β, C, dim, power, d_tile)
