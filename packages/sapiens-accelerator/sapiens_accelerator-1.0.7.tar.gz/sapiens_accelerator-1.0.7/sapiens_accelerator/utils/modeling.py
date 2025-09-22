"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import contextlib
import gc
import inspect
import json
import logging
import os
import re
import shutil
import tempfile
import warnings
from collections import OrderedDict, defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union
import torch
import torch.nn as nn
from ..state import AcceleratorState
from .constants import SAFE_WEIGHTS_NAME, WEIGHTS_NAME
from .dataclasses import AutocastKwargs, CustomDtype, DistributedType
from .imports import (is_mlu_available, is_mps_available, is_musa_available, is_npu_available, is_peft_available, is_torch_xla_available, is_xpu_available)
from .memory import clear_device_cache, get_xpu_available_memory
from .offload import load_offloaded_weight, offload_weight, save_offload_index
from .tqdm import is_tqdm_available, tqdm
from .versions import compare_versions, is_torch_version
if is_npu_available(check_device=False): import torch_npu
if is_mlu_available(check_device=False): import torch_mlu
if is_musa_available(check_device=False): import torch_musa
from safetensors import safe_open
from safetensors.torch import load_file as safe_load_file
WEIGHTS_INDEX_NAME = "pytorch_model.bin.index.json"
logger = logging.getLogger(__name__)
def is_peft_model(model):
    from .other import extract_model_from_parallel
    if is_peft_available(): from peft import PeftModel
    return is_peft_available() and isinstance(extract_model_from_parallel(model), PeftModel)
def check_device_same(first_device, second_device):
    if first_device.type != second_device.type: return False
    if first_device.type == "cuda" and first_device.index is None: first_device = torch.device("cuda", index=0)
    if second_device.type == "cuda" and second_device.index is None: second_device = torch.device("cuda", index=0)
    return first_device == second_device
def convert_file_size_to_int(size: Union[int, str]):
    mem_size = -1
    err_msg = (f"`size` {size} is not in a valid format. Use an integer for bytes, or a string with an unit (like '5.0GB').")
    try:
        if isinstance(size, int): mem_size = size
        elif size.upper().endswith("GIB"): mem_size = int(float(size[:-3]) * (2**30))
        elif size.upper().endswith("MIB"): mem_size = int(float(size[:-3]) * (2**20))
        elif size.upper().endswith("KIB"): mem_size = int(float(size[:-3]) * (2**10))
        elif size.upper().endswith("GB"):
            int_size = int(float(size[:-2]) * (10**9))
            mem_size = int_size // 8 if size.endswith("b") else int_size
        elif size.upper().endswith("MB"):
            int_size = int(float(size[:-2]) * (10**6))
            mem_size = int_size // 8 if size.endswith("b") else int_size
        elif size.upper().endswith("KB"):
            int_size = int(float(size[:-2]) * (10**3))
            mem_size = int_size // 8 if size.endswith("b") else int_size
    except ValueError: raise ValueError(err_msg)
    if mem_size < 0: raise ValueError(err_msg)
    return mem_size
def dtype_byte_size(dtype: torch.dtype):
    if dtype == torch.bool: return 1 / 8
    elif dtype == CustomDtype.INT2: return 1 / 4
    elif dtype == CustomDtype.INT4: return 1 / 2
    elif dtype == CustomDtype.FP8: return 1
    elif is_torch_version(">=", "2.1.0") and dtype == torch.float8_e4m3fn: return 1
    bit_search = re.search(r"[^\d](\d+)$", str(dtype))
    if bit_search is None: raise ValueError(f"`dtype` is not a valid dtype: {dtype}.")
    bit_size = int(bit_search.groups()[0])
    return bit_size // 8
def id_tensor_storage(tensor: torch.Tensor) -> Tuple[torch.device, int, int]:
    _SIZE = {torch.int64: 8, torch.float32: 4, torch.int32: 4, torch.bfloat16: 2, torch.float16: 2, torch.int16: 2, torch.uint8: 1, torch.int8: 1, torch.bool: 1, torch.float64: 8}
    try:
        storage_ptr = tensor.untyped_storage().data_ptr()
        storage_size = tensor.untyped_storage().nbytes()
    except Exception:
        try:
            storage_ptr = tensor.storage().data_ptr()
            storage_size = tensor.storage().size() * _SIZE[tensor.dtype]
        except NotImplementedError:
            storage_ptr = 0
            storage_size = tensor.nelement() * _SIZE[tensor.dtype]
    return tensor.device, storage_ptr, storage_size
