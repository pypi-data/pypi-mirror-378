"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import logging
import os
from copy import deepcopy
from typing import Dict, List, Optional, Union
import torch
import torch.nn as nn
from sapiens_accelerator.utils.imports import (is_4bit_sapiens_available, is_8bit_sapiens_available)
from ..big_modeling import dispatch_model, init_empty_weights
from .dataclasses import BnbQuantizationConfig
from .modeling import (find_tied_parameters, get_balanced_memory, infer_auto_device_map, load_checkpoint_in_model, offload_weight, set_module_tensor_to_device)
logger = logging.getLogger(__name__)
def load_and_quantize_model(model: torch.nn.Module, sapiens_quantization_config: BnbQuantizationConfig, weights_location: Union[str, os.PathLike] = None,
device_map: Optional[Dict[str, Union[int, str, torch.device]]] = None, no_split_module_classes: Optional[List[str]] = None, max_memory: Optional[Dict[Union[int, str], Union[int, str]]] = None,
offload_folder: Optional[Union[str, os.PathLike]] = None, offload_state_dict: bool = False):
    load_in_4bit = sapiens_quantization_config.load_in_4bit
    load_in_8bit = sapiens_quantization_config.load_in_8bit
    if load_in_8bit and not is_8bit_sapiens_available(): raise ImportError("You have a version of `sapiens_machine` that is not compatible with 8bit quantization, make sure you have the latest version of `sapiens_machine` installed.")
    if load_in_4bit and not is_4bit_sapiens_available(): raise ValueError("You have a version of `sapiens_machine` that is not compatible with 4bit quantization, make sure you have the latest version of `sapiens_machine` installed.")
    modules_on_cpu = []
    if isinstance(device_map, dict) and len(device_map.keys()) > 1: modules_on_cpu = [key for key, value in device_map.items() if value in ["disk", "cpu"]]
    if sapiens_quantization_config.skip_modules is None: sapiens_quantization_config.skip_modules = get_keys_to_not_convert(model)
    if load_in_4bit: sapiens_quantization_config.skip_modules.extend(modules_on_cpu)
    modules_to_not_convert = sapiens_quantization_config.skip_modules
    if sapiens_quantization_config.keep_in_fp32_modules is None: sapiens_quantization_config.keep_in_fp32_modules = []
    keep_in_fp32_modules = sapiens_quantization_config.keep_in_fp32_modules
    modules_to_not_convert.extend(keep_in_fp32_modules)
    model.is_loaded_in_4bit = load_in_4bit
    model.is_loaded_in_8bit = load_in_8bit
    model_device = get_parameter_device(model)
    if model_device.type != "meta":
        model = replace_with_sapiens_layers(model, sapiens_quantization_config, modules_to_not_convert=modules_to_not_convert)
        dtype = sapiens_quantization_config.torch_dtype
        for name, param in model.state_dict().items():
            if any(module_to_keep_in_fp32 in name for module_to_keep_in_fp32 in keep_in_fp32_modules):
                param.to(torch.float32)
                if param.dtype != torch.float32:
                    name = name.replace(".weight", "").replace(".bias", "")
                    param = getattr(model, name, None)
                    if param is not None: param.to(torch.float32)
            elif torch.is_floating_point(param): param.to(dtype)
        if model_device.type == "cuda":
            model.cuda(torch.cuda.current_device())
            torch.cuda.empty_cache()
        elif torch.cuda.is_available(): model.to(torch.cuda.current_device())
        else: raise RuntimeError("No GPU found. A GPU is needed for quantization.")
        return model
    elif weights_location is None: raise RuntimeError(f"`weights_location` needs to be the folder path containing the weights of the model, but we found {weights_location} ")
    else:
        with init_empty_weights(): model = replace_with_sapiens_layers(model, sapiens_quantization_config, modules_to_not_convert=modules_to_not_convert)
        device_map = get_quantized_model_device_map(model, sapiens_quantization_config, device_map, max_memory=max_memory, no_split_module_classes=no_split_module_classes)
        if offload_state_dict is None and device_map is not None and "disk" in device_map.values(): offload_state_dict = True
        offload = any(x in list(device_map.values()) for x in ["cpu", "disk"])
        load_checkpoint_in_model(model, weights_location, device_map, dtype=sapiens_quantization_config.torch_dtype, offload_folder=offload_folder,
        offload_state_dict=offload_state_dict, keep_in_fp32_modules=sapiens_quantization_config.keep_in_fp32_modules, offload_8bit_sapiens=load_in_8bit and offload)
        return dispatch_model(model, device_map=device_map, offload_dir=offload_folder)
def get_quantized_model_device_map(model, sapiens_quantization_config, device_map=None, max_memory=None, no_split_module_classes=None):
    if device_map is None:
        if torch.cuda.is_available(): device_map = {"": torch.cuda.current_device()}
        else: raise RuntimeError("No GPU found. A GPU is needed for quantization.")
    if isinstance(device_map, str):
        if device_map not in ["auto", "balanced", "balanced_low_0", "sequential"]: raise ValueError("If passing a string for `device_map`, please choose 'auto', 'balanced', 'balanced_low_0' or 'sequential'.")
        special_dtypes = {}
        special_dtypes.update({name: sapiens_quantization_config.torch_dtype for name, _ in model.named_parameters() if any(m in name for m in sapiens_quantization_config.skip_modules)})
        special_dtypes.update({name: torch.float32 for name, _ in model.named_parameters() if any(m in name for m in sapiens_quantization_config.keep_in_fp32_modules)})
        kwargs = {}
        kwargs["special_dtypes"] = special_dtypes
        kwargs["no_split_module_classes"] = no_split_module_classes
        kwargs["dtype"] = sapiens_quantization_config.target_dtype
        if device_map != "sequential": max_memory = get_balanced_memory(model, low_zero=(device_map == "balanced_low_0"), max_memory=max_memory, **kwargs)
        kwargs["max_memory"] = max_memory
        device_map = infer_auto_device_map(model, **kwargs)
    if isinstance(device_map, dict):
        modules_not_to_convert = sapiens_quantization_config.skip_modules + sapiens_quantization_config.keep_in_fp32_modules
        device_map_without_some_modules = {key: device_map[key] for key in device_map.keys() if key not in modules_not_to_convert}
        for device in ["cpu", "disk"]:
            if device in device_map_without_some_modules.values():
                if sapiens_quantization_config.load_in_4bit: raise
        del device_map_without_some_modules
    return device_map
