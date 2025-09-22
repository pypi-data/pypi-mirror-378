"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import functools
from typing import Dict, List, Mapping, Optional, Union
import torch
import torch.nn as nn
from .state import PartialState
from .utils import (PrefixedDataset, find_device, named_module_tensors, send_to_device, set_module_tensor_to_device)
from .utils.memory import clear_device_cache
from .utils.modeling import get_non_persistent_buffers
from .utils.other import recursive_getattr
_sapiens_accelerator_added_attributes = ["to", "cuda", "npu", "xpu", "mlu", "musa"]
class ModelHook:
    no_grad = False
    def init_hook(self, module): return module
    def pre_forward(self, module, *args, **kwargs): return args, kwargs
    def post_forward(self, module, output): return output
    def detach_hook(self, module): return module
class SequentialHook(ModelHook):
    def __init__(self, *hooks): self.hooks = hooks
    def init_hook(self, module):
        for hook in self.hooks: module = hook.init_hook(module)
        return module
    def pre_forward(self, module, *args, **kwargs):
        for hook in self.hooks: args, kwargs = hook.pre_forward(module, *args, **kwargs)
        return args, kwargs
    def post_forward(self, module, output):
        for hook in self.hooks: output = hook.post_forward(module, output)
        return output
    def detach_hook(self, module):
        for hook in self.hooks: module = hook.detach_hook(module)
        return module
def add_hook_to_module(module: nn.Module, hook: ModelHook, append: bool = False):
    if append and (getattr(module, "_hf_hook", None) is not None):
        old_hook = module._hf_hook
        remove_hook_from_module(module)
        hook = SequentialHook(old_hook, hook)
    if hasattr(module, "_hf_hook") and hasattr(module, "_old_forward"): old_forward = module._old_forward
    else:
        old_forward = module.forward
        module._old_forward = old_forward
    module = hook.init_hook(module)
    module._hf_hook = hook
    def new_forward(module, *args, **kwargs):
        args, kwargs = module._hf_hook.pre_forward(module, *args, **kwargs)
        if module._hf_hook.no_grad:
            with torch.no_grad(): output = module._old_forward(*args, **kwargs)
        else: output = module._old_forward(*args, **kwargs)
        return module._hf_hook.post_forward(module, output)
    if "GraphModuleImpl" in str(type(module)): module.__class__.forward = functools.update_wrapper(functools.partial(new_forward, module), old_forward)
    else: module.forward = functools.update_wrapper(functools.partial(new_forward, module), old_forward)
    return module
def remove_hook_from_module(module: nn.Module, recurse=False):
    if hasattr(module, "_hf_hook"):
        module._hf_hook.detach_hook(module)
        delattr(module, "_hf_hook")
    if hasattr(module, "_old_forward"):
        if "GraphModuleImpl" in str(type(module)): module.__class__.forward = module._old_forward
        else: module.forward = module._old_forward
        delattr(module, "_old_forward")
    for attr in _sapiens_accelerator_added_attributes: module.__dict__.pop(attr, None)
    if recurse:
        for child in module.children(): remove_hook_from_module(child, recurse)
    return module