def set_module_tensor_to_device(module: nn.Module, tensor_name: str, device: Union[int, str, torch.device], value: Optional[torch.Tensor] = None,
dtype: Optional[Union[str, torch.dtype]] = None, fp16_statistics: Optional[torch.HalfTensor] = None, tied_params_map: Optional[Dict[int, Dict[torch.device, torch.Tensor]]] = None):
    if "." in tensor_name:
        splits = tensor_name.split(".")
        for split in splits[:-1]:
            new_module = getattr(module, split)
            if new_module is None: raise ValueError(f"{module} has no attribute {split}.")
            module = new_module
        tensor_name = splits[-1]
    if tensor_name not in module._parameters and tensor_name not in module._buffers: raise ValueError(f"{module} does not have a parameter or a buffer named {tensor_name}.")
    is_buffer = tensor_name in module._buffers
    old_value = getattr(module, tensor_name)
    if (value is not None and tied_params_map is not None and value.data_ptr() in tied_params_map and device in tied_params_map[value.data_ptr()]):
        module._parameters[tensor_name] = tied_params_map[value.data_ptr()][device]
        return
    elif (tied_params_map is not None and old_value.data_ptr() in tied_params_map and device in tied_params_map[old_value.data_ptr()]):
        module._parameters[tensor_name] = tied_params_map[old_value.data_ptr()][device]
        return
    if old_value.device == torch.device("meta") and device not in ["meta", torch.device("meta")] and value is None: raise ValueError(f"{tensor_name} is on the meta device, we need a `value` to put in on {device}.")
    param = module._parameters[tensor_name] if tensor_name in module._parameters else None
    param_cls = type(param)
    if value is not None:
        if old_value.shape != value.shape and param_cls.__name__ != "Params4bit": raise ValueError(f'Trying to set a tensor of shape {value.shape} in "{tensor_name}" (which has shape {old_value.shape}), this looks incorrect.')
        if dtype is None: value = value.to(old_value.dtype)
        elif not str(value.dtype).startswith(("torch.uint", "torch.int", "torch.bool")): value = value.to(dtype)
    device_quantization = None
    with torch.no_grad():
        if (param is not None and param.device.type != "cuda" and torch.device(device).type == "cuda" and param_cls.__name__ in ["Int8Params", "FP4Params", "Params4bit"]):
            device_quantization = device
            device = "cpu"
        if isinstance(device, int):
            if is_npu_available(): device = f"npu:{device}"
            elif is_mlu_available(): device = f"mlu:{device}"
            elif is_musa_available(): device = f"musa:{device}"
            elif is_xpu_available(): device = f"xpu:{device}"
        if "xpu" in str(device) and not is_xpu_available(): raise ValueError(f'{device} is not available, you should use device="cpu" instead')
        if value is None:
            new_value = old_value.to(device)
            if dtype is not None and device in ["meta", torch.device("meta")]:
                if not str(old_value.dtype).startswith(("torch.uint", "torch.int", "torch.bool")): new_value = new_value.to(dtype)
                if not is_buffer: module._parameters[tensor_name] = param_cls(new_value, requires_grad=old_value.requires_grad)
        elif isinstance(value, torch.Tensor): new_value = value.to(device)
        else: new_value = torch.tensor(value, device=device)
        if device_quantization is not None: device = device_quantization
        if is_buffer: module._buffers[tensor_name] = new_value
        elif value is not None or not check_device_same(torch.device(device), module._parameters[tensor_name].device):
            param_cls = type(module._parameters[tensor_name])
            kwargs = module._parameters[tensor_name].__dict__
            if param_cls.__name__ in ["Int8Params", "FP4Params", "Params4bit"]:
                if param_cls.__name__ == "Int8Params" and new_value.dtype == torch.float32: new_value = new_value.to(torch.float16)
                if device == "cpu" and param_cls.__name__ == "Int8Params":
                    new_value = param_cls(new_value, requires_grad=old_value.requires_grad, **kwargs).to(0).to("cpu")
                    new_value.CB = new_value.CB.to("cpu")
                    new_value.SCB = new_value.SCB.to("cpu")
                else: new_value = param_cls(new_value, requires_grad=old_value.requires_grad, **kwargs).to(device)
            elif param_cls.__name__ in ["QTensor", "QBitsTensor"]: new_value = torch.nn.Parameter(new_value, requires_grad=old_value.requires_grad).to(device)
            elif param_cls.__name__ in ["AffineQuantizedTensor"]: new_value = torch.nn.Parameter(param_cls(new_value.layout_tensor, new_value.block_size,
            new_value.shape, new_value.quant_min, new_value.quant_max, new_value.zero_point_domain), requires_grad=old_value.requires_grad).to(device)
            else: new_value = param_cls(new_value, requires_grad=old_value.requires_grad).to(device)
            module._parameters[tensor_name] = new_value
            if fp16_statistics is not None:
                module._parameters[tensor_name].SCB = fp16_statistics.to(device)
                del fp16_statistics
            if (module.__class__.__name__ == "Linear8bitLt" and getattr(module.weight, "SCB", None) is None and str(module.weight.device) != "meta"):
                device_index = torch.device(device).index if torch.device(device).type == "cuda" else None
                if not getattr(module.weight, "SCB", None) and device_index is not None:
                    if module.bias is not None and module.bias.device.type != "meta": module = module.cuda(device_index)
                    elif module.bias is None: module = module.cuda(device_index)
            elif (module.__class__.__name__ == "Linear4bit" and getattr(module.weight, "quant_state", None) is None and str(module.weight.device) != "meta"):
                device_index = torch.device(device).index if torch.device(device).type == "cuda" else None
                if not getattr(module.weight, "quant_state", None) and device_index is not None: module.weight = module.weight.cuda(device_index)
    if device != "cpu": clear_device_cache()
    if (tied_params_map is not None and old_value.data_ptr() in tied_params_map and device not in tied_params_map[old_value.data_ptr()]): tied_params_map[old_value.data_ptr()][device] = new_value
    elif (value is not None and tied_params_map is not None and value.data_ptr() in tied_params_map and device not in tied_params_map[value.data_ptr()]): tied_params_map[value.data_ptr()][device] = new_value
def named_module_tensors(module: nn.Module, include_buffers: bool = True, recurse: bool = False, remove_non_persistent: bool = False):
    yield from module.named_parameters(recurse=recurse)
    if include_buffers:
        non_persistent_buffers = set()
        if remove_non_persistent: non_persistent_buffers = get_non_persistent_buffers(module, recurse=recurse)
        for named_buffer in module.named_buffers(recurse=recurse):
            name, _ = named_buffer
            if name not in non_persistent_buffers: yield named_buffer
