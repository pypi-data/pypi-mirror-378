"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import importlib
import importlib.metadata
import os
import warnings
from functools import lru_cache, wraps
import torch
from packaging import version
from packaging.version import parse
from .environment import parse_flag_from_env, str_to_bool
from .versions import compare_versions, is_torch_version
USE_TORCH_XLA = parse_flag_from_env("USE_TORCH_XLA", default=True)
_torch_xla_available = False
if USE_TORCH_XLA:
    try:
        import torch_xla.core.xla_model as xm
        import torch_xla.runtime
        _torch_xla_available = True
    except ImportError: pass
_tpu_available = _torch_xla_available
_torch_distributed_available = torch.distributed.is_available()
def _is_package_available(pkg_name, metadata_name=None):
    package_exists = importlib.util.find_spec(pkg_name) is not None
    if package_exists:
        try:
            _ = importlib.metadata.metadata(pkg_name if metadata_name is None else metadata_name)
            return True
        except importlib.metadata.PackageNotFoundError: return False
def is_torch_distributed_available() -> bool: return _torch_distributed_available
def is_ccl_available():
    try: pass
    except ImportError: pass
    return (importlib.util.find_spec("torch_ccl") is not None or importlib.util.find_spec("oneccl_bindings_for_pytorch") is not None)
def get_ccl_version(): return importlib.metadata.version("oneccl_bind_pt")
def is_import_timer_available(): return _is_package_available("import_timer")
def is_pynvml_available(): return _is_package_available("pynvml") or _is_package_available("pynvml", "nvidia-ml-py")
def is_pytest_available(): return _is_package_available("pytest")
def is_msamp_available(): return _is_package_available("msamp", "ms-amp")
def is_schedulefree_available(): return _is_package_available("schedulefree")
def is_transformer_engine_available(): return _is_package_available("transformer_engine", "transformer-engine")
def is_lomo_available(): return _is_package_available("lomo_optim")
def is_fp8_available(): return is_msamp_available() or is_transformer_engine_available()
def is_cuda_available():
    pytorch_nvml_based_cuda_check_previous_value = os.environ.get("PYTORCH_NVML_BASED_CUDA_CHECK")
    try:
        os.environ["PYTORCH_NVML_BASED_CUDA_CHECK"] = str(1)
        available = torch.cuda.is_available()
    finally:
        if pytorch_nvml_based_cuda_check_previous_value: os.environ["PYTORCH_NVML_BASED_CUDA_CHECK"] = pytorch_nvml_based_cuda_check_previous_value
        else: os.environ.pop("PYTORCH_NVML_BASED_CUDA_CHECK", None)
    return available
@lru_cache
def is_torch_xla_available(check_is_tpu=False, check_is_gpu=False):
    assert not (check_is_tpu and check_is_gpu), "The check_is_tpu and check_is_gpu cannot both be true."
    if not _torch_xla_available: return False
    elif check_is_gpu: return torch_xla.runtime.device_type() in ["GPU", "CUDA"]
    elif check_is_tpu: return torch_xla.runtime.device_type() == "TPU"
    return True
def is_deepspeed_available():
    if is_mlu_available(): return _is_package_available("deepspeed", metadata_name="deepspeed-mlu")
    return _is_package_available("deepspeed")
def is_pippy_available(): return is_torch_version(">=", "2.4.0")
def is_bf16_available(ignore_tpu=False):
    if is_torch_xla_available(check_is_tpu=True): return not ignore_tpu
    if is_cuda_available(): return torch.cuda.is_bf16_supported()
    if is_mps_available(): return False
    return True
def is_4bit_sapiens_available():
    package_exists = _is_package_available("sapiens_machine")
    if package_exists:
        sapiens_version = version.parse(importlib.metadata.version("sapiens_machine"))
        return compare_versions(sapiens_version, ">=", "0.39.0")
    return False
def is_8bit_sapiens_available():
    package_exists = _is_package_available("sapiens_machine")
    if package_exists:
        sapiens_version = version.parse(importlib.metadata.version("sapiens_machine"))
        return compare_versions(sapiens_version, ">=", "0.37.2")
    return False
def is_sapiens_available(): return _is_package_available("sapiens_machine")
def is_sapiens_machine_multi_backend_available():
    if not is_sapiens_available(): return False
    import sapiens_machine as sapiens
    return "multi_backend" in getattr(sapiens, "features", set())
def is_torchvision_available(): return _is_package_available("torchvision")
def is_megatron_lm_available():
    if str_to_bool(os.environ.get("SAPIENS_ACCELERATOR_USE_MEGATRON_LM", "False")) == 1:
        if importlib.util.find_spec("megatron") is not None:
            try:
                megatron_version = parse(importlib.metadata.version("megatron-core"))
                if compare_versions(megatron_version, "==", "0.5.0"): return importlib.util.find_spec(".data", "megatron")
            except Exception as e: return False