class AlignDevicesHook(ModelHook):
    def __init__(self, execution_device: Optional[Union[int, str, torch.device]] = None, offload: bool = False, io_same_device: bool = False,
    weights_map: Optional[Mapping] = None, offload_buffers: bool = False, place_submodules: bool = False, skip_keys: Optional[Union[str, List[str]]] = None,
    tied_params_map: Optional[Dict[int, Dict[torch.device, torch.Tensor]]] = None):
        self.execution_device = execution_device
        self.offload = offload
        self.io_same_device = io_same_device
        self.weights_map = weights_map
        self.offload_buffers = offload_buffers
        self.place_submodules = place_submodules
        self.skip_keys = skip_keys
        self.input_device = None
        self.param_original_devices = {}
        self.buffer_original_devices = {}
        self.tied_params_names = set()
        self.tied_params_map = tied_params_map
    def __repr__(self): return (f"AlignDevicesHook(execution_device={self.execution_device}, offload={self.offload}, io_same_device={self.io_same_device}, offload_buffers={self.offload_buffers}, place_submodules={self.place_submodules}, skip_keys={repr(self.skip_keys)})")
    def init_hook(self, module):
        if self.execution_device == "meta" or self.execution_device == torch.device("meta"): self.tied_params_map = None
        if not self.offload and self.execution_device is not None:
            for name, _ in named_module_tensors(module, recurse=self.place_submodules): set_module_tensor_to_device(module, name, self.execution_device, tied_params_map=self.tied_params_map)
        elif self.offload:
            self.original_devices = {name: param.device for name, param in named_module_tensors(module, recurse=self.place_submodules)}
            if self.weights_map is None: self.weights_map = {name: param.to("cpu") for name, param in named_module_tensors(module, include_buffers=self.offload_buffers, recurse=self.place_submodules)}
            for name, _ in named_module_tensors(module, include_buffers=self.offload_buffers, recurse=self.place_submodules, remove_non_persistent=True):
                if (self.tied_params_map is not None and recursive_getattr(module, name).data_ptr() in self.tied_params_map): self.tied_params_names.add(name)
                set_module_tensor_to_device(module, name, "meta")
            if not self.offload_buffers and self.execution_device is not None:
                for name, _ in module.named_buffers(recurse=self.place_submodules): set_module_tensor_to_device(module, name, self.execution_device, tied_params_map=self.tied_params_map)
            elif self.offload_buffers and self.execution_device is not None:
                for name in get_non_persistent_buffers(module, recurse=self.place_submodules): set_module_tensor_to_device(module, name, self.execution_device, tied_params_map=self.tied_params_map)
        return module
    def pre_forward(self, module, *args, **kwargs):
        if self.io_same_device: self.input_device = find_device([args, kwargs])
        if self.offload:
            self.tied_pointers_to_remove = set()
            for name, _ in named_module_tensors(module, include_buffers=self.offload_buffers, recurse=self.place_submodules, remove_non_persistent=True):
                fp16_statistics = None
                value = self.weights_map[name]
                if "weight" in name and name.replace("weight", "SCB") in self.weights_map.keys():
                    if value.dtype == torch.int8: fp16_statistics = self.weights_map[name.replace("weight", "SCB")]
                if name in self.tied_params_names and value.data_ptr() not in self.tied_params_map: self.tied_params_map[value.data_ptr()] = {}
                if (value is not None and self.tied_params_map is not None and value.data_ptr() in self.tied_params_map and self.execution_device not in self.tied_params_map[value.data_ptr()]): self.tied_pointers_to_remove.add((value.data_ptr(), self.execution_device))
                set_module_tensor_to_device(module, name, self.execution_device, value=value, fp16_statistics=fp16_statistics, tied_params_map=self.tied_params_map)
        return send_to_device(args, self.execution_device), send_to_device(kwargs, self.execution_device, skip_keys=self.skip_keys)
    def post_forward(self, module, output):
        if self.offload:
            for name, _ in named_module_tensors(module, include_buffers=self.offload_buffers, recurse=self.place_submodules, remove_non_persistent=True):
                set_module_tensor_to_device(module, name, "meta")
                if type(module).__name__ == "Linear8bitLt":
                    module.state.SCB = None
                    module.state.CxB = None
            for value_pointer, device in self.tied_pointers_to_remove: del self.tied_params_map[value_pointer][device]
            self.tied_pointers_to_remove = set()
        if self.io_same_device and self.input_device is not None: output = send_to_device(output, self.input_device, skip_keys=self.skip_keys)
        return output
    def detach_hook(self, module):
        if self.offload:
            for name, device in self.original_devices.items():
                if device != torch.device("meta"): set_module_tensor_to_device(module, name, device, value=self.weights_map.get(name, None))
        return module
def attach_execution_device_hook(module: torch.nn.Module, execution_device: Union[int, str, torch.device], skip_keys: Optional[Union[str, List[str]]] = None,
preload_module_classes: Optional[List[str]] = None, tied_params_map: Optional[Dict[int, Dict[torch.device, torch.Tensor]]] = None):
    if not hasattr(module, "_hf_hook") and len(module.state_dict()) > 0: add_hook_to_module(module, AlignDevicesHook(execution_device, skip_keys=skip_keys, tied_params_map=tied_params_map))
    if preload_module_classes is not None and module.__class__.__name__ in preload_module_classes: return
    for child in module.children(): attach_execution_device_hook(child, execution_device, skip_keys=skip_keys, tied_params_map=tied_params_map)
def attach_align_device_hook(module: torch.nn.Module, execution_device: Optional[torch.device] = None, offload: bool = False, weights_map: Optional[Mapping] = None,
offload_buffers: bool = False, module_name: str = "", skip_keys: Optional[Union[str, List[str]]] = None, preload_module_classes: Optional[List[str]] = None,
tied_params_map: Optional[Dict[int, Dict[torch.device, torch.Tensor]]] = None):
    directs = named_module_tensors(module)
    full_offload = (offload and preload_module_classes is not None and module.__class__.__name__ in preload_module_classes)
    if len(list(directs)) > 0 or full_offload:
        if weights_map is not None:
            prefix = f"{module_name}." if len(module_name) > 0 else ""
            prefixed_weights_map = PrefixedDataset(weights_map, prefix)
        else: prefixed_weights_map = None
        hook = AlignDevicesHook(execution_device=execution_device, offload=offload, weights_map=prefixed_weights_map, offload_buffers=offload_buffers,
        place_submodules=full_offload, skip_keys=skip_keys, tied_params_map=tied_params_map)
        add_hook_to_module(module, hook, append=True)
    if full_offload: return
    for child_name, child in module.named_children():
        child_name = f"{module_name}.{child_name}" if len(module_name) > 0 else child_name
        attach_align_device_hook(child, execution_device=execution_device, offload=offload, weights_map=weights_map, offload_buffers=offload_buffers,
        module_name=child_name, preload_module_classes=preload_module_classes, skip_keys=skip_keys, tied_params_map=tied_params_map)
