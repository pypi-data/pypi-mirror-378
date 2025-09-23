from typing import Callable
from contextlib import contextmanager
import copy
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class ModePickAny:
    __repr__ = lambda self: "PickAny"

class ModePickBest:
    __repr__ = lambda self: "PickBest"

PickAny = ModePickAny()
PickBest = ModePickBest()

@dataclass
class Settings:
    policy: ModePickAny | ModePickBest = PickAny
    max_workers: int = 32
    allow_failure: bool = True
    verbose: bool = False
    max_configs: int = 512
    precompile: bool = False
    plot_timings: bool = False

    @contextmanager
    def set(self,
            policy: ModePickAny | ModePickBest | None = None,
            max_workers: int | None = None,
            allow_failure: bool | None = None,
            verbose: bool | None = None,
            max_configs: int | None = None,
            precompile: bool | None = None,
            plot_timings: bool | None = None):
        old_settings = copy.copy(self)
        if policy is not None:
            logger.info(f"Setting policy to {policy}")
            assert isinstance(policy, (ModePickAny, ModePickBest))
            self.policy = policy
        if max_workers is not None:
            logger.info(f"Setting max_workers to {max_workers}")
            assert isinstance(max_workers, int)
            self.max_workers = max_workers
        if allow_failure is not None:
            logger.info(f"Setting allow_failure to {allow_failure}")
            assert isinstance(allow_failure, bool)
            self.allow_failure = allow_failure
        if verbose is not None:
            logger.info(f"Setting verbose to {verbose}")
            assert isinstance(verbose, bool)
            self.verbose = verbose
        if max_configs is not None:
            logger.info(f"Setting max_configs to {max_configs}")
            assert isinstance(max_configs, int)
            self.max_configs = max_configs
        if precompile is not None:
            logger.info(f"Setting precompile to {precompile}")
            assert isinstance(precompile, bool)
            self.precompile = precompile
        if plot_timings is not None:
            logger.info(f"Setting plot_timings to {plot_timings}")
            if self.policy != PickBest and plot_timings:
                logger.warning("plot_timings is only effective in PickBest mode")
            assert isinstance(plot_timings, bool)
            self.plot_timings = plot_timings
        try:
            yield
        finally:
            if self.precompile:
                import vidrial.jit.jit as jit # Lazy import to avoid circular dependency
                jit.precompile()
            logger.info(f"Restoring old settings")
            self.policy = old_settings.policy
            self.max_workers = old_settings.max_workers
            self.allow_failure = old_settings.allow_failure
            self.verbose = old_settings.verbose
            self.max_configs = old_settings.max_configs
            self.precompile = old_settings.precompile
            self.plot_timings = old_settings.plot_timings

# Global settings instance
settings = Settings()
