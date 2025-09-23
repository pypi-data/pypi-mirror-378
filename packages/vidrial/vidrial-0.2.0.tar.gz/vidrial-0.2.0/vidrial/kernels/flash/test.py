import torch as th
from itertools import product
from vidrial.jit.settings import settings, PickAny
from flash_attn.flash_attn_interface import flash_attn_func
from vidrial.kernels.flash.op import op as flash_vidrial
from vidrial.py_utils.test_utils import diff
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

with settings.set(policy=PickAny, max_configs=999999, plot_timings=False, max_workers=127):
    th.manual_seed(42)
    results = []
    batch_sizes = [1]
    head_sizes = [8]
    seq_lens = [512, 1024]
    head_dims = [32, 128]
    for b, h, tq, d in product(batch_sizes, head_sizes, seq_lens, head_dims):
        tk = tq
        e = d
        Q = th.randn(b, tq, h, d, device='cuda', dtype=th.bfloat16)
        K = th.randn(b, tk, h, d, device='cuda', dtype=th.bfloat16)
        V = th.randn(b, tk, h, e, device='cuda', dtype=th.bfloat16)
        O, l = flash_vidrial(Q, K, V)
        O_flash = flash_attn_func(Q, K, V, causal=True, softmax_scale=None)
        max_diff = th.max(th.abs(O - O_flash))
        results.append({
            'b': b,
            'h': h,
            'tq': tq,
            'tk': tk,
            'd': d,
            'e': e,
            'max_diff': max_diff.item()
        })
    print(pd.DataFrame(results))