def remove_hook_from_submodules(module: nn.Module):
    remove_hook_from_module(module)
    for child in module.children(): remove_hook_from_submodules(child)
def attach_align_device_hook_on_blocks(module: nn.Module, execution_device: Optional[Union[torch.device, Dict[str, torch.device]]] = None,
offload: Union[bool, Dict[str, bool]] = False, weights_map: Mapping = None, offload_buffers: bool = False, module_name: str = "", skip_keys: Optional[Union[str, List[str]]] = None,
preload_module_classes: Optional[List[str]] = None, tied_params_map: Optional[Dict[int, Dict[torch.device, torch.Tensor]]] = None):
    if not isinstance(execution_device, Mapping) and not isinstance(offload, dict):
        if not offload:
            hook = AlignDevicesHook(execution_device=execution_device, io_same_device=True, skip_keys=skip_keys, place_submodules=True, tied_params_map=tied_params_map)
            add_hook_to_module(module, hook)
        else: attach_align_device_hook(module, execution_device=execution_device, offload=True, weights_map=weights_map, offload_buffers=offload_buffers,
        module_name=module_name, skip_keys=skip_keys, tied_params_map=tied_params_map)
        return
    if not isinstance(execution_device, Mapping): execution_device = {key: execution_device for key in offload.keys()}
    if not isinstance(offload, Mapping): offload = {key: offload for key in execution_device.keys()}
    if module_name in execution_device and module_name in offload and not offload[module_name]:
        hook = AlignDevicesHook(execution_device=execution_device[module_name], offload_buffers=offload_buffers, io_same_device=(module_name == ""),
        place_submodules=True, skip_keys=skip_keys, tied_params_map=tied_params_map)
        add_hook_to_module(module, hook)
        attach_execution_device_hook(module, execution_device[module_name], skip_keys=skip_keys, tied_params_map=tied_params_map)
    elif module_name in execution_device and module_name in offload:
        attach_align_device_hook(module, execution_device=execution_device[module_name], offload=True, weights_map=weights_map, offload_buffers=offload_buffers,
        module_name=module_name, skip_keys=skip_keys, preload_module_classes=preload_module_classes, tied_params_map=tied_params_map)
        if not hasattr(module, "_hf_hook"):
            hook = AlignDevicesHook(execution_device=execution_device[module_name], io_same_device=(module_name == ""), skip_keys=skip_keys, tied_params_map=tied_params_map)
            add_hook_to_module(module, hook)
        attach_execution_device_hook(module, execution_device[module_name], preload_module_classes=preload_module_classes, skip_keys=skip_keys, tied_params_map=tied_params_map)
    elif module_name == "":
        hook = AlignDevicesHook(execution_device=execution_device.get(""), io_same_device=True, skip_keys=skip_keys, tied_params_map=tied_params_map)
        add_hook_to_module(module, hook)
    for child_name, child in module.named_children():
        child_name = f"{module_name}.{child_name}" if len(module_name) > 0 else child_name
        attach_align_device_hook_on_blocks(child, execution_device=execution_device, offload=offload, weights_map=weights_map, offload_buffers=offload_buffers,
        module_name=child_name, preload_module_classes=preload_module_classes, skip_keys=skip_keys, tied_params_map=tied_params_map)
class CpuOffload(ModelHook):
    def __init__(self, execution_device: Optional[Union[str, int, torch.device]] = None, prev_module_hook: Optional["UserCpuOffloadHook"] = None):
        self.prev_module_hook = prev_module_hook
        self.execution_device = execution_device if execution_device is not None else PartialState().default_device
    def init_hook(self, module): return module.to("cpu")
    def pre_forward(self, module, *args, **kwargs):
        if self.prev_module_hook is not None:
            self.prev_module_hook.offload()
            clear_device_cache()
        module.to(self.execution_device)
        return send_to_device(args, self.execution_device), send_to_device(kwargs, self.execution_device)
class UserCpuOffloadHook:
    def __init__(self, model, hook):
        self.model = model
        self.hook = hook
    def offload(self): self.hook.init_hook(self.model)
    def remove(self): remove_hook_from_module(self.model)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
