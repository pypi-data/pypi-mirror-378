"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Dict, List, Optional, Union
import torch
import torch.nn as nn
from .hooks import (AlignDevicesHook, CpuOffload, UserCpuOffloadHook, add_hook_to_module, attach_align_device_hook, attach_align_device_hook_on_blocks)
from .utils import (OffloadedWeightsLoader, check_cuda_p2p_ib_support, check_device_map, extract_submodules_state_dict, find_tied_parameters, get_balanced_memory,
infer_auto_device_map, is_mlu_available, is_musa_available, is_npu_available, is_torch_version, is_xpu_available, load_checkpoint_in_model, offload_state_dict,
parse_flag_from_env, retie_parameters)
from .utils.other import recursive_getattr
logger = logging.getLogger(__name__)
@contextmanager
def init_empty_weights(include_buffers: bool = None):
    if include_buffers is None: include_buffers = parse_flag_from_env("SAPIENS_ACCELERATOR_INIT_INCLUDE_BUFFERS", False)
    with init_on_device(torch.device("meta"), include_buffers=include_buffers) as f: yield f
@contextmanager
def init_on_device(device: torch.device, include_buffers: bool = None):
    if include_buffers is None: include_buffers = parse_flag_from_env("SAPIENS_ACCELERATOR_INIT_INCLUDE_BUFFERS", False)
    if is_torch_version(">=", "2.0") and include_buffers:
        with device: yield
        return
    old_register_parameter = nn.Module.register_parameter
    if include_buffers: old_register_buffer = nn.Module.register_buffer
    def register_empty_parameter(module, name, param):
        old_register_parameter(module, name, param)
        if param is not None:
            param_cls = type(module._parameters[name])
            kwargs = module._parameters[name].__dict__
            kwargs["requires_grad"] = param.requires_grad
            module._parameters[name] = param_cls(module._parameters[name].to(device), **kwargs)
    def register_empty_buffer(module, name, buffer, persistent=True):
        old_register_buffer(module, name, buffer, persistent=persistent)
        if buffer is not None: module._buffers[name] = module._buffers[name].to(device)
    if include_buffers: tensor_constructors_to_patch = {torch_function_name: getattr(torch, torch_function_name) for torch_function_name in ["empty", "zeros", "ones", "full"]}
    else: tensor_constructors_to_patch = {}
    def patch_tensor_constructor(fn):
        def wrapper(*args, **kwargs):
            kwargs["device"] = device
            return fn(*args, **kwargs)
        return wrapper
    try:
        nn.Module.register_parameter = register_empty_parameter
        if include_buffers: nn.Module.register_buffer = register_empty_buffer
        for torch_function_name in tensor_constructors_to_patch.keys(): setattr(torch, torch_function_name, patch_tensor_constructor(getattr(torch, torch_function_name)))
        yield
    finally:
        nn.Module.register_parameter = old_register_parameter
        if include_buffers: nn.Module.register_buffer = old_register_buffer
        for torch_function_name, old_torch_function in tensor_constructors_to_patch.items(): setattr(torch, torch_function_name, old_torch_function)
def cpu_offload(model: nn.Module, execution_device: Optional[torch.device] = None, offload_buffers: bool = False, state_dict: Optional[Dict[str, torch.Tensor]] = None, preload_module_classes: Optional[List[str]] = None):
    if execution_device is None: execution_device = next(iter(model.parameters())).device
    if state_dict is None: state_dict = {n: p.to("cpu") for n, p in model.state_dict().items()}
    add_hook_to_module(model, AlignDevicesHook(io_same_device=True), append=True)
    attach_align_device_hook(model, execution_device=execution_device, offload=True, offload_buffers=offload_buffers, weights_map=state_dict, preload_module_classes=preload_module_classes)
    return model
def cpu_offload_with_hook(model: torch.nn.Module, execution_device: Optional[Union[int, str, torch.device]] = None, prev_module_hook: Optional[UserCpuOffloadHook] = None):
    hook = CpuOffload(execution_device=execution_device, prev_module_hook=prev_module_hook)
    add_hook_to_module(model, hook, append=True)
    user_hook = UserCpuOffloadHook(model, hook)
    return model, user_hook
def disk_offload(model: nn.Module, offload_dir: Union[str, os.PathLike], execution_device: Optional[torch.device] = None, offload_buffers: bool = False, preload_module_classes: Optional[List[str]] = None):
    if not os.path.isdir(offload_dir) or not os.path.isfile(os.path.join(offload_dir, "index.json")): offload_state_dict(offload_dir, model.state_dict())
    if execution_device is None: execution_device = next(iter(model.parameters())).device
    weights_map = OffloadedWeightsLoader(save_folder=offload_dir)
    add_hook_to_module(model, AlignDevicesHook(io_same_device=True), append=True)
    attach_align_device_hook(model, execution_device=execution_device, offload=True, offload_buffers=offload_buffers, weights_map=weights_map, preload_module_classes=preload_module_classes)
    return model
