"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
import os
import platform
import subprocess
import numpy as np
import psutil
import torch
from sapiens_accelerator import __version__ as version
from sapiens_accelerator.commands.config import default_config_file, load_config_from_file
from ..utils import is_mlu_available, is_musa_available, is_npu_available, is_xpu_available
def env_command_parser(subparsers=None):
    if subparsers is not None: parser = subparsers.add_parser("env")
    else: parser = argparse.ArgumentParser("SapiensAccelerator env command")
    parser.add_argument("--config_file", default=None, help="The config file to use for the default values in the launching script.")
    if subparsers is not None: parser.set_defaults(func=env_command)
    return parser
def env_command(args):
    pt_version = torch.__version__
    pt_cuda_available = torch.cuda.is_available()
    pt_xpu_available = is_xpu_available()
    pt_mlu_available = is_mlu_available()
    pt_musa_available = is_musa_available()
    pt_npu_available = is_npu_available()
    sapiens_accelerator_config = "Not found"
    if args.config_file is not None or os.path.isfile(default_config_file): sapiens_accelerator_config = load_config_from_file(args.config_file).to_dict()
    command = None
    bash_location = "Not found"
    if os.name == "nt": command = ["where", "sapiens_accelerator"]
    elif os.name == "posix": command = ["which", "sapiens_accelerator"]
    if command is not None: bash_location = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    info = {"`SapiensAccelerator` version": version, "Platform": platform.platform(), "`sapiens_accelerator` bash location": bash_location, "Python version": platform.python_version(),
    "Numpy version": np.__version__, "PyTorch version (GPU?)": f"{pt_version} ({pt_cuda_available})", "PyTorch XPU available": str(pt_xpu_available),
    "PyTorch NPU available": str(pt_npu_available), "PyTorch MLU available": str(pt_mlu_available), "PyTorch MUSA available": str(pt_musa_available),
    "System RAM": f"{psutil.virtual_memory().total / 1024 ** 3:.2f} GB"}
    if pt_cuda_available: info["GPU type"] = torch.cuda.get_device_name()
    if pt_mlu_available: info["MLU type"] = torch.mlu.get_device_name()
    if pt_npu_available: info["CANN version"] = torch.version.cann
    sapiens_accelerator_config_str = ("\n".join([f"\t- {prop}: {val}" for prop, val in sapiens_accelerator_config.items()]) if isinstance(sapiens_accelerator_config, dict) else f"\t{sapiens_accelerator_config}")
    info["`SapiensAccelerator` configs"] = sapiens_accelerator_config
    return info
def main() -> int:
    parser = env_command_parser()
    args = parser.parse_args()
    env_command(args)
    return 0
if __name__ == "__main__": raise SystemExit(main())
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
