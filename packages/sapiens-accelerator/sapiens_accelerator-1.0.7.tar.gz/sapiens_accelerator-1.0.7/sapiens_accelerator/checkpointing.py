"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import random
from pathlib import Path
from typing import List
import numpy as np
import torch
from safetensors.torch import load_model
from torch.cuda.amp import GradScaler
from .utils import (MODEL_NAME, OPTIMIZER_NAME, RNG_STATE_NAME, SAFE_MODEL_NAME, SAFE_WEIGHTS_NAME, SAMPLER_NAME, SCALER_NAME, SCHEDULER_NAME, WEIGHTS_NAME,
get_pretty_name, is_mlu_available, is_torch_xla_available, is_xpu_available, save)
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
from .logging import get_logger
from .state import PartialState
logger = get_logger(__name__)
def save_accelerator_state(output_dir: str, model_states: List[dict], optimizers: list, schedulers: list, dataloaders: list, process_index: int,
step: int, scaler: GradScaler = None, save_on_each_node: bool = False, safe_serialization: bool = True):
    output_dir = Path(output_dir)
    for i, state in enumerate(model_states):
        weights_name = WEIGHTS_NAME if not safe_serialization else SAFE_WEIGHTS_NAME
        if i > 0: weights_name = weights_name.replace(".", f"_{i}.")
        output_model_file = output_dir.joinpath(weights_name)
        save(state, output_model_file, save_on_each_node=save_on_each_node, safe_serialization=safe_serialization)
    for i, opt in enumerate(optimizers):
        state = opt.state_dict()
        optimizer_name = f"{OPTIMIZER_NAME}.bin" if i == 0 else f"{OPTIMIZER_NAME}_{i}.bin"
        output_optimizer_file = output_dir.joinpath(optimizer_name)
        save(state, output_optimizer_file, save_on_each_node=save_on_each_node, safe_serialization=False)
    for i, scheduler in enumerate(schedulers):
        state = scheduler.state_dict()
        scheduler_name = f"{SCHEDULER_NAME}.bin" if i == 0 else f"{SCHEDULER_NAME}_{i}.bin"
        output_scheduler_file = output_dir.joinpath(scheduler_name)
        save(state, output_scheduler_file, save_on_each_node=save_on_each_node, safe_serialization=False)
    for i, dataloader in enumerate(dataloaders):
        sampler_name = f"{SAMPLER_NAME}.bin" if i == 0 else f"{SAMPLER_NAME}_{i}.bin"
        output_sampler_file = output_dir.joinpath(sampler_name)
        from .data_loader import IterableDatasetShard, SeedableRandomSampler
        if isinstance(dataloader.dataset, IterableDatasetShard):
            sampler = dataloader.get_sampler()
            if isinstance(sampler, SeedableRandomSampler): save(sampler, output_sampler_file, save_on_each_node=save_on_each_node, safe_serialization=False)
        if getattr(dataloader, "use_stateful_dataloader", False):
            dataloader_state_dict_name = "dl_state_dict.bin" if i == 0 else f"dl_state_dict_{i}.bin"
            output_dataloader_state_dict_file = output_dir.joinpath(dataloader_state_dict_name)
            state_dict = dataloader.state_dict()
            torch.save(state_dict, output_dataloader_state_dict_file)
    if scaler is not None:
        state = scaler.state_dict()
        output_scaler_file = output_dir.joinpath(SCALER_NAME)
        torch.save(state, output_scaler_file)
    states = {}
    states_name = f"{RNG_STATE_NAME}_{process_index}.pkl"
    states["step"] = step
    states["random_state"] = random.getstate()
    states["numpy_random_seed"] = np.random.get_state()
    states["torch_manual_seed"] = torch.get_rng_state()
    if is_xpu_available(): states["torch_xpu_manual_seed"] = torch.xpu.get_rng_state_all()
    if is_mlu_available(): states["torch_mlu_manual_seed"] = torch.mlu.get_rng_state_all()
    else: states["torch_cuda_manual_seed"] = torch.cuda.get_rng_state_all()
    if is_torch_xla_available(): states["xm_seed"] = xm.get_rng_state()
    output_states_file = output_dir.joinpath(states_name)
    torch.save(states, output_states_file)
    return output_dir