def get_non_persistent_buffers(module: nn.Module, recurse: bool = False):
    non_persistent_buffers_set = module._non_persistent_buffers_set
    if recurse:
        for _, m in module.named_modules(): non_persistent_buffers_set |= m._non_persistent_buffers_set
    return non_persistent_buffers_set
class FindTiedParametersResult(list):
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)
    def values(self): return sum([x[1:] for x in self], [])
def check_tied_parameters_in_config(model: nn.Module):
    has_tied_word_embedding = False
    has_tied_encoder_decoder = False
    has_tied_module = False
    if "PreTrainedModel" in [c.__name__ for c in inspect.getmro(model.__class__)]:
        has_tied_word_embedding = (hasattr(model, "config") and getattr(model.config, "tie_word_embeddings", False) and model.get_output_embeddings())
        has_tied_encoder_decoder = (hasattr(model, "config") and getattr(model.config, "is_encoder_decoder", False) and getattr(model.config, "tie_encoder_decoder", False))
        has_tied_module = any(hasattr(module, "_tie_weights") for module in model.modules())
    return any([has_tied_word_embedding, has_tied_encoder_decoder, has_tied_module])
def _get_param_device(param, device_map):
    if param in device_map: return device_map[param]
    parent_param = ".".join(param.split(".")[:-1])
    if parent_param == param: raise ValueError(f"The `device_map` does not contain the module {param}.")
    else: return _get_param_device(parent_param, device_map)
def check_tied_parameters_on_same_device(tied_params, device_map):
    for tie_param in tied_params:
        tie_param_devices = {}
        for param in tie_param: tie_param_devices[param] = _get_param_device(param, device_map)
def _get_named_modules(module: torch.nn.Module, memo: Optional[Set[torch.nn.Module]] = None, prefix: str = "", remove_duplicate: bool = True):
    if memo is None: memo = set()
    if module not in memo:
        if remove_duplicate: memo.add(module)
        yield prefix, module
        for name, sub_module in module._modules.items():
            if sub_module is None: continue
            submodule_prefix = prefix + ("." if prefix else "") + name
            yield from _get_named_modules(sub_module, memo, submodule_prefix, remove_duplicate)
def _get_named_parameters(module: torch.nn.Module, prefix="", recurse=True, remove_duplicate: bool = True):
    memo = set()
    modules = (_get_named_modules(module, prefix=prefix, remove_duplicate=remove_duplicate) if recurse else [(prefix, module)])
    for module_prefix, module in modules:
        members = module._parameters.items()
        for k, v in members:
            if v is None or v in memo: continue
            if remove_duplicate: memo.add(v)
            name = module_prefix + ("." if module_prefix else "") + k
            yield name, v
def find_tied_parameters(model: torch.nn.Module, **kwargs):
    all_named_parameters = {name: param for name, param in _get_named_parameters(model, remove_duplicate=False)}
    no_duplicate_named_parameters = {name: param for name, param in _get_named_parameters(model, remove_duplicate=True)}
    tied_param_names = set(all_named_parameters.keys()) - set(no_duplicate_named_parameters.keys())
    tied_param_groups = {}
    for tied_param_name in tied_param_names:
        tied_param = all_named_parameters[tied_param_name]
        for param_name, param in no_duplicate_named_parameters.items():
            if param is tied_param:
                if param_name not in tied_param_groups: tied_param_groups[param_name] = []
                tied_param_groups[param_name].append(tied_param_name)
    return FindTiedParametersResult([sorted([weight] + list(set(tied))) for weight, tied in tied_param_groups.items()])
def retie_parameters(model, tied_params):
    for tied_group in tied_params:
        param_to_tie = None
        for param_name in tied_group:
            module = model
            splits = param_name.split(".")
            for split in splits[:-1]: module = getattr(module, split)
            param = getattr(module, splits[-1])
            if param_to_tie is None and param.device != torch.device("meta"):
                param_to_tie = param
                break
        if param_to_tie is not None:
            for param_name in tied_group:
                module = model
                splits = param_name.split(".")
                for split in splits[:-1]: module = getattr(module, split)
                setattr(module, splits[-1], param_to_tie)
def _get_proper_dtype(dtype: Union[str, torch.device]) -> torch.dtype:
    if isinstance(dtype, str):
        dtype = dtype.replace("torch.", "")
        dtype = getattr(torch, dtype)
    return dtype
def compute_module_sizes(model: nn.Module, dtype: Optional[Union[str, torch.device]] = None, special_dtypes: Optional[Dict[str, Union[str, torch.device]]] = None, buffers_only: bool = False):
    if dtype is not None:
        dtype = _get_proper_dtype(dtype)
        dtype_size = dtype_byte_size(dtype)
    if special_dtypes is not None:
        special_dtypes = {key: _get_proper_dtype(dtyp) for key, dtyp in special_dtypes.items()}
        special_dtypes_size = {key: dtype_byte_size(dtyp) for key, dtyp in special_dtypes.items()}
    module_sizes = defaultdict(int)
    module_list = []
    if not buffers_only: module_list = named_module_tensors(model, recurse=True)
    else: module_list = model.named_buffers(recurse=True)
    for name, tensor in module_list:
        if special_dtypes is not None and name in special_dtypes: size = tensor.numel() * special_dtypes_size[name]
        elif dtype is None: size = tensor.numel() * dtype_byte_size(tensor.dtype)
        elif str(tensor.dtype).startswith(("torch.uint", "torch.int", "torch.bool")): size = tensor.numel() * dtype_byte_size(tensor.dtype)
        else: size = tensor.numel() * min(dtype_size, dtype_byte_size(tensor.dtype))
        name_parts = name.split(".")
        for idx in range(len(name_parts) + 1): module_sizes[".".join(name_parts[:idx])] += size
    return module_sizes
