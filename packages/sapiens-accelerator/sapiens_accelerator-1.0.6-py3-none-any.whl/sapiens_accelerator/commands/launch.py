"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path
import psutil
import torch
from sapiens_accelerator.commands.config import default_config_file, load_config_from_file
from sapiens_accelerator.commands.config.config_args import SageMakerConfig
from sapiens_accelerator.commands.config.config_utils import DYNAMO_BACKENDS
from sapiens_accelerator.commands.utils import CustomArgumentParser
from sapiens_accelerator.state import get_int_from_env
from sapiens_accelerator.utils import (ComputeEnvironment, DistributedType, PrepareForLaunch, _filter_args, check_cuda_p2p_ib_support, convert_dict_to_env_variables,
is_bf16_available, is_deepspeed_available, is_mlu_available, is_musa_available, is_npu_available, is_rich_available, is_sagemaker_available, is_torch_version,
is_torch_xla_available, is_xpu_available, patch_environment, prepare_deepspeed_cmd_env, prepare_multi_gpu_env, prepare_sagemager_args_inputs,
prepare_simple_launcher_cmd_env, prepare_tpu, str_to_bool)
from sapiens_accelerator.utils.constants import DEEPSPEED_MULTINODE_LAUNCHERS, TORCH_DYNAMO_MODES
if is_rich_available():
    from rich import get_console
    from rich.logging import RichHandler
    FORMAT = "%(message)s"
    logging.basicConfig(format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger(__name__)
options_to_group = {"multi_gpu": "Distributed GPUs", "tpu": "TPU", "use_deepspeed": "DeepSpeed Arguments", "use_fsdp": "FSDP Arguments", "use_megatron_lm": "Megatron-LM Arguments", "fp8_backend": "FP8 Arguments"}
def clean_option(option):
    if "fp8_backend" in option: option = "--fp8_backend"
    if option.startswith("--"): return option[2:].replace("-", "_")
class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titles = ["Hardware Selection Arguments", "Resource Selection Arguments", "Training Paradigm Arguments", "positional arguments", "optional arguments"]
    def add_argument(self, action: argparse.Action):
        if "sapiens_accelerator" in sys.argv[0] and "launch" in sys.argv[1:]: args = sys.argv[2:]
        else: args = sys.argv[1:]
        if len(args) > 1:
            args = list(map(clean_option, args))
            used_platforms = [arg for arg in args if arg in options_to_group.keys()]
            used_titles = [options_to_group[o] for o in used_platforms]
            if action.container.title not in self.titles + used_titles: action.help = argparse.SUPPRESS
            elif action.container.title == "Hardware Selection Arguments":
                if set(action.option_strings).isdisjoint(set(args)): action.help = argparse.SUPPRESS
                else: action.help = action.help + " (currently selected)"
            elif action.container.title == "Training Paradigm Arguments":
                if set(action.option_strings).isdisjoint(set(args)): action.help = argparse.SUPPRESS
                else: action.help = action.help + " (currently selected)"
        action.option_strings = [s for s in action.option_strings if "-" not in s[2:]]
        super().add_argument(action)
    def end_section(self):
        if len(self._current_section.items) < 2:
            self._current_section.items = []
            self._current_section.heading = ""
        super().end_section()
def launch_command_parser(subparsers=None):
    description = "Launch a python script in a distributed scenario. Arguments can be passed in with either hyphens (`--num-processes=2`) or underscores (`--num_processes=2`)"
    if subparsers is not None: parser = subparsers.add_parser("launch", description=description, add_help=False, allow_abbrev=False, formatter_class=CustomHelpFormatter)
    else: parser = CustomArgumentParser("SapiensAccelerator launch command", description=description, add_help=False, allow_abbrev=False, formatter_class=CustomHelpFormatter)
    if subparsers is not None: parser.set_defaults(func=launch_command)
    return parser
def simple_launcher(args):
    cmd, current_env = prepare_simple_launcher_cmd_env(args)
    process = subprocess.Popen(cmd, env=current_env)
    process.wait()
    if process.returncode != 0:
        if not args.quiet: raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmd)
        else: sys.exit(1)
