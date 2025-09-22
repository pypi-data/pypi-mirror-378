"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import os
import sys
import tempfile
import torch
from .state import AcceleratorState, PartialState
from .utils import (PrecisionType, PrepareForLaunch, are_libraries_initialized, check_cuda_p2p_ib_support, get_gpu_info, is_mps_available, is_torch_version, patch_environment)
from .utils.constants import ELASTIC_LOG_LINE_PREFIX_TEMPLATE_PYTORCH_VERSION
def test_launch(): _ = PartialState()
def notebook_launcher(function, args=(), num_processes=None, mixed_precision="no", use_port="29500", master_addr="127.0.0.1", node_rank=0, num_nodes=1,
rdzv_backend="static", rdzv_endpoint="", rdzv_conf=None, rdzv_id="none", max_restarts=0, monitor_interval=0.1, log_line_prefix_template=None):
    in_colab = False
    in_kaggle = False
    if any(key.startswith("KAGGLE") for key in os.environ.keys()): in_kaggle = True
    elif "IPython" in sys.modules: in_colab = "google.colab" in str(sys.modules["IPython"].get_ipython())
    try: mixed_precision = PrecisionType(mixed_precision.lower())
    except ValueError: raise ValueError(f"Unknown mixed_precision mode: {args.mixed_precision.lower()}. Choose between {PrecisionType.list()}.")
    if (in_colab or in_kaggle) and (os.environ.get("TPU_NAME", None) is not None):
        import torch_xla.distributed.xla_multiprocessing as xmp
        if len(AcceleratorState._shared_state) > 0: raise ValueError("To train on TPU in Colab or Kaggle Kernel, the `Accelerator` should only be initialized inside your training function. Restart your notebook and make sure no cells initializes an `Accelerator`.")
        if num_processes is None: num_processes = 8
        launcher = PrepareForLaunch(function, distributed_type="XLA")
        xmp.spawn(launcher, args=args, nprocs=num_processes, start_method="fork")
    elif in_colab and get_gpu_info()[1] < 2: function(*args)
    else:
        if num_processes is None: raise ValueError("You have to specify the number of GPUs you would like to use, add `num_processes=...` to your call.")
        if node_rank >= num_nodes: raise ValueError("The node_rank must be less than the number of nodes.")
        if num_processes > 1:
            from torch.distributed.launcher.api import LaunchConfig, elastic_launch
            from torch.multiprocessing import start_processes
            from torch.multiprocessing.spawn import ProcessRaisedException
            if len(AcceleratorState._shared_state) > 0: raise ValueError("To launch a multi-GPU training from your notebook, the `Accelerator` should only be initialized inside your training function. Restart your notebook and make sure no cells initializes an `Accelerator`.")
            problematic_imports = are_libraries_initialized("sapiens_machine")
            if len(problematic_imports) > 0:
                err = ("Could not start distributed process. Libraries known to initialize CUDA upon import have been imported already. Please keep these imports inside your training function to try and help with this:")
                for lib_name in problematic_imports: err += f"\n\t* `{lib_name}`"
                raise RuntimeError(err)
            patched_env = dict(nproc=num_processes, node_rank=node_rank, world_size=num_nodes * num_processes, master_addr=master_addr, master_port=use_port, mixed_precision=mixed_precision)
            if not check_cuda_p2p_ib_support():
                patched_env["nccl_p2p_disable"] = "1"
                patched_env["nccl_ib_disable"] = "1"
            with patch_environment(**patched_env):
                if os.environ.get("SAPIENS_ACCELERATOR_DEBUG_MODE", "false").lower() == "true":
                    launcher = PrepareForLaunch(test_launch, distributed_type="MULTI_GPU")
                    try: start_processes(launcher, args=(), nprocs=num_processes, start_method="fork")
                    except ProcessRaisedException as e:
                        err = "An issue was found when verifying a stable environment for the notebook launcher."
                        if "Cannot re-initialize CUDA in forked subprocess" in e.args[0]: raise RuntimeError(f"{err} This likely stems from an outside import causing issues once the `notebook_launcher()` is called. Please review your imports and test them when running the `notebook_launcher()` to identify which one is problematic and causing CUDA to be initialized.") from e
                        else: raise RuntimeError(f"{err} The following error was raised: {e}") from e
                launcher = PrepareForLaunch(function, distributed_type="MULTI_GPU")
                try:
                    if rdzv_conf is None: rdzv_conf = {}
                    if rdzv_backend == "static":
                        rdzv_conf["rank"] = node_rank
                        if not rdzv_endpoint: rdzv_endpoint = f"{master_addr}:{use_port}"
                    launch_config_kwargs = dict(min_nodes=num_nodes, max_nodes=num_nodes, nproc_per_node=num_processes, run_id=rdzv_id, rdzv_endpoint=rdzv_endpoint,
                    rdzv_backend=rdzv_backend, rdzv_configs=rdzv_conf, max_restarts=max_restarts, monitor_interval=monitor_interval, start_method="fork")
                    if is_torch_version(">=", ELASTIC_LOG_LINE_PREFIX_TEMPLATE_PYTORCH_VERSION): launch_config_kwargs["log_line_prefix_template"] = log_line_prefix_template
                    elastic_launch(config=LaunchConfig(**launch_config_kwargs), entrypoint=function)(*args)
                except ProcessRaisedException as e:
                    if "Cannot re-initialize CUDA in forked subprocess" in e.args[0]: raise RuntimeError("CUDA has been initialized before the `notebook_launcher` could create a forked subprocess. This likely stems from an outside import causing issues once the `notebook_launcher()` is called. Please review your imports and test them when running the `notebook_launcher()` to identify which one is problematic and causing CUDA to be initialized.") from e
                    else: raise RuntimeError(f"An issue was found when launching the training: {e}") from e
        else:
            if is_mps_available(): os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            function(*args)
def debug_launcher(function, args=(), num_processes=2):
    from torch.multiprocessing import start_processes
    with tempfile.NamedTemporaryFile() as tmp_file:
        with patch_environment(world_size=num_processes, master_addr="127.0.0.1", master_port="29500", sapiens_accelerator_mixed_precision="no", sapiens_accelerator_debug_rdv_file=tmp_file.name, sapiens_accelerator_use_cpu="yes"):
            launcher = PrepareForLaunch(function, debug=True)
            start_processes(launcher, args=args, nprocs=num_processes, start_method="fork")
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