def is_transformers_available(): return _is_package_available("transformers")
def is_datasets_available(): return _is_package_available("datasets")
def is_peft_available(): return _is_package_available("peft")
def is_timm_available(): return _is_package_available("timm")
def is_triton_available(): return _is_package_available("triton")
def is_aim_available():
    package_exists = _is_package_available("aim")
    if package_exists:
        aim_version = version.parse(importlib.metadata.version("aim"))
        return compare_versions(aim_version, "<", "4.0.0")
    return False
def is_tensorboard_available(): return _is_package_available("tensorboard") or _is_package_available("tensorboardX")
def is_wandb_available(): return _is_package_available("wandb")
def is_comet_ml_available(): return _is_package_available("comet_ml")
def is_boto3_available(): return _is_package_available("boto3")
def is_rich_available():
    if _is_package_available("rich"): return parse_flag_from_env("SAPIENS_ACCELERATOR_ENABLE_RICH", False)
    return False
def is_sagemaker_available(): return _is_package_available("sagemaker")
def is_tqdm_available(): return _is_package_available("tqdm")
def is_clearml_available(): return _is_package_available("clearml")
def is_pandas_available(): return _is_package_available("pandas")
def is_mlflow_available():
    if _is_package_available("mlflow"): return True
    if importlib.util.find_spec("mlflow") is not None:
        try:
            _ = importlib.metadata.metadata("mlflow-skinny")
            return True
        except importlib.metadata.PackageNotFoundError: return False
    return False
def is_mps_available(min_version="1.12"): return is_torch_version(">=", min_version) and torch.backends.mps.is_available() and torch.backends.mps.is_built()
def is_ipex_available():
    def get_major_and_minor_from_version(full_version): return str(version.parse(full_version).major) + "." + str(version.parse(full_version).minor)
    _torch_version = importlib.metadata.version("torch")
    if importlib.util.find_spec("intel_extension_for_pytorch") is None: return False
    _ipex_version = "N/A"
    try: _ipex_version = importlib.metadata.version("intel_extension_for_pytorch")
    except importlib.metadata.PackageNotFoundError: return False
    torch_major_and_minor = get_major_and_minor_from_version(_torch_version)
    ipex_major_and_minor = get_major_and_minor_from_version(_ipex_version)
    if torch_major_and_minor != ipex_major_and_minor: return False
    return True
@lru_cache
def is_mlu_available(check_device=False):
    if importlib.util.find_spec("torch_mlu") is None: return False
    import torch_mlu
    if check_device:
        try:
            _ = torch.mlu.device_count()
            return torch.mlu.is_available()
        except RuntimeError: return False
    return hasattr(torch, "mlu") and torch.mlu.is_available()
@lru_cache
def is_musa_available(check_device=False):
    if importlib.util.find_spec("torch_musa") is None: return False
    import torch_musa
    if check_device:
        try:
            _ = torch.musa.device_count()
            return torch.musa.is_available()
        except RuntimeError: return False
    return hasattr(torch, "musa") and torch.musa.is_available()
@lru_cache
def is_npu_available(check_device=False):
    if importlib.util.find_spec("torch_npu") is None: return False
    import torch_npu
    if check_device:
        try:
            _ = torch.npu.device_count()
            return torch.npu.is_available()
        except RuntimeError: return False
    return hasattr(torch, "npu") and torch.npu.is_available()
@lru_cache
def is_xpu_available(check_device=False):
    if not parse_flag_from_env("SAPIENS_ACCELERATOR_USE_XPU", default=True): return False
    if is_ipex_available():
        if is_torch_version("<=", "1.12"): return False
        import intel_extension_for_pytorch
    else:
        if is_torch_version("<=", "2.3"): return False
    if check_device:
        try:
            _ = torch.xpu.device_count()
            return torch.xpu.is_available()
        except RuntimeError: return False
    return hasattr(torch, "xpu") and torch.xpu.is_available()
def is_dvclive_available(): return _is_package_available("dvclive")
def is_torchdata_available(): return _is_package_available("torchdata")
def is_torchdata_stateful_dataloader_available():
    package_exists = _is_package_available("torchdata")
    if package_exists:
        torchdata_version = version.parse(importlib.metadata.version("torchdata"))
        return compare_versions(torchdata_version, ">=", "0.8.0")
    return False
def deepspeed_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from sapiens_accelerator.state import AcceleratorState
        from sapiens_accelerator.utils.dataclasses import DistributedType
        if AcceleratorState._shared_state != {} and AcceleratorState().distributed_type != DistributedType.DEEPSPEED: raise ValueError("DeepSpeed is not enabled, please make sure that an `Accelerator` is configured for `deepspeed` before calling this function.")
        return func(*args, **kwargs)
    return wrapper
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
