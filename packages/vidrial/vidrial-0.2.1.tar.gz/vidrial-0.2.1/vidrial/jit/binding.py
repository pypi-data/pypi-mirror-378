import inspect
import copy
from typing import Callable, Any
from functools import wraps
from vidrial.jit.tuner import tune_and_update
from vidrial.jit.timingcache import ConfigTimingCache
from vidrial.jit.package import register_config_cache
from vidrial.jit.settings import settings, PickAny, PickBest
import logging
logger = logging.getLogger(__name__)

def plot_timings(fn: Callable, timings: list[dict]):
    """ Plot the timings of the configurations.
    """
    name = f"timing_{fn.__module__}.{fn.__qualname__}.png"
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.set_loglevel('error')  # Silence all non-error logs
    except Exception as e:
        logger.warning("matplotlib is not installed, skipping timing plot")
        return
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(timings)), [t['time'] for t in timings], label=f'Timing for {fn.__module__}.{fn.__qualname__}')
    plt.xlabel('Configuration Index')
    plt.ylabel('Time (ms)')
    plt.legend()
    plt.savefig(name)

def make_binding(cache: ConfigTimingCache, sweep: list[dict] | Callable) -> Callable:
    """ Decorator for picking the best configuration from a config cache object when running a 
    function, optionally run a sweep of configurations to pick the best one when cache misses. 
    

    Canonical usage:
    ```python
        cache = ConfigTimingCache('fn', lambda args: args['X'].shape)
        def sweep(args: dict) -> list[dict]:
            return [
                {'tile_1': 32, 'tile_2': 32, 'thread_num': 32},
                {'tile_1': 64, 'tile_2': 64, 'thread_num': 64},
            ]

        @make_binding(cache, sweep=sweep)
        def fn(X, Y, tile_1, tile_2, thread_num) -> torch.Tensor:
            ...

        fn(X, Y)
    ```
    where the best configuration is picked from the set of configurations that are provided by the decorator.

    There are 3 places where the the configuration can be picked from:
    1. TuningCache: If a given set of argument hashes to a key that is in the cache, the best configuration is picked from the cache.
    2. Sweeping: If cache misses and a sweep is provided, the decorator will run a sweep of configurations and pick the best one (and optionally update the cache).

    It is also possible to bypass the decorator entirely by calling the function with a complete specification of configuration.

    The above semantics are exemplified below:
    
    ```python
        @make_binding(cache)
        def fn(X: torch.Tensor, Y: torch.Tensor, tile_1: int, tile_2: int, thread_num: int) -> torch.Tensor:
            ...

        fn(X, Y) // rely on TuningCache, fails if no cache is found
    ```

    ```python
        @make_binding(cache, sweep=sweep)
        def fn(X: torch.Tensor, Y: torch.Tensor, tile_1: int, tile_2: int, thread_num: int) -> torch.Tensor:
            ...

        fn(X, Y) // rely on TuningCache first, then sweep if cache misses
    ```

    ```python
        @make_binding(cache)
        def fn(X: torch.Tensor, Y: torch.Tensor, tile_1: int = 32, tile_2: int = 32, thread_num: int = 32) -> torch.Tensor:
            ...

        fn(X, Y) // rely on TuningCache first, then default kwargs if cache misses
    ```

    ```python
        @make_binding(cache, sweep=sweep)
        def fn(X: torch.Tensor, Y: torch.Tensor, tile_1, tile_2, thread_num) -> torch.Tensor:
            ...

        fn(X, Y, tile_1=32, tile_2=32, thread_num=32) // bypass the decorator entirely
    ```

    Args:
        cache: A ConfigTimingCache object to store the cache.
        sweep: A list of configurations or a function that takes the arguments and returns a list of configurations to use if the cache is missed.

    Returns:
        A decorator that wraps the function and returns the best configuration.
    """
    assert cache is not None, "cache must be provided"
    register_config_cache(cache)

    def decorator(fn: Callable) -> Callable:
        log_prefix = "function selector | "
        if hasattr(fn, '__qualname__'): # ensure fn can be a magic mock
            log_prefix += f"{fn.__qualname__} | "
        @wraps(fn)
        def _wrapped(*args, **kwargs) -> Any:
            all_arg_names = list(inspect.signature(fn).parameters.keys())
            _args = dict(zip(all_arg_names, args)) | kwargs

            if len(_args) == len(all_arg_names):
                logger.debug(f"{log_prefix}All the arguments are provided, nothing to configure")
                return fn(**_args)

            if _args in cache: 
                logger.info(f"{log_prefix}TimingCache hit at {cache.location}. Run best config")
                if settings.plot_timings:
                    plot_timings(fn, cache.get_timings(_args))
                best_config = cache[_args]
                return fn(**_args, **best_config) # run the best config

            logger.debug(f"{log_prefix}TimingCache miss at {cache.location}. Generating config sweep")
            configs = sweep(_args) if callable(sweep) else copy.copy(sweep)
            logger.debug(f"{log_prefix}Sweep configs: {configs[:10]}...")

            if isinstance(configs, dict) or len(configs) == 1: # a single config
                config = configs if isinstance(configs, dict) else configs[0]
                logger.debug(f"{log_prefix}Sweep produced a single config")
                return fn(**_args, **config)

            assert isinstance(configs, list)
            logger.debug(f"{log_prefix}Sweep produced {len(configs)} configs")
            if len(configs) > settings.max_configs:
                logger.debug(f"{log_prefix}truncating to {settings.max_configs}")
                configs = configs[0:settings.max_configs]
            logger.debug(f"{log_prefix}Policy: {settings.policy}")
            if settings.policy == PickAny:
                if not settings.allow_failure:
                    logger.debug(f"{log_prefix}PickAny mode: Compilation faliures not allowed. Running first config only.")
                    return fn(**_args, **(configs[0]))
                for i, config in enumerate(configs):
                    logger.debug(f"{log_prefix}PickAny mode: Trying config {i} out of {len(configs)}")
                    try:
                        return fn(**_args, **config)
                    except Exception as e:
                        logger.debug(f"{log_prefix}Config {i} failed with error: {e}")
                        continue
                raise ValueError("No valid configs are provided")

            # run the sweep in parallel across max_workers
            if settings.policy == PickBest:
                logger.debug(f"{log_prefix}PickBest mode: Benchmark sweep in parallel across {settings.max_workers} workers")
                timings = tune_and_update(fn, _args, configs,
                                            cache,
                                            num=10,
                                            allow_failure=settings.allow_failure,
                                            no_side_effect=True,
                                            max_workers=min(settings.max_workers, len(configs)),
                                            verbose=settings.verbose)
                if settings.plot_timings:
                    plot_timings(fn, timings)
                best_config = timings[0]['config']
                return fn(**_args, **best_config)
            raise ValueError("Unable to pick and run a config")
        return _wrapped
    
    return decorator