def dispatch_model(model: nn.Module, device_map: Dict[str, Union[str, int, torch.device]], main_device: Optional[torch.device] = None, state_dict: Optional[Dict[str, torch.Tensor]] = None,
offload_dir: Optional[Union[str, os.PathLike]] = None, offload_index: Optional[Dict[str, str]] = None, offload_buffers: bool = False, skip_keys: Optional[Union[str, List[str]]] = None,
preload_module_classes: Optional[List[str]] = None, force_hooks: bool = False):
    check_device_map(model, device_map)
    is_sapiens_quantized = (getattr(model, "is_quantized", False) or getattr(model, "is_loaded_in_8bit", False)) and getattr(model, "quantization_method", "sapiens_machine") == "sapiens_machine"
    if (len(set(device_map.values())) > 1) or is_sapiens_quantized or force_hooks:
        if main_device is None:
            if set(device_map.values()) == {"cpu"} or set(device_map.values()) == {"cpu", "disk"}: main_device = "cpu"
            else: main_device = [d for d in device_map.values() if d not in ["cpu", "disk"]][0]
        if main_device != "cpu":
            cpu_modules = [name for name, device in device_map.items() if device == "cpu"]
            if state_dict is None and len(cpu_modules) > 0: state_dict = extract_submodules_state_dict(model.state_dict(), cpu_modules)
        disk_modules = [name for name, device in device_map.items() if device == "disk"]
        if offload_dir is None and offload_index is None and len(disk_modules) > 0: raise ValueError(f"We need an `offload_dir` to dispatch this model according to this `device_map`, the following submodules need to be offloaded: {', '.join(disk_modules)}.")
        if (len(disk_modules) > 0 and offload_index is None and (not os.path.isdir(offload_dir) or not os.path.isfile(os.path.join(offload_dir, "index.json")))):
            disk_state_dict = extract_submodules_state_dict(model.state_dict(), disk_modules)
            offload_state_dict(offload_dir, disk_state_dict)
        execution_device = {name: main_device if device in ["cpu", "disk"] else device for name, device in device_map.items()}
        execution_device[""] = main_device
        offloaded_devices = ["disk"] if main_device == "cpu" or main_device == "mps" else ["cpu", "disk"]
        offload = {name: device in offloaded_devices for name, device in device_map.items()}
        save_folder = offload_dir if len(disk_modules) > 0 else None
        if state_dict is not None or save_folder is not None or offload_index is not None:
            device = main_device if offload_index is not None else None
            weights_map = OffloadedWeightsLoader(state_dict=state_dict, save_folder=save_folder, index=offload_index, device=device)
        else: weights_map = None
        tied_params = find_tied_parameters(model)
        tied_params_map = {}
        for group in tied_params:
            for param_name in group:
                data_ptr = recursive_getattr(model, param_name).data_ptr()
                tied_params_map[data_ptr] = {}
        attach_align_device_hook_on_blocks(model, execution_device=execution_device, offload=offload, offload_buffers=offload_buffers, weights_map=weights_map,
        skip_keys=skip_keys, preload_module_classes=preload_module_classes, tied_params_map=tied_params_map)
        offloaded_devices_str = " and ".join([device for device in set(device_map.values()) if device in ("cpu", "disk")])
        retie_parameters(model, tied_params)
        def add_warning(fn, model):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                for param in model.parameters():
                    if param.device == torch.device("meta"): raise RuntimeError("You can't move a model that has some modules offloaded to cpu or disk.")
                return fn(*args, **kwargs)
            return wrapper
        model.to = add_warning(model.to, model)
        if is_npu_available(): model.npu = add_warning(model.npu, model)
        elif is_mlu_available(): model.mlu = add_warning(model.mlu, model)
        elif is_musa_available(): model.musa = add_warning(model.musa, model)
        elif is_xpu_available(): model.xpu = add_warning(model.xpu, model)
        else: model.cuda = add_warning(model.cuda, model)
        use_multi_gpu = len([device for device in set(device_map.values()) if device not in ("cpu", "disk")]) > 1
    else:
        device = list(device_map.values())[0]
        if is_npu_available() and isinstance(device, int): device = f"npu:{device}"
        elif is_mlu_available() and isinstance(device, int): device = f"mlu:{device}"
        elif is_musa_available() and isinstance(device, int): device = f"musa:{device}"
        elif is_xpu_available() and isinstance(device, int): device = f"xpu:{device}"
        if device != "disk": model.to(device)
        else: raise ValueError("You are trying to offload the whole model to the disk. Please use the `disk_offload` function instead.")
    model.hf_device_map = dict(device_map)
    return model
def load_checkpoint_and_dispatch(model: nn.Module, checkpoint: Union[str, os.PathLike], device_map: Optional[Union[str, Dict[str, Union[int, str, torch.device]]]] = None,
max_memory: Optional[Dict[Union[int, str], Union[int, str]]] = None, no_split_module_classes: Optional[List[str]] = None, offload_folder: Optional[Union[str, os.PathLike]] = None,
offload_buffers: bool = False, dtype: Optional[Union[str, torch.dtype]] = None, offload_state_dict: Optional[bool] = None, skip_keys: Optional[Union[str, List[str]]] = None,
preload_module_classes: Optional[List[str]] = None, force_hooks: bool = False, strict: bool = False):
    if isinstance(device_map, str) and device_map not in ["auto", "balanced", "balanced_low_0", "sequential"]: raise ValueError("If passing a string for `device_map`, please choose 'auto', 'balanced', 'balanced_low_0' or 'sequential'.")
    if isinstance(device_map, str):
        if device_map != "sequential": max_memory = get_balanced_memory(model, max_memory=max_memory, no_split_module_classes=no_split_module_classes, dtype=dtype, low_zero=(device_map == "balanced_low_0"))
        device_map = infer_auto_device_map(model, max_memory=max_memory, no_split_module_classes=no_split_module_classes, dtype=dtype, offload_buffers=offload_buffers)
    if offload_state_dict is None and device_map is not None and "disk" in device_map.values(): offload_state_dict = True
    load_checkpoint_in_model(model, checkpoint, device_map=device_map, offload_folder=offload_folder, dtype=dtype, offload_state_dict=offload_state_dict,
    offload_buffers=offload_buffers, strict=strict)
    if device_map is None: return model
    return dispatch_model(model, device_map=device_map, offload_dir=offload_folder, offload_buffers=offload_buffers, skip_keys=skip_keys,
    preload_module_classes=preload_module_classes, force_hooks=force_hooks)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