def compute_module_total_buffer_size(model: nn.Module, dtype: Optional[Union[str, torch.device]] = None, special_dtypes: Optional[Dict[str, Union[str, torch.device]]] = None):
    module_sizes = compute_module_sizes(model, dtype=dtype, special_dtypes=special_dtypes, buffers_only=True)
    return module_sizes.get("", 0)
def get_max_layer_size(modules: List[Tuple[str, torch.nn.Module]], module_sizes: Dict[str, int], no_split_module_classes: List[str]):
    max_size = 0
    layer_names = []
    modules_to_treat = modules.copy()
    while len(modules_to_treat) > 0:
        module_name, module = modules_to_treat.pop(0)
        modules_children = list(module.named_children()) if isinstance(module, torch.nn.Module) else []
        if len(modules_children) == 0 or module.__class__.__name__ in no_split_module_classes:
            size = module_sizes[module_name]
            if size > max_size:
                max_size = size
                layer_names = [module_name]
            elif size == max_size: layer_names.append(module_name)
        else: modules_to_treat = [(f"{module_name}.{n}", v) for n, v in modules_children] + modules_to_treat
    return max_size, layer_names
def get_max_memory(max_memory: Optional[Dict[Union[int, str], Union[int, str]]] = None):
    import psutil
    if max_memory is None:
        max_memory = {}
        if is_npu_available():
            for i in range(torch.npu.device_count()):
                try:
                    _ = torch.tensor(0, device=torch.device("npu", i))
                    max_memory[i] = torch.npu.mem_get_info(i)[0]
                except Exception: continue
        elif is_mlu_available():
            for i in range(torch.mlu.device_count()):
                try:
                    _ = torch.tensor(0, device=torch.device("mlu", i))
                    max_memory[i] = torch.mlu.mem_get_info(i)[0]
                except Exception: continue
        elif is_musa_available():
            for i in range(torch.musa.device_count()):
                try:
                    _ = torch.tensor(0, device=torch.device("musa", i))
                    max_memory[i] = torch.musa.mem_get_info(i)[0]
                except Exception: continue
        elif is_xpu_available():
            for i in range(torch.xpu.device_count()):
                try:
                    _ = torch.tensor(0, device=torch.device("xpu", i))
                    max_memory[i] = get_xpu_available_memory(i)
                except Exception: continue
        else:
            for i in range(torch.cuda.device_count()):
                try:
                    _ = torch.tensor([0], device=i)
                    max_memory[i] = torch.cuda.mem_get_info(i)[0]
                except Exception: continue
        if is_mps_available(): max_memory["mps"] = psutil.virtual_memory().available
        else: max_memory["cpu"] = psutil.virtual_memory().available
        return max_memory
    for key in max_memory:
        if isinstance(max_memory[key], str): max_memory[key] = convert_file_size_to_int(max_memory[key])
    gpu_devices = [k for k in max_memory.keys() if isinstance(k, int)]
    gpu_devices.sort()
    if is_npu_available(): num_devices = torch.npu.device_count()
    elif is_mlu_available(): num_devices = torch.mlu.device_count()
    elif is_musa_available(): num_devices = torch.musa.device_count()
    elif is_xpu_available(): num_devices = torch.xpu.device_count()
    else: num_devices = torch.cuda.device_count()
    all_devices = gpu_devices + [k for k in ["mps", "cpu", "disk"] if k in max_memory.keys()]
    for k in max_memory.keys():
        if k not in all_devices: raise ValueError(f"Device {k} is not recognized, available devices are integers(for GPU/XPU), 'mps', 'cpu' and 'disk'")
    max_memory = {k: max_memory[k] for k in all_devices}
    return max_memory
def clean_device_map(device_map: Dict[str, Union[int, str, torch.device]], module_name: str = ""):
    prefix = "" if module_name == "" else f"{module_name}."
    values = [v for k, v in device_map.items() if k.startswith(prefix)]
    if len(set(values)) == 1 and len(values) > 1:
        for k in [k for k in device_map if k.startswith(prefix)]: del device_map[k]
        device_map[module_name] = values[0]
    children_modules = [k for k in device_map.keys() if k.startswith(prefix) and len(k) > len(module_name)]
    idx = len(module_name.split(".")) + 1 if len(module_name) > 0 else 1
    children_modules = set(".".join(k.split(".")[:idx]) for k in children_modules)
    for child in children_modules: clean_device_map(device_map, module_name=child)
    return device_map
def load_offloaded_weights(model, index, offload_folder):
    if index is None or len(index) == 0: return
    for param_name, metadata in index.items():
        if "SCB" in param_name: continue
        fp16_statistics = None
        if "weight" in param_name and param_name.replace("weight", "SCB") in index.keys():
            weight_name = param_name.replace("weight", "SCB")
            fp16_statistics = load_offloaded_weight(os.path.join(offload_folder, f"{weight_name}.dat"), index[weight_name])
        tensor_file = os.path.join(offload_folder, f"{param_name}.dat")
        weight = load_offloaded_weight(tensor_file, metadata)
        set_module_tensor_to_device(model, param_name, "cpu", value=weight, fp16_statistics=fp16_statistics)
def get_module_leaves(module_sizes):
    module_children = {}
    for module in module_sizes:
        if module == "" or "." not in module: continue
        parent = module.rsplit(".", 1)[0]
        module_children[parent] = module_children.get(parent, 0) + 1
    leaves = [module for module in module_sizes if module_children.get(module, 0) == 0 and module != ""]
    return leaves
