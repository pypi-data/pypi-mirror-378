"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import math
from types import MethodType
from typing import Any, Dict, List, Optional, Tuple, Union
from .state import PartialState
from .utils import (calculate_maximum_sizes, convert_bytes, copy_tensor_to_devices, ignorant_find_batch_size, infer_auto_device_map,
is_pippy_available, pad_input_tensors, send_to_device)
def generate_device_map(model, num_processes: int = 1, no_split_module_classes=None, max_memory: dict = None):
    if num_processes == 1: return infer_auto_device_map(model, no_split_module_classes=no_split_module_classes, clean_result=False)
    if max_memory is None:
        model_size, shared = calculate_maximum_sizes(model)
        memory = (model_size + shared[0]) / num_processes
        memory = convert_bytes(memory)
        value, ending = memory.split(" ")
        memory = math.ceil(float(value)) * 1.1
        memory = f"{memory} {ending}"
        max_memory = {i: memory for i in range(num_processes)}
    device_map = infer_auto_device_map(model, max_memory=max_memory, no_split_module_classes=no_split_module_classes, clean_result=False)
    return device_map
def find_pippy_batch_size(args, kwargs):
    found_batch_size = None
    if args is not None:
        for arg in args:
            found_batch_size = ignorant_find_batch_size(arg)
            if found_batch_size is not None: break
    if kwargs is not None and found_batch_size is None:
        for kwarg in kwargs.values():
            found_batch_size = ignorant_find_batch_size(kwarg)
            if found_batch_size is not None: break
    return found_batch_size
def build_pipeline(model, split_points, args, kwargs, num_chunks):
    from torch.distributed.pipelining import ScheduleGPipe, SplitPoint, pipeline
    state = PartialState()
    split_spec = {split_point: SplitPoint.BEGINNING for split_point in split_points}
    pipe = pipeline(model, mb_args=args, mb_kwargs=kwargs, split_spec=split_spec)
    stage = pipe.build_stage(state.local_process_index, device=state.device)
    schedule = ScheduleGPipe(stage, num_chunks)
    return schedule
def pippy_forward(forward, num_chunks, gather_output, *args, **kwargs):
    state = PartialState()
    output = None
    if state.num_processes == 1: output = forward(*args, **kwargs)
    elif state.is_local_main_process:
        found_batch_size = find_pippy_batch_size(args, kwargs)
        if found_batch_size is None: raise ValueError("Could not find batch size from args or kwargs")
        else:
            if found_batch_size != num_chunks:
                args = pad_input_tensors(args, found_batch_size, num_chunks)
                kwargs = pad_input_tensors(kwargs, found_batch_size, num_chunks)
        forward(*args, **kwargs)
    elif state.is_last_process: output = forward()
    else: forward()
    if gather_output: output = copy_tensor_to_devices(output)
    return output
def prepare_pippy(model, split_points: Optional[Union[str, List[str]]] = "auto", no_split_module_classes: Optional[List[str]] = None, example_args: Optional[Tuple[Any]] = (),
example_kwargs: Optional[Dict[str, Any]] = None, num_chunks: Optional[int] = None, gather_output: Optional[bool] = False):
    if not is_pippy_available(): raise ImportError("Using `torch.distributed.pipelining` requires PyTorch 2.4.0 or later.")
    state = PartialState()
    example_args = send_to_device(example_args, "cpu")
    example_kwargs = send_to_device(example_kwargs, "cpu")
    if num_chunks is None: num_chunks = state.num_processes
    if split_points == "auto":
        device_map = generate_device_map(model, num_chunks, no_split_module_classes=no_split_module_classes)
        split_points = []
        for i in range(1, num_chunks): split_points.append(next(k for k, v in device_map.items() if v == i))
    model.hf_split_points = split_points
    stage = build_pipeline(model, split_points, example_args, example_kwargs, num_chunks)
    model._original_forward = model.forward
    model._original_call = model.__call__
    model.pippy_stage = stage
    model.hf_split_points = split_points
    def forward(*args, **kwargs): return pippy_forward(stage.step, num_chunks, gather_output, *args, **kwargs)
    model_forward = MethodType(forward, model)
    forward.__wrapped__ = model_forward
    model.forward = forward
    return model
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