def load_accelerator_state(input_dir, models, optimizers, schedulers, dataloaders, process_index, scaler=None, map_location=None, **load_model_func_kwargs):
    override_attributes = dict()
    if map_location not in [None, "cpu", "on_device"]: raise TypeError("Unsupported optimizer map location passed, please choose one of `None`, `'cpu'`, or `'on_device'`")
    if map_location is None: map_location = "cpu"
    elif map_location == "on_device": map_location = PartialState().device
    input_dir = Path(input_dir)
    for i, model in enumerate(models):
        ending = f"_{i}" if i > 0 else ""
        input_model_file = input_dir.joinpath(f"{SAFE_MODEL_NAME}{ending}.safetensors")
        if input_model_file.exists(): load_model(model, input_model_file, device=str(map_location), **load_model_func_kwargs)
        else:
            input_model_file = input_dir.joinpath(f"{MODEL_NAME}{ending}.bin")
            state_dict = torch.load(input_model_file, map_location=map_location)
            model.load_state_dict(state_dict, **load_model_func_kwargs)
    for i, opt in enumerate(optimizers):
        optimizer_name = f"{OPTIMIZER_NAME}.bin" if i == 0 else f"{OPTIMIZER_NAME}_{i}.bin"
        input_optimizer_file = input_dir.joinpath(optimizer_name)
        optimizer_state = torch.load(input_optimizer_file, map_location=map_location)
        optimizers[i].load_state_dict(optimizer_state)
    for i, scheduler in enumerate(schedulers):
        scheduler_name = f"{SCHEDULER_NAME}.bin" if i == 0 else f"{SCHEDULER_NAME}_{i}.bin"
        input_scheduler_file = input_dir.joinpath(scheduler_name)
        scheduler.load_state_dict(torch.load(input_scheduler_file))
    for i, dataloader in enumerate(dataloaders):
        sampler_name = f"{SAMPLER_NAME}.bin" if i == 0 else f"{SAMPLER_NAME}_{i}.bin"
        input_sampler_file = input_dir.joinpath(sampler_name)
        from .data_loader import IterableDatasetShard, SeedableRandomSampler
        if isinstance(dataloader.dataset, IterableDatasetShard):
            sampler = dataloader.get_sampler()
            if isinstance(sampler, SeedableRandomSampler): sampler = dataloader.set_sampler(torch.load(input_sampler_file))
        if getattr(dataloader, "use_stateful_dataloader", False):
            dataloader_state_dict_name = "dl_state_dict.bin" if i == 0 else f"dl_state_dict_{i}.bin"
            input_dataloader_state_dict_file = input_dir.joinpath(dataloader_state_dict_name)
            if input_dataloader_state_dict_file.exists():
                state_dict = torch.load(input_dataloader_state_dict_file)
                dataloader.load_state_dict(state_dict)
    if scaler is not None:
        input_scaler_file = input_dir.joinpath(SCALER_NAME)
        scaler.load_state_dict(torch.load(input_scaler_file))
    try:
        states = torch.load(input_dir.joinpath(f"{RNG_STATE_NAME}_{process_index}.pkl"))
        if "step" in states: override_attributes["step"] = states["step"]
        random.setstate(states["random_state"])
        np.random.set_state(states["numpy_random_seed"])
        torch.set_rng_state(states["torch_manual_seed"])
        if is_xpu_available(): torch.xpu.set_rng_state_all(states["torch_xpu_manual_seed"])
        if is_mlu_available(): torch.mlu.set_rng_state_all(states["torch_mlu_manual_seed"])
        else: torch.cuda.set_rng_state_all(states["torch_cuda_manual_seed"])
        if is_torch_xla_available(): xm.set_rng_state(states["xm_seed"])
    except Exception: pass
    return override_attributes
def save_custom_state(obj, path, index: int = 0, save_on_each_node: bool = False):
    save_location = Path(path) / f"custom_checkpoint_{index}.pkl"
    save(obj.state_dict(), save_location, save_on_each_node=save_on_each_node)
def load_custom_state(obj, path, index: int = 0):
    load_location = f"{path}/custom_checkpoint_{index}.pkl"
    obj.load_state_dict(torch.load(load_location, map_location="cpu"))
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