def replace_with_sapiens_layers(model, sapiens_quantization_config, modules_to_not_convert=None, current_key_name=None):
    if modules_to_not_convert is None: modules_to_not_convert = []
    model, has_been_replaced = _replace_with_sapiens_layers(model, sapiens_quantization_config, modules_to_not_convert, current_key_name)
    return model
def _replace_with_sapiens_layers(model, sapiens_quantization_config, modules_to_not_convert=None, current_key_name=None):
    import sapiens_machine as sapiens
    has_been_replaced = False
    for name, module in model.named_children():
        if current_key_name is None: current_key_name = []
        current_key_name.append(name)
        if isinstance(module, nn.Linear) and name not in modules_to_not_convert:
            current_key_name_str = ".".join(current_key_name)
            proceed = True
            for key in modules_to_not_convert:
                if ((key in current_key_name_str) and (key + "." in current_key_name_str)) or key == current_key_name_str:
                    proceed = False
                    break
            if proceed:
                if sapiens_quantization_config.load_in_8bit: sapiens_module = sapiens.nn.Linear8bitLt(module.in_features, module.out_features, module.bias is not None, has_fp16_weights=False, threshold=sapiens_quantization_config.llm_int8_threshold)
                elif sapiens_quantization_config.load_in_4bit: sapiens_module = sapiens.nn.Linear4bit(module.in_features, module.out_features, module.bias is not None, sapiens_quantization_config.sapiens_4bit_compute_dtype,
                compress_statistics=sapiens_quantization_config.sapiens_4bit_use_double_quant, quant_type=sapiens_quantization_config.sapiens_4bit_quant_type)
                else: raise ValueError("load_in_8bit and load_in_4bit can't be both False")
                sapiens_module.weight.data = module.weight.data
                if module.bias is not None: sapiens_module.bias.data = module.bias.data
                sapiens_module.requires_grad_(False)
                setattr(model, name, sapiens_module)
                has_been_replaced = True
        if len(list(module.children())) > 0:
            _, _has_been_replaced = _replace_with_sapiens_layers(module, sapiens_quantization_config, modules_to_not_convert, current_key_name)
            has_been_replaced = has_been_replaced | _has_been_replaced
        current_key_name.pop(-1)
    return model, has_been_replaced
def get_keys_to_not_convert(model):
    with init_empty_weights(): tied_model = deepcopy(model)
    tied_params = find_tied_parameters(tied_model)
    if isinstance(tied_params, dict): tied_keys = sum(list(tied_params.values()), []) + list(tied_params.keys())
    else: tied_keys = sum(tied_params, [])
    has_tied_params = len(tied_keys) > 0
    is_base_model = False
    if hasattr(model, "base_model_prefix"): is_base_model = not hasattr(model, model.base_model_prefix)
    if (not has_tied_params) and is_base_model: return []
    list_modules = list(model.named_children())
    list_last_module = [list_modules[-1][0]]
    intersection = set(list_last_module) - set(tied_keys)
    list_untouched = list(set(tied_keys)) + list(intersection)
    names_to_remove = [".weight", ".bias"]
    filtered_module_names = []
    for name in list_untouched:
        for name_to_remove in names_to_remove:
            if name_to_remove in name: name = name.replace(name_to_remove, "")
        filtered_module_names.append(name)
    return filtered_module_names
def has_4bit_sapiens_layers(model):
    import sapiens_machine as sapiens
    for m in model.modules():
        if isinstance(m, sapiens.nn.Linear4bit): return True
    return False
def get_parameter_device(parameter: nn.Module): return next(parameter.parameters()).device
def quantize_and_offload_8bit(model, param, param_name, new_dtype, offload_folder, offload_index, fp16_statistics):
    if fp16_statistics is None:
        set_module_tensor_to_device(model, param_name, 0, dtype=new_dtype, value=param)
        tensor_name = param_name
        module = model
        if "." in tensor_name:
            splits = tensor_name.split(".")
            for split in splits[:-1]:
                new_module = getattr(module, split)
                if new_module is None: raise ValueError(f"{module} has no attribute {split}.")
                module = new_module
            tensor_name = splits[-1]
        module._parameters[tensor_name].requires_grad = False
        offload_weight(module._parameters[tensor_name], param_name, offload_folder, index=offload_index)
        if hasattr(module._parameters[tensor_name], "SCB"): offload_weight(module._parameters[tensor_name].SCB, param_name.replace("weight", "SCB"), offload_folder, index=offload_index)
    else:
        offload_weight(param, param_name, offload_folder, index=offload_index)
        offload_weight(fp16_statistics, param_name.replace("weight", "SCB"), offload_folder, index=offload_index)
    set_module_tensor_to_device(model, param_name, "meta", dtype=new_dtype, value=torch.empty(*param.size()))
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