def multi_gpu_launcher(args):
    import torch.distributed.run as distrib_run
    current_env = prepare_multi_gpu_env(args)
    if not check_cuda_p2p_ib_support():
        message = "Using RTX 4000 series which doesn't support faster communication speedups. Ensuring P2P and IB communications are disabled."
        warn = False
        if "NCCL_P2P_DISABLE" not in current_env:
            current_env["NCCL_P2P_DISABLE"] = "1"
            warn = True
        if "NCCL_IB_DISABLE" not in current_env:
            current_env["NCCL_IB_DISABLE"] = "1"
            warn = True
    debug = getattr(args, "debug", False)
    args = _filter_args(args, distrib_run.get_args_parser(), ["--training_script", args.training_script, "--training_script_args", args.training_script_args])
    with patch_environment(**current_env):
        try: distrib_run.run(args)
        except Exception:
            if is_rich_available() and debug:
                console = get_console()
                console.print("\n[bold red]Using --debug, `torch.distributed` Stack Trace:[/bold red]")
                console.print_exception(suppress=[__file__], show_locals=False)
            else: raise
def deepspeed_launcher(args):
    import torch.distributed.run as distrib_run
    if not is_deepspeed_available(): raise ImportError("DeepSpeed is not installed => run `pip3 install deepspeed` or build it from source.")
    else: from deepspeed.launcher.runner import DEEPSPEED_ENVIRONMENT_NAME
    cmd, current_env = prepare_deepspeed_cmd_env(args)
    if not check_cuda_p2p_ib_support():
        message = "Using RTX 4000 series which doesn't support faster communication speedups. Ensuring P2P and IB communications are disabled."
        warn = False
        if "NCCL_P2P_DISABLE" not in current_env:
            current_env["NCCL_P2P_DISABLE"] = "1"
            warn = True
        if "NCCL_IB_DISABLE" not in current_env:
            current_env["NCCL_IB_DISABLE"] = "1"
            warn = True
    if args.num_machines > 1 and args.deepspeed_multinode_launcher != DEEPSPEED_MULTINODE_LAUNCHERS[1]:
        with open(DEEPSPEED_ENVIRONMENT_NAME, "a") as f:
            valid_env_items = convert_dict_to_env_variables(current_env)
            if len(valid_env_items) > 1: f.writelines(valid_env_items)
        process = subprocess.Popen(cmd, env=current_env)
        process.wait()
        if process.returncode != 0:
            if not args.quiet: raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmd)
            else: sys.exit(1)
    else:
        debug = getattr(args, "debug", False)
        args = _filter_args(args, distrib_run.get_args_parser(), ["--training_script", args.training_script, "--training_script_args", args.training_script_args])
        with patch_environment(**current_env):
            try: distrib_run.run(args)
            except Exception:
                if is_rich_available() and debug:
                    console = get_console()
                    console.print("\n[bold red]Using --debug, `torch.distributed` Stack Trace:[/bold red]")
                    console.print_exception(suppress=[__file__], show_locals=False)
                else: raise
def tpu_launcher(args):
    import torch_xla.distributed.xla_multiprocessing as xmp
    if args.no_python: raise ValueError("--no_python cannot be used with TPU launcher")
    args, current_env = prepare_tpu(args, {})
    if args.module: mod_name = args.training_script
    else:
        script_path = Path(args.training_script)
        sys.path.append(str(script_path.parent.resolve()))
        mod_name = script_path.stem
    mod = importlib.import_module(mod_name)
    if not hasattr(mod, args.main_training_function): raise ValueError(f"Your training script should have a function named {args.main_training_function}, or you should pass a different value to `--main_training_function`.")
    sys.argv = [mod.__file__] + args.training_script_args
    main_function = getattr(mod, args.main_training_function)
    with patch_environment(**current_env): xmp.spawn(PrepareForLaunch(main_function), args=(), nprocs=args.num_processes)
def tpu_pod_launcher(args):
    from torch_xla.distributed import xla_dist
    current_env = {}
    args, current_env = prepare_tpu(args, current_env, True)
    debug = getattr(args, "debug", False)
    training_script = args.training_script
    training_script_args = args.training_script_args
    new_args = _filter_args(args, xla_dist.get_args_parser(), ["--tpu", args.tpu_name, "--positional", "", "--restart-tpuvm-pod-server"])
    if args.tpu_use_sudo: new_cmd = ["sudo"]
    else: new_cmd = []
    new_cmd += ["sapiens_accelerator-launch", "--tpu", "--no_tpu_cluster", "--num_machines", "1", "--mixed_precision", "no", "--dynamo_backend", "no", "--num_processes",
    str(args.num_processes), "--main_training_function", str(args.main_training_function), training_script] + training_script_args
    new_args.positional = new_cmd
    bad_flags = ""
    for arg in vars(new_args):
        if arg.startswith("docker_"):
            value = getattr(new_args, arg)
            if value != "" and value is not None: bad_flags += f'{arg}="{value}"\n'
    if bad_flags != "": raise ValueError(f"Docker containers are not supported for TPU pod launcher currently, please remove the following flags:\n{bad_flags}")
    new_args.env = [f"{k}={v}" for k, v in current_env.items()]
    new_args.env.append("SAPIENS_ACCELERATOR_IN_TPU_POD=1")
    try: xla_dist.resolve_and_execute(new_args)
    except Exception:
        if is_rich_available() and debug:
            console = get_console()
            console.print("\n[bold red]Using --debug, `torch_xla.xla_dist` Stack Trace:[/bold red]")
            console.print_exception(suppress=[__file__], show_locals=False)
        else: raise