def get_balanced_memory(model: nn.Module, max_memory: Optional[Dict[Union[int, str], Union[int, str]]] = None, no_split_module_classes: Optional[List[str]] = None,
dtype: Optional[Union[str, torch.dtype]] = None, special_dtypes: Optional[Dict[str, Union[str, torch.device]]] = None, low_zero: bool = False):
    user_not_set_max_memory = max_memory is None
    max_memory = get_max_memory(max_memory)
    if is_npu_available(): expected_device_type = "npu"
    elif is_mlu_available(): expected_device_type = "mlu"
    elif is_musa_available(): expected_device_type = "musa"
    elif is_xpu_available(): expected_device_type = "xpu"
    else: expected_device_type = "cuda"
    num_devices = len([d for d in max_memory if torch.device(d).type == expected_device_type and max_memory[d] > 0])
    if num_devices == 0: return max_memory
    if num_devices == 1:
        low_zero = False
        if user_not_set_max_memory:
            for key in max_memory.keys():
                if isinstance(key, int):
                    max_memory[key] *= 0.9
                    break
    module_sizes = compute_module_sizes(model, dtype=dtype, special_dtypes=special_dtypes)
    per_gpu = module_sizes[""] // (num_devices - 1 if low_zero else num_devices)
    if no_split_module_classes is None: no_split_module_classes = []
    elif not isinstance(no_split_module_classes, (list, tuple)): no_split_module_classes = [no_split_module_classes]
    if len(no_split_module_classes) > 0:
        no_split_children = {}
        for name, size in module_sizes.items():
            if name == "": continue
            submodule = model
            for submodule_name in name.split("."): submodule = getattr(submodule, submodule_name)
            class_name = submodule.__class__.__name__
            if class_name in no_split_module_classes and class_name not in no_split_children: no_split_children[class_name] = size
            if set(no_split_children.keys()) == set(no_split_module_classes): break
        buffer = max(no_split_children.values()) if len(no_split_children) > 0 else 0
    else: buffer = 0
    leaves = get_module_leaves(module_sizes)
    module_sizes = {n: v for n, v in module_sizes.items() if n not in leaves}
    leaves = get_module_leaves(module_sizes)
    mean_leaves = int(sum([module_sizes[n] for n in leaves]) / max(len(leaves), 1))
    buffer = int(1.25 * max(buffer, mean_leaves))
    per_gpu += buffer
    gpus_idx_list = list(sorted(device_id for device_id, device_mem in max_memory.items() if isinstance(device_id, int) and device_mem > 0))
    for idx in gpus_idx_list[:-1]: max_memory[idx] = min(max_memory[0] if low_zero and idx == 0 else per_gpu, max_memory[idx])
    if low_zero:
        min_zero = max(0, module_sizes[""] - sum([max_memory[i] for i in range(1, num_devices)]))
        max_memory[0] = min(min_zero, max_memory[0])
    return max_memory
def calculate_maximum_sizes(model: torch.nn.Module):
    sizes = compute_module_sizes(model)
    no_split_modules = getattr(model, "_no_split_modules", None)
    if no_split_modules is None: no_split_modules = []
    modules_to_treat = (list(model.named_parameters(recurse=False)) + list(model.named_children()) + list(model.named_buffers(recurse=False)))
    largest_layer = get_max_layer_size(modules_to_treat, sizes, no_split_modules)
    total_size = sizes[""]
    return total_size, largest_layer
