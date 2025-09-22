"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import pickle
import warnings
from contextlib import contextmanager, nullcontext
from functools import update_wrapper, wraps
from typing import Any, Mapping
import torch
from ..state import AcceleratorState, PartialState
from .constants import TORCH_DISTRIBUTED_OPERATION_TYPES
from .dataclasses import DistributedType, TensorInformation
from .imports import (is_npu_available, is_torch_distributed_available, is_torch_version, is_torch_xla_available, is_xpu_available)
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
if is_torch_distributed_available(): from torch.distributed import ReduceOp
def is_torch_tensor(tensor): return isinstance(tensor, torch.Tensor)
def is_torch_xpu_tensor(tensor): return isinstance(tensor, torch.xpu.FloatTensor, torch.xpu.ByteTensor, torch.xpu.IntTensor, torch.xpu.LongTensor, torch.xpu.HalfTensor, torch.xpu.DoubleTensor, torch.xpu.BFloat16Tensor)
def is_tensor_information(tensor_info): return isinstance(tensor_info, TensorInformation)
def is_namedtuple(data): return isinstance(data, tuple) and hasattr(data, "_asdict") and hasattr(data, "_fields")
def honor_type(obj, generator):
    if is_namedtuple(obj): return type(obj)(*list(generator))
    else: return type(obj)(generator)
def recursively_apply(func, data, *args, test_type=is_torch_tensor, error_on_other_type=False, **kwargs):
    if isinstance(data, (tuple, list)): return honor_type(data, (recursively_apply(func, o, *args, test_type=test_type, error_on_other_type=error_on_other_type, **kwargs) for o in data))
    elif isinstance(data, Mapping): return type(data)({k: recursively_apply(func, v, *args, test_type=test_type, error_on_other_type=error_on_other_type, **kwargs) for k, v in data.items()})
    elif test_type(data): return func(data, *args, **kwargs)
    elif error_on_other_type: raise TypeError(f"Unsupported types ({type(data)}) passed to `{func.__name__}`. Only nested list/tuple/dicts of objects that are valid for `{test_type.__name__}` should be passed.")
    return data
def send_to_device(tensor, device, non_blocking=False, skip_keys=None):
    if is_torch_tensor(tensor) or hasattr(tensor, "to"):
        if device == "npu": device = "npu:0"
        if device == "xpu": device = "xpu:0"
        try: return tensor.to(device, non_blocking=non_blocking)
        except TypeError: return tensor.to(device)
        except AssertionError as error:
            if is_npu_available():
                if isinstance(device, int): device = f"npu:{device}"
            elif is_xpu_available():
                if isinstance(device, int): device = f"xpu:{device}"
            else: raise error
        try: return tensor.to(device, non_blocking=non_blocking)
        except TypeError: return tensor.to(device)
    elif isinstance(tensor, (tuple, list)): return honor_type(tensor, (send_to_device(t, device, non_blocking=non_blocking, skip_keys=skip_keys) for t in tensor))
    elif isinstance(tensor, Mapping):
        if isinstance(skip_keys, str): skip_keys = [skip_keys]
        elif skip_keys is None: skip_keys = []
        return type(tensor)({k: t if k in skip_keys else send_to_device(t, device, non_blocking=non_blocking, skip_keys=skip_keys) for k, t in tensor.items()})
    else: return tensor
def get_data_structure(data):
    def _get_data_structure(tensor): return TensorInformation(shape=tensor.shape, dtype=tensor.dtype)
    return recursively_apply(_get_data_structure, data)
def get_shape(data):
    def _get_shape(tensor): return list(tensor.shape)
    return recursively_apply(_get_shape, data)
def initialize_tensors(data_structure):
    def _initialize_tensor(tensor_info): return torch.empty(*tensor_info.shape, dtype=tensor_info.dtype)
    return recursively_apply(_initialize_tensor, data_structure, test_type=is_tensor_information)
def find_batch_size(data):
    if isinstance(data, (tuple, list, Mapping)) and (len(data) == 0): raise ValueError(f"Cannot find the batch size from empty {type(data)}.")
    if isinstance(data, (tuple, list)): return find_batch_size(data[0])
    elif isinstance(data, Mapping):
        for k in data.keys(): return find_batch_size(data[k])
    elif not isinstance(data, torch.Tensor): raise TypeError(f"Can only find the batch size of tensors but got {type(data)}.")
    return data.shape[0]