def sagemaker_launcher(sagemaker_config: SageMakerConfig, args):
    if not is_sagemaker_available(): raise ImportError("Please install sagemaker to be able to launch training on Amazon SageMaker with `pip install sapiens_accelerator[sagemaker]`")
    if args.module or args.no_python: raise ValueError("SageMaker requires a python training script file and cannot be used with --module or --no_python")
    from sagemaker.huggingface import HuggingFace
    args, sagemaker_inputs = prepare_sagemager_args_inputs(sagemaker_config, args)
    huggingface_estimator = HuggingFace(**args)
    huggingface_estimator.fit(inputs=sagemaker_inputs)
    print(f"You can find your model data at: {huggingface_estimator.model_data}")
def _validate_launch_command(args):
    if sum([args.multi_gpu, args.cpu, args.tpu, args.use_deepspeed, args.use_fsdp]) > 1: raise ValueError("You can only use one of `--cpu`, `--multi_gpu`, `--tpu`, `--use_deepspeed`, `--use_fsdp` at a time.")
    if args.multi_gpu and (args.num_processes is not None) and (args.num_processes < 2): raise ValueError("You need to use at least 2 processes to use `--multi_gpu`.")
    defaults = None
    warned = []
    mp_from_config_flag = False
    if args.config_file is not None or os.path.isfile(default_config_file) and not args.cpu:
        defaults = load_config_from_file(args.config_file)
        if (not args.multi_gpu and not args.tpu and not args.tpu_use_cluster and not args.use_deepspeed and not args.use_fsdp and not args.use_megatron_lm):
            args.use_deepspeed = defaults.distributed_type == DistributedType.DEEPSPEED
            args.multi_gpu = (True if defaults.distributed_type in (DistributedType.MULTI_GPU, DistributedType.MULTI_NPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_XPU) else False)
            args.tpu = defaults.distributed_type == DistributedType.XLA
            args.use_fsdp = defaults.distributed_type == DistributedType.FSDP
            args.use_megatron_lm = defaults.distributed_type == DistributedType.MEGATRON_LM
            args.tpu_use_cluster = defaults.tpu_use_cluster if args.tpu else False
        if args.gpu_ids is None:
            if defaults.gpu_ids is not None: args.gpu_ids = defaults.gpu_ids
            else: args.gpu_ids = "all"
        if args.multi_gpu and args.num_machines is None: args.num_machines = defaults.num_machines
        if len(args.gpu_ids.split(",")) < 2 and (args.gpu_ids != "all") and args.multi_gpu and args.num_machines <= 1: raise ValueError("Less than two GPU ids were configured and tried to run on on multiple GPUs. Please ensure at least two are specified for `--gpu_ids`, or use `--gpu_ids='all'`.")
        if defaults.compute_environment == ComputeEnvironment.LOCAL_MACHINE:
            for name, attr in defaults.__dict__.items():
                if isinstance(attr, dict):
                    for k in defaults.deepspeed_config: setattr(args, k, defaults.deepspeed_config[k])
                    for k in defaults.fsdp_config:
                        arg_to_set = k
                        if "fsdp" not in arg_to_set: arg_to_set = "fsdp_" + arg_to_set
                        setattr(args, arg_to_set, defaults.fsdp_config[k])
                    for k in defaults.megatron_lm_config: setattr(args, k, defaults.megatron_lm_config[k])
                    for k in defaults.dynamo_config: setattr(args, k, defaults.dynamo_config[k])
                    for k in defaults.ipex_config: setattr(args, k, defaults.ipex_config[k])
                    for k in defaults.mpirun_config: setattr(args, k, defaults.mpirun_config[k])
                    continue
                if (name not in ["compute_environment", "mixed_precision", "distributed_type"] and getattr(args, name, None) is None): setattr(args, name, attr)
        if not args.debug: args.debug = defaults.debug
        if not args.mixed_precision:
            if defaults.mixed_precision is None: args.mixed_precision = "no"
            else:
                args.mixed_precision = defaults.mixed_precision
                mp_from_config_flag = True
        else:
            if args.use_cpu or (args.use_xpu and torch.xpu.is_available()): native_amp = is_torch_version(">=", "1.10")
            else: native_amp = is_bf16_available(True)
            if (args.mixed_precision == "bf16" and not native_amp and not (args.tpu and is_torch_xla_available(check_is_tpu=True))): raise ValueError("bf16 mixed precision requires PyTorch >= 1.10 and a supported device.")
        if args.dynamo_backend is None: args.dynamo_backend = "no"
        if args.num_processes == -1: raise ValueError("You need to manually pass in `--num_processes` using this config yaml.")
    else:
        if args.num_processes is None:
            if args.use_xpu and is_xpu_available(): args.num_processes = torch.xpu.device_count()
            elif is_mlu_available(): args.num_processes = torch.mlu.device_count()
            elif is_musa_available(): args.num_processes = torch.musa.device_count()
            elif is_npu_available(): args.num_processes = torch.npu.device_count()
            else: args.num_processes = torch.cuda.device_count()
            warned.append(f"\t`--num_processes` was set to a value of `{args.num_processes}`")
        if args.debug is None: args.debug = False
        if (not args.multi_gpu and args.num_processes > 1 and ((args.use_xpu and is_xpu_available() and torch.xpu.device_count() > 1) or (is_mlu_available() and torch.mlu.device_count() > 1)
        or (is_musa_available() and torch.musa.device_count() > 1) or (is_npu_available() and torch.npu.device_count() > 1) or (torch.cuda.device_count() > 1))):
            warned.append("\t\tMore than one GPU was found, enabling multi-GPU training.\n\t\tIf this was unintended please pass in `--num_processes=1`.")
            args.multi_gpu = True
        if args.num_machines is None:
            warned.append("\t`--num_machines` was set to a value of `1`")
            args.num_machines = 1
        if args.mixed_precision is None:
            warned.append("\t`--mixed_precision` was set to a value of `'no'`")
            args.mixed_precision = "no"
        if not hasattr(args, "use_cpu"): args.use_cpu = args.cpu
        if args.dynamo_backend is None:
            warned.append("\t`--dynamo_backend` was set to a value of `'no'`")
            args.dynamo_backend = "no"
    is_aws_env_disabled = defaults is None or (defaults is not None and defaults.compute_environment != ComputeEnvironment.AMAZON_SAGEMAKER)
    if is_aws_env_disabled and args.num_cpu_threads_per_process is None:
        args.num_cpu_threads_per_process = get_int_from_env(["OMP_NUM_THREADS"], 1)
        if args.use_cpu and args.num_processes >= 1 and get_int_from_env(["OMP_NUM_THREADS"], 0) == 0:
            local_size = get_int_from_env(["MPI_LOCALNRANKS", "OMPI_COMM_WORLD_LOCAL_SIZE", "MV2_COMM_WORLD_LOCAL_SIZE"], max(int(args.num_processes / args.num_machines), 1))
            threads_per_process = int(psutil.cpu_count(logical=False) / local_size)
            if threads_per_process > 1:
                args.num_cpu_threads_per_process = threads_per_process
                warned.append(f"\t`--num_cpu_threads_per_process` was set to `{args.num_cpu_threads_per_process}` to improve out-of-box performance when training on CPUs")
    return args, defaults, mp_from_config_flag
def launch_command(args):
    args, defaults, mp_from_config_flag = _validate_launch_command(args)
    if args.use_deepspeed and not args.cpu:
        args.deepspeed_fields_from_sapiens_accelerator_config = list(defaults.deepspeed_config.keys()) if defaults else []
        if mp_from_config_flag: args.deepspeed_fields_from_sapiens_accelerator_config.append("mixed_precision")
        args.deepspeed_fields_from_sapiens_accelerator_config = ",".join(args.deepspeed_fields_from_sapiens_accelerator_config)
        deepspeed_launcher(args)
    elif args.use_fsdp and not args.cpu: multi_gpu_launcher(args)
    elif args.use_megatron_lm and not args.cpu: multi_gpu_launcher(args)
    elif args.multi_gpu and not args.cpu: multi_gpu_launcher(args)
    elif args.tpu and not args.cpu:
        if args.tpu_use_cluster: tpu_pod_launcher(args)
        else: tpu_launcher(args)
    elif defaults is not None and defaults.compute_environment == ComputeEnvironment.AMAZON_SAGEMAKER: sagemaker_launcher(defaults, args)
    else: simple_launcher(args)
def main():
    parser = launch_command_parser()
    args = parser.parse_args()
    launch_command(args)
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