def infer_auto_device_map(model: nn.Module, max_memory: Optional[Dict[Union[int, str], Union[int, str]]] = None, no_split_module_classes: Optional[List[str]] = None,
dtype: Optional[Union[str, torch.dtype]] = None, special_dtypes: Optional[Dict[str, Union[str, torch.dtype]]] = None, verbose: bool = False,
clean_result: bool = True, offload_buffers: bool = False):
    max_memory = get_max_memory(max_memory)
    if no_split_module_classes is None: no_split_module_classes = []
    elif not isinstance(no_split_module_classes, (list, tuple)): no_split_module_classes = [no_split_module_classes]
    devices = list(max_memory.keys())
    if "disk" not in devices: devices.append("disk")
    gpus = [device for device in devices if device not in ["cpu", "disk"]]
    if "mps" in gpus: main_devices = ["mps"]
    elif len(gpus) > 0: main_devices = [gpus[0], "cpu"]
    else: main_devices = ["cpu"]
    module_sizes = compute_module_sizes(model, dtype=dtype, special_dtypes=special_dtypes)
    tied_parameters = find_tied_parameters(model)
    device_map = OrderedDict()
    current_device = 0
    current_memory_used = 0
    device_memory_used = {}
    device_buffer_sizes = {}
    modules_to_treat = (list(model.named_parameters(recurse=False)) + list(model.named_children()) + list(model.named_buffers(recurse=False)))
    max_layer_size, max_layer_names = get_max_layer_size(modules_to_treat, module_sizes, no_split_module_classes)
    while len(modules_to_treat) > 0:
        name, module = modules_to_treat.pop(0)
        max_layer_names = [n for n in max_layer_names if n != name and not n.startswith(name + ".")]
        if len(max_layer_names) == 0: max_layer_size, max_layer_names = get_max_layer_size([(n, m) for n, m in modules_to_treat if isinstance(m, torch.nn.Module)], module_sizes, no_split_module_classes)
        module_size = module_sizes[name]
        tied_param_goups = [tied_group for tied_group in tied_parameters if any(name + "." in k + "." for k in tied_group) and not all(name + "." in k + "." for k in tied_group)]
        tied_params = sum([[p for p in tied_group if name + "." not in p + "."] for tied_group in tied_param_goups], [])
        device = devices[current_device]
        current_max_size = max_memory[device] if device != "disk" else None
        current_memory_reserved = 0
        if devices[current_device] in main_devices:
            current_max_size = current_max_size - max_layer_size
            current_memory_reserved = max_layer_size
        if current_max_size is not None and current_memory_used + module_size > current_max_size:
            modules_children = ([] if isinstance(module, nn.Parameter) or isinstance(module, torch.Tensor) else list(module.named_children()))
            if len(modules_children) == 0 or module.__class__.__name__ in no_split_module_classes:
                device_memory_used[device] = current_memory_used + current_memory_reserved
                current_device += 1
                modules_to_treat = [(name, module)] + modules_to_treat
                current_memory_used = 0
            else:
                modules_children = list(module.named_parameters(recurse=False)) + modules_children
                modules_to_treat = [(f"{name}.{n}", v) for n, v in modules_children] + modules_to_treat
                max_layer_size, max_layer_names = get_max_layer_size([(n, m) for n, m in modules_to_treat if isinstance(m, torch.nn.Module)], module_sizes, no_split_module_classes)
        elif len(tied_params) > 0:
            tied_module_names = []
            tied_modules = []
            for tied_param in tied_params:
                tied_module_index = [i for i, (n, _) in enumerate(modules_to_treat) if n in tied_param][0]
                tied_module_names.append(modules_to_treat[tied_module_index][0])
                tied_modules.append(modules_to_treat[tied_module_index][1])
            module_size_with_ties = module_size
            for tied_param, tied_module_name in zip(tied_params, tied_module_names): module_size_with_ties += module_sizes[tied_module_name] - module_sizes[tied_param]
            if current_max_size is None or current_memory_used + module_size_with_ties <= current_max_size:
                current_memory_used += module_size_with_ties
                device_map[name] = devices[current_device]
                for tied_module_name in tied_module_names:
                    if tied_module_name in [m[0] for m in modules_to_treat]:
                        tied_module_index = [i for i, (n, _) in enumerate(modules_to_treat) if n == tied_module_name][0]
                        modules_to_treat.pop(tied_module_index)
                    device_map[tied_module_name] = devices[current_device]
                if not offload_buffers and isinstance(module, nn.Module):
                    current_buffer_size = compute_module_total_buffer_size(module, dtype=dtype, special_dtypes=special_dtypes)
                    device_buffer_sizes[device] = device_buffer_sizes.get(device, 0) + current_buffer_size
            else:
                split_happened = False
                for tied_module_name, tied_module in zip(tied_module_names, tied_modules):
                    tied_module_children = list(tied_module.named_children())
                    if len(tied_module_children) == 0 or tied_module.__class__.__name__ in no_split_module_classes: continue
                    tied_module_children = list(tied_module.named_parameters(recurse=False)) + tied_module_children
                    tied_module_children = [(f"{tied_module_name}.{n}", v) for n, v in tied_module_children]
                    tied_module_index = [i for i, (n, _) in enumerate(modules_to_treat) if n == tied_module_name][0]
                    modules_to_treat = ([(name, module)] + modules_to_treat[:tied_module_index] + tied_module_children + modules_to_treat[tied_module_index + 1 :])
                    max_layer_size, max_layer_names = get_max_layer_size([(n, m) for n, m in modules_to_treat if isinstance(m, torch.nn.Module)], module_sizes, no_split_module_classes)
                    split_happened = True
                    break
                if not split_happened:
                    device_memory_used[device] = current_memory_used + current_memory_reserved
                    current_device += 1
                    modules_to_treat = [(name, module)] + modules_to_treat
                    current_memory_used = 0
        else:
            current_memory_used += module_size
            device_memory_used[device] = current_memory_used + current_memory_reserved
            device_map[name] = devices[current_device]
            if not offload_buffers and isinstance(module, nn.Module):
                current_buffer_size = compute_module_total_buffer_size(module, dtype=dtype, special_dtypes=special_dtypes)
                device_buffer_sizes[device] = device_buffer_sizes.get(device, 0) + current_buffer_size
    if clean_result: device_map = clean_device_map(device_map)
    non_gpu_buffer_size = device_buffer_sizes.get("cpu", 0) + device_buffer_sizes.get("disk", 0)
    if non_gpu_buffer_size > 0 and not offload_buffers:
        is_buffer_fit_any_gpu = False
        for gpu_device, gpu_max_memory in max_memory.items():
            if gpu_device == "cpu" or gpu_device == "disk": continue
            if not is_buffer_fit_any_gpu:
                gpu_memory_used = device_memory_used.get(gpu_device, 0)
                if gpu_max_memory >= non_gpu_buffer_size + gpu_memory_used: is_buffer_fit_any_gpu = True
    return device_map
def check_device_map(model: nn.Module, device_map: Dict[str, Union[int, str, torch.device]]):
    all_model_tensors = [name for name, _ in model.state_dict().items()]
    for module_name in device_map.keys():
        if module_name == "":
            all_model_tensors.clear()
            break
        else: all_model_tensors = [name for name in all_model_tensors if not name == module_name and not name.startswith(module_name + ".")]
    if len(all_model_tensors) > 0:
        non_covered_params = ", ".join(all_model_tensors)
        raise ValueError(f"The device_map provided does not give any device for the following parameters: {non_covered_params}")
