from vidrial.kernels.flash.op import op, op_reference

""" Functional interface """
def flash(Q, K, V, softmax_scale=None):
    if softmax_scale is None:
        softmax_scale = 1.0 / Q.shape[-1]**0.5
    O, _ = op(Q, K, V, softmax_scale)
    return O

def flash_reference(Q, K, V, softmax_scale=None):
    if softmax_scale is None:
        softmax_scale = 1.0 / Q.shape[-1]**0.5
    O, _ = op_reference(Q, K, V, softmax_scale)
    return O