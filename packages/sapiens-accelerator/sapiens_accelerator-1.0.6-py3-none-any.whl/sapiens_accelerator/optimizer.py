"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import inspect
import torch
from .state import AcceleratorState, GradientState
from .utils import DistributedType, honor_type, is_lomo_available, is_torch_xla_available
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
def move_to_device(state, device):
    if isinstance(state, (list, tuple)): return honor_type(state, (move_to_device(t, device) for t in state))
    elif isinstance(state, dict): return type(state)({k: move_to_device(v, device) for k, v in state.items()})
    elif isinstance(state, torch.Tensor): return state.to(device)
    return state
class SapiensAcceleratordOptimizer(torch.optim.Optimizer):
    def __init__(self, optimizer, device_placement=True, scaler=None):
        self.optimizer = optimizer
        self.scaler = scaler
        self.accelerator_state = AcceleratorState()
        self.gradient_state = GradientState()
        self.device_placement = device_placement
        self._is_overflow = False
        if self.scaler is not None:
            self._sapiens_accelerator_step_called = False
            self._optimizer_original_step_method = self.optimizer.step
            self._optimizer_patched_step_method = patch_optimizer_step(self, self.optimizer.step)
        if device_placement:
            state_dict = self.optimizer.state_dict()
            if self.accelerator_state.distributed_type == DistributedType.XLA: xm.send_cpu_data_to_device(state_dict, self.accelerator_state.device)
            else: state_dict = move_to_device(state_dict, self.accelerator_state.device)
            self.optimizer.load_state_dict(state_dict)
    @property
    def state(self): return self.optimizer.state
    @state.setter
    def state(self, state): self.optimizer.state = state
    @property
    def param_groups(self): return self.optimizer.param_groups
    @param_groups.setter
    def param_groups(self, param_groups): self.optimizer.param_groups = param_groups
    @property
    def defaults(self): return self.optimizer.defaults
    @defaults.setter
    def defaults(self, defaults): self.optimizer.defaults = defaults
    def add_param_group(self, param_group): self.optimizer.add_param_group(param_group)
    def load_state_dict(self, state_dict):
        if self.accelerator_state.distributed_type == DistributedType.XLA and self.device_placement: xm.send_cpu_data_to_device(state_dict, self.accelerator_state.device)
        self.optimizer.load_state_dict(state_dict)
    def state_dict(self): return self.optimizer.state_dict()
    def zero_grad(self, set_to_none=None):
        if self.gradient_state.sync_gradients:
            accept_arg = "set_to_none" in inspect.signature(self.optimizer.zero_grad).parameters
            if accept_arg:
                if set_to_none is None: set_to_none = True
                self.optimizer.zero_grad(set_to_none=set_to_none)
            else:
                if set_to_none is not None: raise ValueError("`set_to_none` for Optimizer.zero_grad` is not supported by this optimizer.")
                self.optimizer.zero_grad()
    def train(self):
        if hasattr(self.optimizer, "train") and callable(self.optimizer.train): self.optimizer.train()
    def eval(self):
        if hasattr(self.optimizer, "eval") and callable(self.optimizer.eval): self.optimizer.eval()
    def step(self, closure=None):
        if is_lomo_available(): from lomo_optim import AdaLomo, Lomo
        if (not self.gradient_state.is_xla_gradients_synced and self.accelerator_state.distributed_type == DistributedType.XLA):
            gradients = xm._fetch_gradients(self.optimizer)
            xm.all_reduce("sum", gradients, scale=1.0 / xm.xrt_world_size())
            self.gradient_state.is_xla_gradients_synced = True
        if is_lomo_available():
            if isinstance(self.optimizer, (Lomo, AdaLomo)): return
        if self.gradient_state.sync_gradients:
            if self.scaler is not None:
                self.optimizer.step = self._optimizer_patched_step_method
                self.scaler.step(self.optimizer, closure)
                self.scaler.update()
                if not self._sapiens_accelerator_step_called: self._is_overflow = True
                else: self._is_overflow = False
                self.optimizer.step = self._optimizer_original_step_method
                self._sapiens_accelerator_step_called = False
            else: self.optimizer.step(closure)
        if self.accelerator_state.distributed_type == DistributedType.XLA: self.gradient_state.is_xla_gradients_synced = False
    def _switch_parameters(self, parameters_map):
        for param_group in self.optimizer.param_groups: param_group["params"] = [parameters_map.get(p, p) for p in param_group["params"]]
    @property
    def step_was_skipped(self): return self._is_overflow
    def __getstate__(self):
        _ignored_keys = ["_sapiens_accelerator_step_called", "_optimizer_original_step_method", "_optimizer_patched_step_method"]
        return {k: v for k, v in self.__dict__.items() if k not in _ignored_keys}
    def __setstate__(self, state):
        self.__dict__.update(state)
        if self.scaler is not None:
            self._sapiens_accelerator_step_called = False
            self._optimizer_original_step_method = self.optimizer.step
            self._optimizer_patched_step_method = patch_optimizer_step(self, self.optimizer.step)
def patch_optimizer_step(sapiens_acceleratord_optimizer: SapiensAcceleratordOptimizer, method):
    def patched_step(*args, **kwargs):
        sapiens_acceleratord_optimizer._sapiens_accelerator_step_called = True
        return method(*args, **kwargs)
    return patched_step
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