def load_state_dict(checkpoint_file, device_map=None):
    if checkpoint_file.endswith(".safetensors"):
        with safe_open(checkpoint_file, framework="pt") as f:
            metadata = f.metadata()
            weight_names = f.keys()
        if metadata is None: metadata = {"format": "pt"}
        if metadata.get("format") not in ["pt", "tf", "flax"]: raise OSError(f"The safetensors archive passed at {checkpoint_file} does not contain the valid metadata. Make sure you save your model with the `save_pretrained` method.")
        elif metadata["format"] != "pt": raise ValueError(f"The checkpoint passed was saved with {metadata['format']}, we need a the pt format.")
        if device_map is None: return safe_load_file(checkpoint_file)
        else:
            if len(set(device_map.values())) == 1:
                device = list(device_map.values())[0]
                target_device = device
                if is_xpu_available():
                    if compare_versions("safetensors", "<", "0.4.2"): raise ImportError("Safetensors version must be >= 0.4.2 for XPU. Please upgrade safetensors.")
                    if isinstance(device, int): target_device = f"xpu:{device}"
                return safe_load_file(checkpoint_file, device=target_device)
            devices = list(set(device_map.values()) - {"disk"})
            if "cpu" not in devices: devices.append("cpu")
            device_weights = {device: [] for device in devices}
            for module_name, device in device_map.items():
                if device in devices: device_weights[device].extend([k for k in weight_names if k == module_name or k.startswith(module_name + ".")])
            device_weights["cpu"].extend([k for k in weight_names if k not in sum(device_weights.values(), [])])
            tensors = {}
            if is_tqdm_available(): progress_bar = tqdm(main_process_only=False, total=sum([len(device_weights[device]) for device in devices]), unit="w", smoothing=0, leave=False)
            else: progress_bar = None
            for device in devices:
                target_device = device
                if is_xpu_available():
                    if compare_versions("safetensors", "<", "0.4.2"): raise ImportError("Safetensors version must be >= 0.4.2 for XPU. Please upgrade safetensors.")
                    if isinstance(device, int): target_device = f"xpu:{device}"
                with safe_open(checkpoint_file, framework="pt", device=target_device) as f:
                    for key in device_weights[device]:
                        if progress_bar is not None:
                            progress_bar.set_postfix(dev=device, refresh=False)
                            progress_bar.set_description(key)
                        tensors[key] = f.get_tensor(key)
                        if progress_bar is not None: progress_bar.update()
            if progress_bar is not None: progress_bar.close()
            return tensors
    else: return torch.load(checkpoint_file, map_location=torch.device("cpu"))
def get_state_dict_offloaded_model(model: nn.Module):
    from ..hooks import AlignDevicesHook
    state_dict = {}
    placeholders = set()
    for name, module in model.named_modules():
        if name == "": continue
        if hasattr(module, "_hf_hook") and isinstance(module._hf_hook, AlignDevicesHook) and module._hf_hook.offload:
            original_device = module._hf_hook.execution_device
            module._hf_hook.execution_device = "cpu"
            try: module._hf_hook.pre_forward(module)
            except MemoryError: raise MemoryError("Offloaded module must fit in CPU memory to call save_model!") from None
            module_state_dict = module.state_dict()
            module._hf_hook.post_forward(module, torch.tensor([]))
            module._hf_hook.execution_device = original_device
        else: module_state_dict = module.state_dict()
        for key in module_state_dict:
            if module_state_dict[key].device == torch.device("meta"):
                placeholders.add(name + f".{key}")
                continue
            params = module_state_dict[key]
            state_dict[name + f".{key}"] = params
    for key in placeholders.copy():
        if key in state_dict: placeholders.remove(key)
    return state_dict
def get_state_dict_from_offload(module: nn.Module, module_name: str, state_dict: Dict[str, Union[str, torch.tensor]], device_to_put_offload: Union[int, str, torch.device] = "cpu"):
    from ..hooks import AlignDevicesHook
    root = module_name[: module_name.rfind(".")]
    preforward = False
    if hasattr(module, "_hf_hook") and isinstance(module._hf_hook, AlignDevicesHook) and module._hf_hook.offload:
        original_device = module._hf_hook.execution_device
        module._hf_hook.execution_device = device_to_put_offload
        module._hf_hook.pre_forward(module)
        preforward = True
    for m_key in module.state_dict():
        params = module.state_dict()[m_key]
        if (root + f".{m_key}") in state_dict: state_dict[root + f".{m_key}"] = params
    if preforward:
        module._hf_hook.post_forward(module, torch.tensor([]))
        module._hf_hook.execution_device = original_device
    return state_dict
