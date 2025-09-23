import torch as th
from vidrial.kernels.flash.binding import binding

#TODO: support GQA, non-causal, etc
@th.library.custom_op("vidrial::flash", mutates_args=())
def op(Q: th.Tensor, K: th.Tensor, V: th.Tensor, softmax_scale: float = None) -> tuple[th.Tensor, th.Tensor]:
    """ Computes flash attention

    Arguments:
        Q: (batch_size, seqlen_q, nheads, head_dim), the query tensor
        K: (batch_size, seqlen_k, nheads, head_dim), the key tensor    
        V: (batch_size, seqlen_k, nheads, value_dim), the value tensor
        softmax_scale: float. The scaling of QK^T before applying softmax.
            Default to 1 / sqrt(head_dim).

    Returns:
        O: (batch_size, seqlen_q, nheads, value_dim), the output tensor
        l: (batch_size, seqlen_q, nheads), the log-sum-of-exponentials factors
    """
    batch_size, seqlen, nheads, head_dim, value_dim = *Q.shape, V.shape[-1]
    assert K.shape == (batch_size, seqlen, nheads, head_dim), f"Invalid K shape: {K.shape}"
    assert V.shape == (batch_size, seqlen, nheads, value_dim), f"Invalid V shape: {V.shape}"

    if softmax_scale is None:
        softmax_scale = 1.0 / head_dim**0.5
    O = th.empty(Q.shape[:-1] + (value_dim,), device=Q.device, dtype=Q.dtype)
    l = th.empty(Q.shape[:-1], device=Q.device, dtype=th.float32)
    Q, K, V, O, l = map(lambda x: x.transpose(1, 2), (Q, K, V, O, l)) # [b, h, t, d]
    binding(Q, K, V, O, l, softmax_scale) # type: ignore
    O, l = map(lambda x: x.transpose(1, 2), (O, l)) # [b, t, h, d]
    return O, l

@op.register_fake
def op_fake(Q: th.Tensor, K: th.Tensor, V: th.Tensor, softmax_scale: float = None):
    return th.empty(Q.shape[:-1] + (V.shape[-1],), device=Q.device, dtype=Q.dtype), th.empty(Q.shape[:-1], device=Q.device, dtype=th.float32)


# ------------- Backward Implementation -------------

def op_setup(ctx, inputs, output):
    Q, K, V, O, l, softmax_scale = inputs
    ctx.save_for_backward(Q, K, V)
    ctx.softmax_scale = softmax_scale
def op_backward(ctx, dO, dl):
    raise NotImplementedError("Backward pass for flash attention is not implemented using vidrial")
th.library.register_autograd("vidrial::flash", op_backward, setup_context=op_setup)


def op_reference(Q, K, V, O, l):
    S = (Q @ K.transpose(-1, -2)).to(th.float32)
    b, tq, tk = S.shape
    M = th.tril(th.ones(tq, tk, device=S.device, dtype=th.bool)).unsqueeze(0).expand(b, -1, -1)
    S = S.masked_fill(~M, float('-inf'))
    S = S - S.max(dim=-1, keepdim=True).values
    P = th.exp(S)
    l = P.sum(dim=-1)
    P = (P / l.unsqueeze(-1)).to(O.dtype)
    O = P @ V
    return O, l