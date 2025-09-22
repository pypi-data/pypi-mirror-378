"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import functools
import gc
import importlib
import inspect
import warnings
import torch
from .imports import (is_cuda_available, is_ipex_available, is_mlu_available, is_mps_available, is_musa_available, is_npu_available, is_xpu_available)
from .versions import compare_versions
def clear_device_cache(garbage_collection=False):
    if garbage_collection: gc.collect()
    if is_xpu_available(): torch.xpu.empty_cache()
    elif is_mlu_available(): torch.mlu.empty_cache()
    elif is_musa_available(): torch.musa.empty_cache()
    elif is_npu_available(): torch.npu.empty_cache()
    elif is_mps_available(min_version="2.0"): torch.mps.empty_cache()
    elif is_cuda_available(): torch.cuda.empty_cache()
def release_memory(*objects):
    if not isinstance(objects, list): objects = list(objects)
    for i in range(len(objects)): objects[i] = None
    clear_device_cache(garbage_collection=True)
    return objects
def should_reduce_batch_size(exception: Exception) -> bool:
    _statements = ["CUDA out of memory.", "cuDNN error: CUDNN_STATUS_NOT_SUPPORTED.", "DefaultCPUAllocator: can't allocate memory"]
    if isinstance(exception, RuntimeError) and len(exception.args) == 1: return any(err in exception.args[0] for err in _statements)
    return False
def find_executable_batch_size(function: callable = None, starting_batch_size: int = 128):
    if function is None: return functools.partial(find_executable_batch_size, starting_batch_size=starting_batch_size)
    batch_size = starting_batch_size
    def decorator(*args, **kwargs):
        nonlocal batch_size
        clear_device_cache(garbage_collection=True)
        params = list(inspect.signature(function).parameters.keys())
        if len(params) < (len(args) + 1):
            arg_str = ", ".join([f"{arg}={value}" for arg, value in zip(params[1:], args[1:])])
            raise TypeError(f"Batch size was passed into `{function.__name__}` as the first argument when called. Remove this as the decorator already does so: `{function.__name__}({arg_str})`")
        while True:
            if batch_size == 0: raise RuntimeError("No executable batch size found, reached zero.")
            try: return function(batch_size, *args, **kwargs)
            except Exception as e:
                if should_reduce_batch_size(e):
                    clear_device_cache(garbage_collection=True)
                    batch_size //= 2
                else: raise
    return decorator
def get_xpu_available_memory(device_index: int):
    if is_ipex_available():
        ipex_version = importlib.metadata.version("intel_extension_for_pytorch")
        if compare_versions(ipex_version, ">=", "2.5"):
            from intel_extension_for_pytorch.xpu import mem_get_info
            return mem_get_info(device_index)[0]
    return torch.xpu.max_memory_allocated(device_index)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