def load_checkpoint_in_model(model: nn.Module, checkpoint: Union[str, os.PathLike], device_map: Optional[Dict[str, Union[int, str, torch.device]]] = None,
offload_folder: Optional[Union[str, os.PathLike]] = None, dtype: Optional[Union[str, torch.dtype]] = None, offload_state_dict: bool = False, offload_buffers: bool = False,
keep_in_fp32_modules: List[str] = None, offload_8bit_sapiens: bool = False, strict: bool = False):
    if offload_8bit_sapiens: from .sapiens import quantize_and_offload_8bit
    tied_params = find_tied_parameters(model)
    if device_map is not None: check_tied_parameters_on_same_device(tied_params, device_map)
    if offload_folder is None and device_map is not None and "disk" in device_map.values(): raise ValueError("At least one of the model submodule will be offloaded to disk, please pass along an `offload_folder`.")
    elif offload_folder is not None and device_map is not None and "disk" in device_map.values(): os.makedirs(offload_folder, exist_ok=True)
    if isinstance(dtype, str):
        dtype = dtype.replace("torch.", "")
        dtype = getattr(torch, dtype)
    checkpoint_files = None
    index_filename = None
    if os.path.isfile(checkpoint):
        if str(checkpoint).endswith(".json"): index_filename = checkpoint
        else: checkpoint_files = [checkpoint]
    elif os.path.isdir(checkpoint):
        potential_state_bin = [f for f in os.listdir(checkpoint) if f == WEIGHTS_NAME]
        potential_state_safetensor = [f for f in os.listdir(checkpoint) if f == SAFE_WEIGHTS_NAME]
        if len(potential_state_bin) == 1: checkpoint_files = [os.path.join(checkpoint, potential_state_bin[0])]
        elif len(potential_state_safetensor) == 1: checkpoint_files = [os.path.join(checkpoint, potential_state_safetensor[0])]
        else:
            potential_index = [f for f in os.listdir(checkpoint) if f.endswith(".index.json")]
            if len(potential_index) == 0: raise ValueError(f"{checkpoint} is not a folder containing a `.index.json` file or a {WEIGHTS_NAME} or a {SAFE_WEIGHTS_NAME} file")
            elif len(potential_index) == 1: index_filename = os.path.join(checkpoint, potential_index[0])
            else: raise ValueError(f"{checkpoint} containing more than one `.index.json` file, delete the irrelevant ones.")
    else: raise ValueError(f"`checkpoint` should be the path to a file containing a whole state dict, or the index of a sharded checkpoint, or a folder containing a sharded checkpoint or the whole state dict, but got {checkpoint}.")
    if index_filename is not None:
        checkpoint_folder = os.path.split(index_filename)[0]
        with open(index_filename) as f: index = json.loads(f.read())
        if "weight_map" in index: index = index["weight_map"]
        checkpoint_files = sorted(list(set(index.values())))
        checkpoint_files = [os.path.join(checkpoint_folder, f) for f in checkpoint_files]
    offload_index = {}
    if offload_state_dict:
        state_dict_folder = tempfile.mkdtemp()
        state_dict_index = {}
    unexpected_keys = set()
    model_keys = set(model.state_dict().keys())
    buffer_names = [name for name, _ in model.named_buffers()]
    for checkpoint_file in checkpoint_files:
        loaded_checkpoint = load_state_dict(checkpoint_file, device_map=device_map)
        if device_map is None:
            model.load_state_dict(loaded_checkpoint, strict=strict)
            unexpected_keys.update(set(loaded_checkpoint.keys()) - model_keys)
        else:
            for param_name, param in loaded_checkpoint.items():
                if "SCB" in param_name: continue
                if param_name not in model_keys:
                    unexpected_keys.add(param_name)
                    if not strict: continue
                module_name = param_name
                while len(module_name) > 0 and module_name not in device_map: module_name = ".".join(module_name.split(".")[:-1])
                if module_name == "" and "" not in device_map: raise ValueError(f"{param_name} doesn't have any device set.")
                param_device = device_map[module_name]
                new_dtype = dtype
                if dtype is not None and torch.is_floating_point(param):
                    if keep_in_fp32_modules is not None and dtype == torch.float16:
                        proceed = False
                        for key in keep_in_fp32_modules:
                            if ((key in param_name) and (key + "." in param_name)) or key == param_name:
                                proceed = True
                                break
                        if proceed: new_dtype = torch.float32
                if "weight" in param_name and param_name.replace("weight", "SCB") in loaded_checkpoint.keys():
                    if param.dtype == torch.int8: fp16_statistics = loaded_checkpoint[param_name.replace("weight", "SCB")]
                else: fp16_statistics = None
                if param_device == "disk":
                    if offload_buffers or param_name not in buffer_names:
                        if new_dtype is None: new_dtype = param.dtype
                        if offload_8bit_sapiens:
                            quantize_and_offload_8bit(model, param, param_name, new_dtype, offload_folder, offload_index, fp16_statistics)
                            continue
                        else: set_module_tensor_to_device(model, param_name, "meta", dtype=new_dtype)
                        offload_weight(param, param_name, offload_folder, index=offload_index)
                elif param_device == "cpu" and offload_state_dict:
                    if new_dtype is None: new_dtype = param.dtype
                    if offload_8bit_sapiens: quantize_and_offload_8bit(model, param, param_name, new_dtype, state_dict_folder, state_dict_index, fp16_statistics)
                    else:
                        set_module_tensor_to_device(model, param_name, "meta", dtype=new_dtype)
                        offload_weight(param, param_name, state_dict_folder, index=state_dict_index)
                else: set_module_tensor_to_device(model, param_name, param_device, value=param, dtype=new_dtype, fp16_statistics=fp16_statistics)
        del loaded_checkpoint
        gc.collect()
    save_offload_index(offload_index, offload_folder)
    if offload_state_dict:
        load_offloaded_weights(model, state_dict_index, state_dict_folder)
        shutil.rmtree(state_dict_folder)
    retie_parameters(model, tied_params)
def get_mixed_precision_context_manager(native_amp: bool = False, autocast_kwargs: AutocastKwargs = None):
    state = AcceleratorState()
    if autocast_kwargs is None: autocast_kwargs = {}
    else: autocast_kwargs = autocast_kwargs.to_kwargs()
    if native_amp:
        device_type = ("cuda" if (state.distributed_type == DistributedType.XLA and is_torch_xla_available(check_is_gpu=True)) else state.device.type)
        if state.mixed_precision == "fp16": return torch.autocast(device_type=device_type, dtype=torch.float16, **autocast_kwargs)
        elif state.mixed_precision in ["bf16", "fp8"] and state.distributed_type in [DistributedType.NO, DistributedType.MULTI_CPU, DistributedType.MULTI_GPU,
        DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU, DistributedType.MULTI_XPU, DistributedType.FSDP, DistributedType.XLA]: return torch.autocast(device_type=device_type, dtype=torch.bfloat16, **autocast_kwargs)
        else: return torch.autocast(device_type=device_type, **autocast_kwargs)
    else: return contextlib.nullcontext()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