def ignorant_find_batch_size(data):
    try: return find_batch_size(data)
    except (ValueError, TypeError): pass
    return None
def listify(data):
    def _convert_to_list(tensor):
        tensor = tensor.detach().cpu()
        if tensor.dtype == torch.bfloat16: tensor = tensor.to(torch.float32)
        return tensor.tolist()
    return recursively_apply(_convert_to_list, data)
def _tpu_gather(tensor):
    def _tpu_gather_one(tensor):
        if tensor.ndim == 0: tensor = tensor.clone()[None]
        if not tensor.is_contiguous(): tensor = tensor.contiguous()
        return xm.all_gather(tensor)
    res = recursively_apply(_tpu_gather_one, tensor, error_on_other_type=True)
    xm.mark_step()
    return res
def _gpu_gather(tensor):
    state = PartialState()
    if is_torch_version(">=", "1.13"): gather_op = torch.distributed.all_gather_into_tensor
    else: gather_op = torch.distributed._all_gather_base
    def _gpu_gather_one(tensor):
        if tensor.ndim == 0: tensor = tensor.clone()[None]
        if not tensor.is_contiguous(): tensor = tensor.contiguous()
        if state.backend is not None and state.backend != "gloo":
            output_tensors = torch.empty(state.num_processes * tensor.numel(), dtype=tensor.dtype, device=state.device)
            gather_op(output_tensors, tensor)
            return output_tensors.view(-1, *tensor.size()[1:])
        else:
            output_tensors = [torch.empty_like(tensor) for _ in range(state.num_processes)]
            torch.distributed.all_gather(output_tensors, tensor)
            return torch.cat(output_tensors, dim=0)
    return recursively_apply(_gpu_gather_one, tensor, error_on_other_type=True)
