"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from pathlib import Path
import torch
from ...utils import is_mlu_available, is_musa_available, is_npu_available, is_xpu_available
from .config_args import ClusterConfig, default_json_config_file
from .config_utils import SubcommandHelpFormatter
description = "Create a default config file for SapiensAccelerator with only a few flags set."
def write_basic_config(mixed_precision="no", save_location: str = default_json_config_file, use_xpu: bool = False):
    path = Path(save_location)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): return False
    mixed_precision = mixed_precision.lower()
    if mixed_precision not in ["no", "fp16", "bf16", "fp8"]: raise ValueError(f"`mixed_precision` should be one of 'no', 'fp16', 'bf16', or 'fp8'. Received {mixed_precision}")
    config = {"compute_environment": "LOCAL_MACHINE", "mixed_precision": mixed_precision}
    if is_mlu_available():
        num_mlus = torch.mlu.device_count()
        config["num_processes"] = num_mlus
        config["use_cpu"] = False
        if num_mlus > 1: config["distributed_type"] = "MULTI_MLU"
        else: config["distributed_type"] = "NO"
    elif is_musa_available():
        num_musas = torch.musa.device_count()
        config["num_processes"] = num_musas
        config["use_cpu"] = False
        if num_musas > 1: config["distributed_type"] = "MULTI_MUSA"
        else: config["distributed_type"] = "NO"
    elif torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        config["num_processes"] = num_gpus
        config["use_cpu"] = False
        if num_gpus > 1: config["distributed_type"] = "MULTI_GPU"
        else: config["distributed_type"] = "NO"
    elif is_xpu_available() and use_xpu:
        num_xpus = torch.xpu.device_count()
        config["num_processes"] = num_xpus
        config["use_cpu"] = False
        if num_xpus > 1: config["distributed_type"] = "MULTI_XPU"
        else: config["distributed_type"] = "NO"
    elif is_npu_available():
        num_npus = torch.npu.device_count()
        config["num_processes"] = num_npus
        config["use_cpu"] = False
        if num_npus > 1: config["distributed_type"] = "MULTI_NPU"
        else: config["distributed_type"] = "NO"
    else:
        num_xpus = 0
        config["use_cpu"] = True
        config["num_processes"] = 1
        config["distributed_type"] = "NO"
    config["debug"] = False
    config["enable_cpu_affinity"] = False
    config = ClusterConfig(**config)
    config.to_json_file(path)
    return path
def default_command_parser(parser, parents):
    parser = parser.add_parser("default", parents=parents, help=description, formatter_class=SubcommandHelpFormatter)
    parser.add_argument("--config_file", default=default_json_config_file, help=("The path to use to store the config file. Will default to a file named default_config.yaml in the cache location, which is the content of the environment `HF_HOME` suffixed with 'sapiens_accelerator', or if you don't have such an environment variable, your cache directory ('~/.cache' or the content of `XDG_CACHE_HOME`) suffixed with 'huggingface'."), dest="save_location")
    parser.add_argument("--mixed_precision", choices=["no", "fp16", "bf16"], type=str, help="Whether or not to use mixed precision training. Choose between FP16 and BF16 (bfloat16) training. BF16 training is only supported on Nvidia Ampere GPUs and PyTorch 1.10 or later.", default="no")
    parser.set_defaults(func=default_config_command)
    return parser
def default_config_command(args): pass
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
