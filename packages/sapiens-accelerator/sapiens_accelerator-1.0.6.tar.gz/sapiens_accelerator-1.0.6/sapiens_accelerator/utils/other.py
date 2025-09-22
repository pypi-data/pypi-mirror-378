"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import collections
import os
import platform
import re
import socket
from contextlib import contextmanager
from functools import partial, reduce
from types import MethodType
from typing import OrderedDict
import torch
from packaging.version import Version
from safetensors.torch import save_file as safe_save_file
from ..commands.config.default import write_basic_config
from ..logging import get_logger
from ..state import PartialState
from .constants import FSDP_PYTORCH_VERSION
from .dataclasses import DistributedType
from .imports import is_deepspeed_available, is_torch_distributed_available, is_torch_xla_available
from .modeling import id_tensor_storage
from .transformer_engine import convert_model
from .versions import is_torch_version
logger = get_logger(__name__)
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
def is_compiled_module(module):
    if is_torch_version("<", "2.0.0") or not hasattr(torch, "_dynamo"): return False
    return isinstance(module, torch._dynamo.eval_frame.OptimizedModule)
def extract_model_from_parallel(model, keep_fp32_wrapper: bool = True, recursive: bool = False):
    options = (torch.nn.parallel.DistributedDataParallel, torch.nn.DataParallel)
    is_compiled = is_compiled_module(model)
    if is_compiled:
        compiled_model = model
        model = model._orig_mod
    if is_deepspeed_available():
        from deepspeed import DeepSpeedEngine
        options += (DeepSpeedEngine,)
    if is_torch_version(">=", FSDP_PYTORCH_VERSION) and is_torch_distributed_available():
        from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
        options += (FSDP,)
    while isinstance(model, options): model = model.module
    if recursive:
        def _recursive_unwrap(module):
            if hasattr(module, "module"): unwrapped_module = _recursive_unwrap(module.module)
            else: unwrapped_module = module
            for name, child in unwrapped_module.named_children(): setattr(unwrapped_module, name, _recursive_unwrap(child))
            return unwrapped_module
        model = _recursive_unwrap(model)
    if not keep_fp32_wrapper:
        forward = model.forward
        original_forward = model.__dict__.pop("_original_forward", None)
        if original_forward is not None:
            while hasattr(forward, "__wrapped__"):
                forward = forward.__wrapped__
                if forward == original_forward: break
            model.forward = MethodType(forward, model)
        if getattr(model, "_converted_to_transformer_engine", False): convert_model(model, to_transformer_engine=False)
    if is_compiled:
        compiled_model._orig_mod = model
        model = compiled_model
    return model
def wait_for_everyone(): PartialState().wait_for_everyone()
def clean_state_dict_for_safetensors(state_dict: dict):
    ptrs = collections.defaultdict(list)
    for name, tensor in state_dict.items():
        if not isinstance(tensor, str): ptrs[id_tensor_storage(tensor)].append(name)
    shared_ptrs = {ptr: names for ptr, names in ptrs.items() if len(names) > 1}
    warn_names = set()
    for names in shared_ptrs.values():
        found_names = [name for name in names if name in state_dict]
        warn_names.update(found_names[1:])
        for name in found_names[1:]: del state_dict[name]
    state_dict = {k: v.contiguous() if isinstance(v, torch.Tensor) else v for k, v in state_dict.items()}
    return state_dict
def save(obj, f, save_on_each_node: bool = False, safe_serialization: bool = False):
    if PartialState().distributed_type == DistributedType.XLA: obj = xm._maybe_convert_to_cpu(obj)
    if safe_serialization:
        save_func = partial(safe_save_file, metadata={"format": "pt"})
        if isinstance(obj, OrderedDict): obj = clean_state_dict_for_safetensors(obj)
    else: save_func = torch.save
    if PartialState().is_main_process and not save_on_each_node: save_func(obj, f)
    elif PartialState().is_local_main_process and save_on_each_node: save_func(obj, f)
@contextmanager
def clear_environment():
    _old_os_environ = os.environ.copy()
    os.environ.clear()
    try: yield
    finally:
        os.environ.clear()
        os.environ.update(_old_os_environ)
@contextmanager
def patch_environment(**kwargs):
    existing_vars = {}
    for key, value in kwargs.items():
        key = key.upper()
        if key in os.environ: existing_vars[key] = os.environ[key]
        os.environ[key] = str(value)
    try: yield
    finally:
        for key in kwargs:
            key = key.upper()
            if key in existing_vars: os.environ[key] = existing_vars[key]
            else: os.environ.pop(key, None)
def get_pretty_name(obj):
    if not hasattr(obj, "__qualname__") and not hasattr(obj, "__name__"): obj = getattr(obj, "__class__", obj)
    if hasattr(obj, "__qualname__"): return obj.__qualname__
    if hasattr(obj, "__name__"): return obj.__name__
    return str(obj)
def merge_dicts(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else: destination[key] = value
    return destination
def is_port_in_use(port: int = None) -> bool:
    if port is None: port = 29500
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: return s.connect_ex(("localhost", port)) == 0
def convert_bytes(size):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024.0: return f"{round(size, 2)} {x}"
        size /= 1024.0
    return f"{round(size, 2)} PB"
def check_os_kernel():
    info = platform.uname()
    system = info.system
    if system != "Linux": return
    _, version, *_ = re.split(r"(\d+\.\d+\.\d+)", info.release)
    min_version = "5.5.0"
def recursive_getattr(obj, attr: str):
    def _getattr(obj, attr): return getattr(obj, attr)
    return reduce(_getattr, [obj] + attr.split("."))
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
