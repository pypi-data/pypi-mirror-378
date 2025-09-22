"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import base64
import json
import os
from copy import deepcopy
from ..optimizer import SapiensAcceleratordOptimizer
from ..scheduler import SapiensAcceleratordScheduler
from .dataclasses import DistributedType
def get_active_deepspeed_plugin(state):
    if state.distributed_type != DistributedType.DEEPSPEED: raise ValueError("Couldn't retrieve the active `DeepSpeedPlugin` as none were enabled. Please make sure that either `Accelerator` is configured for `deepspeed` or make sure that the desired `DeepSpeedPlugin` has been enabled (`AcceleratorState().select_deepspeed_plugin(name)`) before calling this function.")
    if not isinstance(state.deepspeed_plugins, dict): return state.deepspeed_plugins
    return next(plugin for plugin in state.deepspeed_plugins.values() if plugin.selected)
class HfDeepSpeedConfig:
    def __init__(self, config_file_or_dict):
        if isinstance(config_file_or_dict, dict): config = deepcopy(config_file_or_dict)
        elif os.path.exists(config_file_or_dict):
            with open(config_file_or_dict, encoding="utf-8") as f: config = json.load(f)
        else:
            try:
                config_decoded = base64.urlsafe_b64decode(config_file_or_dict).decode("utf-8")
                config = json.loads(config_decoded)
            except (UnicodeDecodeError, AttributeError, ValueError): raise ValueError(f"Expected a string path to an existing deepspeed config, or a dictionary, or a base64 encoded string. Received: {config_file_or_dict}")
        self.config = config
        self.set_stage_and_offload()
    def set_stage_and_offload(self):
        self._stage = self.get_value("zero_optimization.stage", -1)
        self._offload = False
        if self.is_zero2() or self.is_zero3():
            offload_devices_valid = set(["cpu", "nvme"])
            offload_devices = set([self.get_value("zero_optimization.offload_optimizer.device"), self.get_value("zero_optimization.offload_param.device")])
            if len(offload_devices & offload_devices_valid) > 0: self._offload = True
    def find_config_node(self, ds_key_long):
        config = self.config
        nodes = ds_key_long.split(".")
        ds_key = nodes.pop()
        for node in nodes:
            config = config.get(node)
            if config is None: return None, ds_key
        return config, ds_key
    def get_value(self, ds_key_long, default=None):
        config, ds_key = self.find_config_node(ds_key_long)
        if config is None: return default
        return config.get(ds_key, default)
    def del_config_sub_tree(self, ds_key_long, must_exist=False):
        config = self.config
        nodes = ds_key_long.split(".")
        for node in nodes:
            parent_config = config
            config = config.get(node)
            if config is None:
                if must_exist: raise ValueError(f"Can't find {ds_key_long} entry in the config: {self.config}")
                else: return
        if parent_config is not None: parent_config.pop(node)
    def is_true(self, ds_key_long):
        value = self.get_value(ds_key_long)
        return False if value is None else bool(value)
    def is_false(self, ds_key_long):
        value = self.get_value(ds_key_long)
        return False if value is None else not bool(value)
    def is_zero2(self): return self._stage == 2
    def is_zero3(self): return self._stage == 3
    def is_offload(self): return self._offload
class DeepSpeedEngineWrapper:
    def __init__(self, engine): self.engine = engine
    def backward(self, loss, **kwargs):
        self.engine.backward(loss, **kwargs)
        self.engine.step()
class DeepSpeedOptimizerWrapper(SapiensAcceleratordOptimizer):
    def __init__(self, optimizer):
        super().__init__(optimizer, device_placement=False, scaler=None)
        self.__has_overflow__ = hasattr(self.optimizer, "overflow")
    def zero_grad(self, set_to_none=None): pass
    def step(self): pass
    @property
    def step_was_skipped(self):
        if self.__has_overflow__: return self.optimizer.overflow
        return False
class DeepSpeedSchedulerWrapper(SapiensAcceleratordScheduler):
    def __init__(self, scheduler, optimizers): super().__init__(scheduler, optimizers)
    def step(self): pass
class DummyOptim:
    def __init__(self, params, lr=0.001, weight_decay=0, **kwargs):
        self.params = params
        self.lr = lr
        self.weight_decay = weight_decay
        self.kwargs = kwargs
class DummyScheduler:
    def __init__(self, optimizer, total_num_steps=None, warmup_num_steps=0, lr_scheduler_callable=None, **kwargs):
        self.optimizer = optimizer
        self.total_num_steps = total_num_steps
        self.warmup_num_steps = warmup_num_steps
        self.lr_scheduler_callable = lr_scheduler_callable
        self.kwargs = kwargs
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
