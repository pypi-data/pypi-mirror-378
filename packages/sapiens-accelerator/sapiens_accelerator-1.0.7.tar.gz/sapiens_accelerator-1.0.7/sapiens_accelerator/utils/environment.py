"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import logging
import math
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from shutil import which
from typing import List, Optional
import torch
from packaging.version import parse
logger = logging.getLogger(__name__)
def convert_dict_to_env_variables(current_env: dict):
    forbidden_chars = [";", "\n", "<", ">", " "]
    valid_env_items = []
    for key, value in current_env.items():
        if all(char not in (key + value) for char in forbidden_chars) and len(key) >= 1 and len(value) >= 1: valid_env_items.append(f"{key}={value}\n")
    return valid_env_items
def str_to_bool(value) -> int:
    value = value.lower()
    if value in ("y", "yes", "t", "true", "on", "1"): return 1
    elif value in ("n", "no", "f", "false", "off", "0"): return 0
    else: raise ValueError(f"invalid truth value {value}")
def get_int_from_env(env_keys, default):
    for e in env_keys:
        val = int(os.environ.get(e, -1))
        if val >= 0: return val
    return default
def parse_flag_from_env(key, default=False):
    value = os.environ.get(key, str(default))
    return str_to_bool(value) == 1
def parse_choice_from_env(key, default="no"):
    value = os.environ.get(key, str(default))
    return value
def are_libraries_initialized(*library_names: str) -> List[str]: return [lib_name for lib_name in library_names if lib_name in sys.modules.keys()]
def _nvidia_smi():
    if platform.system() == "Windows":
        command = which("nvidia-smi")
        if command is None: command = f"{os.environ['systemdrive']}\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe"
    else: command = "nvidia-smi"
    return command
def get_gpu_info():
    output = subprocess.check_output([_nvidia_smi(), "--query-gpu=count,name", "--format=csv,noheader"], universal_newlines=True)
    output = output.strip()
    gpus = output.split(os.linesep)
    gpu_count = len(gpus)
    gpu_names = [gpu.split(",")[1].strip() for gpu in gpus]
    return gpu_names, gpu_count
def get_driver_version():
    output = subprocess.check_output([_nvidia_smi(), "--query-gpu=driver_version", "--format=csv,noheader"], universal_newlines=True)
    output = output.strip()
    return output.split(os.linesep)[0]
def check_cuda_p2p_ib_support():
    try:
        device_names, device_count = get_gpu_info()
        unsupported_devices = {"RTX 40"}
        if device_count > 1:
            if any(unsupported_device in device_name for device_name in device_names for unsupported_device in unsupported_devices):
                acceptable_driver_version = "550.40.07"
                current_driver_version = get_driver_version()
                if parse(current_driver_version) < parse(acceptable_driver_version): return False
                return True
    except Exception: pass
    return True
def check_fp8_capability():
    cuda_device_capacity = torch.cuda.get_device_capability()
    return cuda_device_capacity >= (8, 9)
@dataclass
class CPUInformation:
    rank: int = field(default=0, metadata={"help": "The rank of the current process."})
    world_size: int = field(default=1, metadata={"help": "The total number of processes in the world."})
    local_rank: int = field(default=0, metadata={"help": "The rank of the current process on the local node."})
    local_world_size: int = field(default=1, metadata={"help": "The total number of processes on the local node."})
def get_cpu_distributed_information() -> CPUInformation:
    information = {}
    information["rank"] = get_int_from_env(["RANK", "PMI_RANK", "OMPI_COMM_WORLD_RANK", "MV2_COMM_WORLD_RANK"], 0)
    information["world_size"] = get_int_from_env(["WORLD_SIZE", "PMI_SIZE", "OMPI_COMM_WORLD_SIZE", "MV2_COMM_WORLD_SIZE"], 1)
    information["local_rank"] = get_int_from_env(["LOCAL_RANK", "MPI_LOCALRANKID", "OMPI_COMM_WORLD_LOCAL_RANK", "MV2_COMM_WORLD_LOCAL_RANK"], 0)
    information["local_world_size"] = get_int_from_env(["LOCAL_WORLD_SIZE", "MPI_LOCALNRANKS", "OMPI_COMM_WORLD_LOCAL_SIZE", "MV2_COMM_WORLD_LOCAL_SIZE"], 1)
    return CPUInformation(**information)
def override_numa_affinity(local_process_index: int, verbose: Optional[bool] = None) -> None:
    if verbose is None: verbose = parse_flag_from_env("SAPIENS_ACCELERATOR_DEBUG_MODE", False)
    if torch.cuda.is_available():
        from sapiens_accelerator.utils import is_pynvml_available
        if not is_pynvml_available(): raise ImportError("To set CPU affinity on CUDA GPUs the `pynvml` package must be available. (`pip install pynvml`)")
        import pynvml as nvml
        nvml.nvmlInit()
        num_elements = math.ceil(os.cpu_count() / 64)
        handle = nvml.nvmlDeviceGetHandleByIndex(local_process_index)
        affinity_string = ""
        for j in nvml.nvmlDeviceGetCpuAffinity(handle, num_elements): affinity_string = f"{j:064b}{affinity_string}"
        affinity_list = [int(x) for x in affinity_string]
        affinity_list.reverse()
        affinity_to_set = [i for i, e in enumerate(affinity_list) if e != 0]
        os.sched_setaffinity(0, affinity_to_set)
        if verbose: cpu_cores = os.sched_getaffinity(0)
@lru_cache
def set_numa_affinity(local_process_index: int, verbose: Optional[bool] = None) -> None: override_numa_affinity(local_process_index=local_process_index, verbose=verbose)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
