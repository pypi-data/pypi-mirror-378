"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import functools
import logging
import os
from .state import PartialState
class MultiProcessAdapter(logging.LoggerAdapter):
    @staticmethod
    def _should_log(main_process_only):
        state = PartialState()
        return not main_process_only or (main_process_only and state.is_main_process)
    def log(self, level, msg, *args, **kwargs):
        if PartialState._shared_state == {}: raise RuntimeError("You must initialize the sapiens_accelerator state by calling either `PartialState()` or `Accelerator()` before using the logging utility.")
        main_process_only = kwargs.pop("main_process_only", True)
        in_order = kwargs.pop("in_order", False)
        kwargs.setdefault("stacklevel", 2)
        if self.isEnabledFor(level):
            if self._should_log(main_process_only):
                msg, kwargs = self.process(msg, kwargs)
                self.logger.log(level, msg, *args, **kwargs)
            elif in_order:
                state = PartialState()
                for i in range(state.num_processes):
                    if i == state.process_index:
                        msg, kwargs = self.process(msg, kwargs)
                        self.logger.log(level, msg, *args, **kwargs)
                    state.wait_for_everyone()
    @functools.lru_cache(None)
    def warning_once(self, *args, **kwargs): self.warning(*args, **kwargs)
def get_logger(name: str, log_level: str = None):
    if log_level is None: log_level = os.environ.get("SAPIENS_ACCELERATOR_LOG_LEVEL", None)
    logger = logging.getLogger(name)
    if log_level is not None:
        logger.setLevel(log_level.upper())
        logger.root.setLevel(log_level.upper())
    return MultiProcessAdapter(logger, {})
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
