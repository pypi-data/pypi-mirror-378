import os
os.environ['JIT_PACKAGE_MODE'] = '1'

from vidrial.jit.timer import timeit
from flash_attn.flash_attn_interface import flash_attn_func
from vidrial.jit.settings import settings, PickBest
from vidrial.kernels.flash.op import op as flash_vidrial
from vidrial.py_utils.test_utils import diff
import torch
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

def create_input(b, tq, tk, h, d, e):
    Q = torch.randn(b, tq, h, d, device='cuda', dtype=torch.bfloat16)
    K = torch.ones(b, tk, h, d, device='cuda', dtype=torch.bfloat16)
    V = torch.randn(b, tk, h, e, device='cuda', dtype=torch.bfloat16)
    O = torch.empty(b, tq, h, e, device='cuda', dtype=torch.bfloat16)
    l = torch.empty(b, tq, h, device='cuda', dtype=torch.float32)
    return Q, K, V, O, l

def compare():
    with settings.set(policy=PickBest, max_configs=512, plot_timings=False):
        result = []
        for b, tq, tk, h, d, e in [(1, 1024, 1024, 16, 64, 64),
                                   (1, 1024, 1024, 16, 32, 32)]:
            Q, K, V, O, l = create_input(b, tq, tk, h, d, e)
            O_flash = flash_attn_func(Q, K, V, causal=True)
            O_vidrial, l_vidrial = flash_vidrial(Q, K, V)

            cuda_avg, cuda_std = timeit(flash_vidrial, Q, K, V, num1=10, num2=30)
            flash_avg, flash_std = timeit(flash_attn_func, Q, K, V, causal=True, num1=10, num2=30)
            max_diff = torch.max(torch.abs(O_vidrial - O_flash)).item()
            result.append({
                'b': b,
                'tq': tq,
                'tk': tk,
                'h': h,
                'd': d,
                'e': e,
                'cuda_avg': cuda_avg,
                'cuda_std': cuda_std,
                'flash_avg': flash_avg,
                'flash_std': flash_std,
                'speedup': flash_avg / cuda_avg,
                'max_diff': max_diff
            })
        return pd.DataFrame(result)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    df = compare()
    print(df)