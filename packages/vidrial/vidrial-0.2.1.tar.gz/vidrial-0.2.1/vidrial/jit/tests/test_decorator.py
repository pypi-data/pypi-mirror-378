from functools import wraps
import torch
from unittest.mock import patch, Mock, MagicMock
from vidrial.jit import settings
from vidrial.jit.binding import make_binding, tune_and_update, PickBest, PickAny
from vidrial.jit.tuner import get_fn_name
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.compiler import compile
import time

def add_one(x: torch.Tensor, sleep: float):
    if sleep == 0.:
        raise ValueError("I need some sleep!")
    time.sleep(sleep)
    return x + 1, sleep
def add_one_hash(kwargs):
    x = kwargs['x']
    hash = str(x.shape) + str(x.stride()) 
    hash += str(x.dtype) + str(x.device)
    return hash
add_one_sweep = [{'sleep': 0.}, {'sleep': 0.02}, {'sleep': 0.01}]

def test_policy_pickany(tmp_path):
    with patch('vidrial.jit.binding.tune_and_update', wraps=tune_and_update) as mock_tune_and_update:
        timing_cache = ConfigTimingCache(get_fn_name(add_one), add_one_hash, root=str(tmp_path))
        fn = make_binding(cache=timing_cache, sweep=add_one_sweep)(add_one)
        with settings.set(PickAny, 1):
            x = torch.randn(64)
            y, sleep = fn(x) # Should run with the first version in the sweep
            assert mock_tune_and_update.call_count == 0 # ensure it doesn't tune anything
            assert torch.allclose(y, x + 1)
            assert sleep != 0. # ensure it didn't pick the version that crashes

def test_policy_pickbest(tmp_path):
    with patch('vidrial.jit.binding.tune_and_update', wraps=tune_and_update) as mock_tune_and_update:
        timing_cache = ConfigTimingCache(get_fn_name(add_one), add_one_hash, root=str(tmp_path))
        fn = make_binding(cache=timing_cache, sweep=add_one_sweep)(add_one)
        with settings.set(PickBest, 1):
            x = torch.randn(64)
            fn(x) # First call should tune since cache is new
            assert mock_tune_and_update.call_count == 1
            mock_tune_and_update.reset_mock()
            y, sleep = fn(x) # call again, should have cache hit
            assert mock_tune_and_update.call_count == 0
            assert torch.allclose(y, x + 1)
            assert sleep == 0.01 # ensure it picks the best version that doesn't crash

def test_policy_pickbest_call_sweep(tmp_path):
    timing_cache = ConfigTimingCache(get_fn_name(add_one), add_one_hash, root=str(tmp_path))
    sweep_fn = lambda args: [{'sleep': 0.01}, {'sleep': 0.02}]
    mock_sweep_fn = Mock(side_effect=sweep_fn)
    fn = make_binding(cache=timing_cache, sweep=mock_sweep_fn)(add_one)
    with settings.set(PickBest, 1):
        x = torch.randn(64)
        fn(x) # First call should tune since cache is new
        assert mock_sweep_fn.call_count == 1
        fn(x) # call again, should not call the sweep because there is a cache hit
        assert mock_sweep_fn.call_count == 1

def test_bypass(tmp_path):
    timing_cache = ConfigTimingCache(get_fn_name(add_one), add_one_hash, root=str(tmp_path))
    sweep_fn = lambda args: [{'sleep': 0.01}, {'sleep': 0.02}]
    mock_sweep_fn = Mock(side_effect=sweep_fn)
    mock_call_tracker = []
    @wraps(add_one)
    def mock_add_one(*args, **kwargs):
        nonlocal mock_call_tracker
        mock_call_tracker.append((args, kwargs))
        return add_one(*args, **kwargs)
    fn = make_binding(cache=timing_cache, sweep=mock_sweep_fn)(mock_add_one)
    x = torch.randn(64)
    fn(x, sleep=0.01) # Call with all the arguments which should bypass any sweep call
    assert mock_sweep_fn.call_count == 0
    assert len(mock_call_tracker) == 1
    assert mock_call_tracker[0][1]['sleep'] == 0.01