class DistributedOperationException(Exception): pass
def verify_operation(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if PartialState().distributed_type == DistributedType.NO or not PartialState().debug: return function(*args, **kwargs)
        operation = f"{function.__module__}.{function.__name__}"
        if "tensor" in kwargs: tensor = kwargs["tensor"]
        else: tensor = args[0]
        if PartialState().device.type != find_device(tensor).type: raise DistributedOperationException(f"One or more of the tensors passed to {operation} were not on the {tensor.device.type} while the `Accelerator` is configured for {PartialState().device.type}. Please move it to the {PartialState().device.type} before calling {operation}.")
        shapes = get_shape(tensor)
        output = gather_object([shapes])
        if output[0] is not None:
            are_same = output.count(output[0]) == len(output)
            if not are_same:
                process_shape_str = "\n  - ".join([f"Process {i}: {shape}" for i, shape in enumerate(output)])
                raise DistributedOperationException(f"Cannot apply desired operation due to shape mismatches. All shapes across devices must be valid.\n\nOperation: `{operation}`\nInput shapes:\n  - {process_shape_str}")
        return function(*args, **kwargs)
    return wrapper
def chained_operation(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try: return function(*args, **kwargs)
        except DistributedOperationException as e:
            operation = f"{function.__module__}.{function.__name__}"
            raise DistributedOperationException(f"Error found while calling `{operation}`. Please see the earlier error for more details.") from e
    return wrapper
@verify_operation
def gather(tensor):
    if PartialState().distributed_type == DistributedType.XLA: return _tpu_gather(tensor)
    elif PartialState().distributed_type in TORCH_DISTRIBUTED_OPERATION_TYPES: return _gpu_gather(tensor)
    else: return tensor
def _gpu_gather_object(object: Any):
    output_objects = [None for _ in range(PartialState().num_processes)]
    torch.distributed.all_gather_object(output_objects, object)
    return [x for y in output_objects for x in y]
def gather_object(object: Any):
    if PartialState().distributed_type == DistributedType.XLA: raise NotImplementedError("gather objects in TPU is not supported")
    elif PartialState().distributed_type in TORCH_DISTRIBUTED_OPERATION_TYPES: return _gpu_gather_object(object)
    else: return object
def _gpu_broadcast(data, src=0):
    def _gpu_broadcast_one(tensor, src=0):
        torch.distributed.broadcast(tensor, src=src)
        return tensor
    return recursively_apply(_gpu_broadcast_one, data, error_on_other_type=True, src=src)
def _tpu_broadcast(tensor, src=0, name="broadcast tensor"):
    if isinstance(tensor, (list, tuple)): return honor_type(tensor, (_tpu_broadcast(t, name=f"{name}_{i}") for i, t in enumerate(tensor)))
    elif isinstance(tensor, Mapping): return type(tensor)({k: _tpu_broadcast(v, name=f"{name}_{k}") for k, v in tensor.items()})
    return xm.mesh_reduce(name, tensor, lambda x: x[src])
TENSOR_TYPE_TO_INT = {torch.float: 1, torch.double: 2, torch.half: 3, torch.bfloat16: 4, torch.uint8: 5, torch.int8: 6, torch.int16: 7, torch.int32: 8, torch.int64: 9, torch.bool: 10}
TENSOR_INT_TO_DTYPE = {v: k for k, v in TENSOR_TYPE_TO_INT.items()}
def gather_tensor_shape(tensor):
    max_tensor_dimension = 2**20
    state = PartialState()
    base_tensor = torch.empty(max_tensor_dimension, dtype=torch.int, device=state.device)
    if tensor is not None:
        shape = tensor.shape
        tensor_dtype = TENSOR_TYPE_TO_INT[tensor.dtype]
        base_tensor[: len(shape) + 1] = torch.tensor(list(shape) + [tensor_dtype], dtype=int)
    base_tensor = reduce(base_tensor, reduction="sum")
    base_tensor = base_tensor[base_tensor.nonzero()]
    dtype = int(base_tensor[-1:][0])
    base_tensor = base_tensor[:-1]
    return base_tensor, dtype
def copy_tensor_to_devices(tensor=None) -> torch.Tensor:
    state = PartialState()
    shape, dtype = gather_tensor_shape(tensor)
    if tensor is None: tensor = torch.zeros(shape, dtype=TENSOR_INT_TO_DTYPE[dtype]).to(state.device)
    return reduce(tensor, reduction="sum")
@verify_operation
def broadcast(tensor, from_process: int = 0):
    if PartialState().distributed_type == DistributedType.XLA: return _tpu_broadcast(tensor, src=from_process, name="sapiens_accelerator.utils.broadcast")
    elif PartialState().distributed_type in TORCH_DISTRIBUTED_OPERATION_TYPES: return _gpu_broadcast(tensor, src=from_process)
    else: return tensor
def broadcast_object_list(object_list, from_process: int = 0):
    if PartialState().distributed_type == DistributedType.XLA:
        for i, obj in enumerate(object_list): object_list[i] = xm.mesh_reduce("sapiens_accelerator.utils.broadcast_object_list", obj, lambda x: x[from_process])
    elif PartialState().distributed_type in TORCH_DISTRIBUTED_OPERATION_TYPES: torch.distributed.broadcast_object_list(object_list, src=from_process)
    return object_list
def slice_tensors(data, tensor_slice, process_index=None, num_processes=None):
    def _slice_tensor(tensor, tensor_slice): return tensor[tensor_slice]
    return recursively_apply(_slice_tensor, data, tensor_slice)
def concatenate(data, dim=0):
    if isinstance(data[0], (tuple, list)): return honor_type(data[0], (concatenate([d[i] for d in data], dim=dim) for i in range(len(data[0]))))
    elif isinstance(data[0], Mapping): return type(data[0])({k: concatenate([d[k] for d in data], dim=dim) for k in data[0].keys()})
    elif not isinstance(data[0], torch.Tensor): raise TypeError(f"Can only concatenate tensors but got {type(data[0])}")
    return torch.cat(data, dim=dim)
class CannotPadNestedTensorWarning(UserWarning): pass
@chained_operation
def pad_across_processes(tensor, dim=0, pad_index=0, pad_first=False):
    def _pad_across_processes(tensor, dim=0, pad_index=0, pad_first=False):
        if getattr(tensor, "is_nested", False): return tensor
        if dim >= len(tensor.shape): return tensor
        size = torch.tensor(tensor.shape, device=tensor.device)[None]
        sizes = gather(size).cpu()
        max_size = max(s[dim] for s in sizes)
        if max_size == tensor.shape[dim]: return tensor
        old_size = tensor.shape
        new_size = list(old_size)
        new_size[dim] = max_size
        new_tensor = tensor.new_zeros(tuple(new_size)) + pad_index
        if pad_first: indices = tuple(slice(max_size - old_size[dim], max_size) if i == dim else slice(None) for i in range(len(new_size)))
        else: indices = tuple(slice(0, old_size[dim]) if i == dim else slice(None) for i in range(len(new_size)))
        new_tensor[indices] = tensor
        return new_tensor
    return recursively_apply(_pad_across_processes, tensor, error_on_other_type=True, dim=dim, pad_index=pad_index, pad_first=pad_first)
def pad_input_tensors(tensor, batch_size, num_processes, dim=0):
    def _pad_input_tensors(tensor, batch_size, num_processes, dim=0):
        remainder = batch_size // num_processes
        last_inputs = batch_size - (remainder * num_processes)
        if batch_size // num_processes == 0: to_pad = num_processes - batch_size
        else: to_pad = num_processes - (batch_size // num_processes)
        if last_inputs > to_pad & to_pad < 1: to_pad = last_inputs - to_pad
        old_size = tensor.shape
        new_size = list(old_size)
        new_size[0] = batch_size + to_pad
        new_tensor = tensor.new_zeros(tuple(new_size))
        indices = tuple(slice(0, old_size[dim]) if i == dim else slice(None) for i in range(len(new_size)))
        new_tensor[indices] = tensor
        return new_tensor
    return recursively_apply(_pad_input_tensors, tensor, error_on_other_type=True, batch_size=batch_size, num_processes=num_processes, dim=dim)
@verify_operation
def reduce(tensor, reduction="mean", scale=1.0):
    def _reduce_across_processes(tensor, reduction="mean", scale=1.0):
        state = PartialState()
        cloned_tensor = tensor.clone()
        if state.distributed_type == DistributedType.NO: return cloned_tensor
        if state.distributed_type == DistributedType.XLA:
            xm.mark_step()
            xm.all_reduce(xm.REDUCE_SUM, [cloned_tensor], scale)
            xm.mark_step()
        elif state.distributed_type.value in TORCH_DISTRIBUTED_OPERATION_TYPES: torch.distributed.all_reduce(cloned_tensor, ReduceOp.SUM)
        if reduction == "mean": cloned_tensor /= state.num_processes
        return cloned_tensor
    return recursively_apply(_reduce_across_processes, tensor, error_on_other_type=True, reduction=reduction, scale=scale)
def convert_to_fp32(tensor):
    def _convert_to_fp32(tensor): return tensor.float()
    def _is_fp16_bf16_tensor(tensor): return (is_torch_tensor(tensor) or hasattr(tensor, "dtype")) and tensor.dtype in (torch.float16, torch.bfloat16)
    return recursively_apply(_convert_to_fp32, tensor, test_type=_is_fp16_bf16_tensor)
class ConvertOutputsToFp32:
    def __init__(self, model_forward):
        self.model_forward = model_forward
        update_wrapper(self, model_forward)
    def __call__(self, *args, **kwargs): return convert_to_fp32(self.model_forward(*args, **kwargs))
    def __getstate__(self): raise pickle.PicklingError("Cannot pickle a prepared model with automatic mixed precision, please unwrap the model with `Accelerator.unwrap_model(model)` before pickling it.")
def convert_outputs_to_fp32(model_forward):
    model_forward = ConvertOutputsToFp32(model_forward)
    def forward(*args, **kwargs): return model_forward(*args, **kwargs)
    forward.__wrapped__ = model_forward
    return forward
def find_device(data):
    if isinstance(data, Mapping):
        for obj in data.values():
            device = find_device(obj)
            if device is not None: return device
    elif isinstance(data, (tuple, list)):
        for obj in data:
            device = find_device(obj)
            if device is not None: return device
    elif isinstance(data, torch.Tensor): return data.device
@contextmanager
def GatheredParameters(params, modifier_rank=None, fwd_module=None, enabled=True):
    if AcceleratorState().distributed_type != DistributedType.DEEPSPEED or (AcceleratorState().deepspeed_plugin is not None and not AcceleratorState().deepspeed_plugin.is_zero3_init_enabled()): gather_param_context = nullcontext()
    else:
        import deepspeed
        gather_param_context = deepspeed.zero.GatheredParameters(params, modifier_rank=modifier_rank, fwd_module=fwd_module, enabled=enabled)
    with gather_param_context: yield
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
