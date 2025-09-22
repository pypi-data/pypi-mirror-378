"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import json
import os
from collections.abc import Mapping
from typing import Dict, List, Optional, Union
import numpy as np
import torch
from safetensors import safe_open
def offload_weight(weight, weight_name, offload_folder, index=None):
    dtype = None
    if str(weight.dtype) == "torch.bfloat16":
        weight = weight.view(torch.int16)
        dtype = "bfloat16"
    array = weight.cpu().numpy()
    tensor_file = os.path.join(offload_folder, f"{weight_name}.dat")
    if index is not None:
        if dtype is None: dtype = str(array.dtype)
        index[weight_name] = {"dtype": dtype, "shape": list(array.shape)}
    if array.ndim == 0: array = array[None]
    file_array = np.memmap(tensor_file, dtype=array.dtype, mode="w+", shape=array.shape)
    file_array[:] = array[:]
    file_array.flush()
    return index
def load_offloaded_weight(weight_file, weight_info):
    shape = tuple(weight_info["shape"])
    if shape == (): shape = (1,)
    dtype = weight_info["dtype"]
    if dtype == "bfloat16": dtype = "int16"
    weight = np.memmap(weight_file, dtype=dtype, shape=shape, mode="r")
    if len(weight_info["shape"]) == 0: weight = weight[0]
    weight = torch.tensor(weight)
    if weight_info["dtype"] == "bfloat16": weight = weight.view(torch.bfloat16)
    return weight
def save_offload_index(index, offload_folder):
    if index is None or len(index) == 0: return
    offload_index_file = os.path.join(offload_folder, "index.json")
    if os.path.isfile(offload_index_file):
        with open(offload_index_file, encoding="utf-8") as f: current_index = json.load(f)
    else: current_index = {}
    current_index.update(index)
    with open(offload_index_file, "w", encoding="utf-8") as f: json.dump(current_index, f, indent=2)
def offload_state_dict(save_dir: Union[str, os.PathLike], state_dict: Dict[str, torch.Tensor]):
    os.makedirs(save_dir, exist_ok=True)
    index = {}
    for name, parameter in state_dict.items(): index = offload_weight(parameter, name, save_dir, index=index)
    save_offload_index(index, save_dir)
class PrefixedDataset(Mapping):
    def __init__(self, dataset: Mapping, prefix: str):
        self.dataset = dataset
        self.prefix = prefix
    def __getitem__(self, key): return self.dataset[f"{self.prefix}{key}"]
    def __iter__(self): return iter([key for key in self.dataset if key.startswith(self.prefix)])
    def __len__(self): return len(self.dataset)
class OffloadedWeightsLoader(Mapping):
    def __init__(self, state_dict: Dict[str, torch.Tensor] = None, save_folder: Optional[Union[str, os.PathLike]] = None, index: Mapping = None, device=None):
        if state_dict is None and save_folder is None and index is None: raise ValueError("Need either a `state_dict`, a `save_folder` or an `index` containing offloaded weights.")
        self.state_dict = {} if state_dict is None else state_dict
        self.save_folder = save_folder
        if index is None and save_folder is not None:
            with open(os.path.join(save_folder, "index.json")) as f: index = json.load(f)
        self.index = {} if index is None else index
        self.all_keys = list(self.state_dict.keys())
        self.all_keys.extend([key for key in self.index if key not in self.all_keys])
        self.device = device
    def __getitem__(self, key: str):
        if key in self.state_dict: return self.state_dict[key]
        weight_info = self.index[key]
        if weight_info.get("safetensors_file") is not None:
            device = "cpu" if self.device is None else self.device
            tensor = None
            try:
                with safe_open(weight_info["safetensors_file"], framework="pt", device=device) as f: tensor = f.get_tensor(weight_info.get("weight_name", key))
            except TypeError:
                with safe_open(weight_info["safetensors_file"], framework="pt", device="cpu") as f: tensor = f.get_tensor(weight_info.get("weight_name", key))
            if "dtype" in weight_info: tensor = tensor.to(getattr(torch, weight_info["dtype"]))
            if tensor.device != torch.device(device): tensor = tensor.to(device)
            return tensor
        weight_file = os.path.join(self.save_folder, f"{key}.dat")
        return load_offloaded_weight(weight_file, weight_info)
    def __iter__(self): return iter(self.all_keys)
    def __len__(self): return len(self.all_keys)
def extract_submodules_state_dict(state_dict: Dict[str, torch.Tensor], submodule_names: List[str]):
    result = {}
    for module_name in submodule_names: result.update({key: param for key, param in state_dict.items() if key == module_name or key.startswith(module_name + ".")})
    return result
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
