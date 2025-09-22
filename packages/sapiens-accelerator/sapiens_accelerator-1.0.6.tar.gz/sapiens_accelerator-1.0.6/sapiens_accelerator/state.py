"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from __future__ import annotations
import logging
import os
import threading
import warnings
from contextlib import contextmanager
from functools import partial
from typing import Any, Callable, Optional
import torch
from .utils import (DistributedType, DynamoBackend, GradientAccumulationPlugin, check_cuda_p2p_ib_support, check_fp8_capability, deepspeed_required,
get_ccl_version, get_cpu_distributed_information, get_int_from_env, is_ccl_available, is_datasets_available, is_deepspeed_available, is_fp8_available,
is_ipex_available, is_mlu_available, is_mps_available, is_musa_available, is_npu_available, is_torch_xla_available, is_xpu_available, parse_choice_from_env,
parse_flag_from_env, set_numa_affinity)
from .utils.dataclasses import SageMakerDistributedType
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
if is_mlu_available(check_device=False): import torch_mlu
if is_musa_available(check_device=False): import torch_musa
if is_npu_available(check_device=False): import torch_npu
logger = logging.getLogger(__name__)
def is_initialized() -> bool: return AcceleratorState._shared_state != {}
def do_nothing(*args, **kwargs): return None
class ThreadLocalSharedDict(threading.local):
    def __init__(self, thread_local: bool = False): self._storage = {}
    def __get__(self, obj, objtype=None): return self._storage
    def __set__(self, obj, value): self._storage = value
SharedDict = dict if not is_torch_xla_available() else ThreadLocalSharedDict
class PartialState:
    _shared_state = SharedDict()
    _known_attrs = ["_cpu", "_mixed_precision", "_shared_state", "backend", "debug", "device", "distributed_type", "fork_launched", "local_process_index", "num_processes", "process_index"]
    def __init__(self, cpu: bool = False, **kwargs):
        self.__dict__ = self._shared_state
        if not self.initialized:
            self._cpu = cpu
            self.backend = None
            env_device = os.environ.get("SAPIENS_ACCELERATOR_TORCH_DEVICE", None)
            self.device = torch.device(env_device) if env_device is not None else None
            self.debug = parse_flag_from_env("SAPIENS_ACCELERATOR_DEBUG_MODE")
            use_sagemaker_dp = kwargs.pop("_use_sagemaker_dp", None)
            dist_information = None
            if use_sagemaker_dp is None: use_sagemaker_dp = (os.environ.get("SAPIENS_ACCELERATOR_USE_SAGEMAKER", "false") == "true" and os.environ.get("SAPIENS_ACCELERATOR_SAGEMAKER_DISTRIBUTED_TYPE") != SageMakerDistributedType.NO)
            original_backend = kwargs.pop("backend", None)
            backend, distributed_type = self._prepare_backend(cpu, use_sagemaker_dp, original_backend)
            if original_backend is not None and backend != original_backend: raise ValueError(f"Your assigned backend {original_backend} is not avaliable, please use {backend}")
            self.backend = backend
            self.distributed_type = distributed_type
            use_deepspeed = False
            if not cpu and self.backend != "xla":
                if int(os.environ.get("LOCAL_RANK", -1)) != -1:
                    if os.environ.get("SAPIENS_ACCELERATOR_USE_DEEPSPEED", "false") == "true":
                        if not is_deepspeed_available(): raise ImportError("DeepSpeed is not available => install it using `pip3 install deepspeed` or build it from source")
                        from deepspeed import comm as dist
                        if not dist.is_initialized(): dist.init_distributed(dist_backend=self.backend, auto_mpi_discovery=False, **kwargs)
                        use_deepspeed = True
                    elif (self.distributed_type not in (DistributedType.MULTI_XPU, DistributedType.MULTI_CPU) and not torch.distributed.is_initialized()): torch.distributed.init_process_group(backend=self.backend, **kwargs)
            if self.distributed_type in (DistributedType.MULTI_XPU, DistributedType.MULTI_CPU):
                dist_information = get_cpu_distributed_information()
                os.environ["RANK"] = str(dist_information.rank)
                os.environ["WORLD_SIZE"] = str(dist_information.world_size)
                os.environ["LOCAL_RANK"] = str(dist_information.local_rank)
                os.environ["LOCAL_WORLD_SIZE"] = str(dist_information.local_world_size)
                if not os.environ.get("MASTER_PORT", None): os.environ["MASTER_PORT"] = "29500"
                if (not os.environ.get("MASTER_ADDR", None) and dist_information.local_world_size != dist_information.world_size and self.backend != "mpi"): raise ValueError("Tried to launch on distributed with multinode, but `MASTER_ADDR` env was not set, please try exporting rank 0's hostname as `MASTER_ADDR`")
                kwargs["rank"] = dist_information.rank
                kwargs["world_size"] = dist_information.world_size
                if (self.distributed_type == DistributedType.MULTI_CPU and get_int_from_env(["OMP_NUM_THREADS"], 0) == 0):
                    import psutil
                    num_cpu_threads_per_process = int(psutil.cpu_count(logical=False) / dist_information.local_world_size)
                    if num_cpu_threads_per_process == 0: num_cpu_threads_per_process = 1
                    torch.set_num_threads(num_cpu_threads_per_process)
                if not torch.distributed.is_initialized(): torch.distributed.init_process_group(backend=self.backend, **kwargs)
            if self.backend is None:
                self.distributed_type = DistributedType.NO
                self.num_processes = 1
                self.process_index = 0
                self.local_process_index = 0
            elif self.backend == "xla":
                self.set_device()
                xm.set_replication(self.device, xm.get_xla_supported_devices())
                self.num_processes = xm.xrt_world_size()
                self.process_index = xm.get_ordinal()
                if is_torch_xla_available(check_is_tpu=True): self.local_process_index = xm.get_local_ordinal()
                else: self.local_process_index = int(os.environ.get("LOCAL_RANK", -1))
            else:
                self.num_processes = torch.distributed.get_world_size()
                self.process_index = torch.distributed.get_rank()
                self.local_process_index = (int(os.environ.get("LOCAL_RANK", -1)) if dist_information is None else dist_information.local_rank)
            self.set_device()
            if use_deepspeed: self.distributed_type = DistributedType.DEEPSPEED
            if parse_flag_from_env("SAPIENS_ACCELERATOR_CPU_AFFINITY", False): set_numa_affinity(self.local_process_index)
            if self.device.type == "cuda" and not check_cuda_p2p_ib_support():
                if "NCCL_P2P_DISABLE" not in os.environ or "NCCL_IB_DISABLE" not in os.environ: raise NotImplementedError("Using RTX 4000 series doesn't support faster communication broadband via P2P or IB. "+'Please set `NCCL_P2P_DISABLE="1"` and `NCCL_IB_DISABLE="1" or use `sapiens_accelerator launch` which '+"will do this automatically.")
        self.fork_launched = parse_flag_from_env("FORK_LAUNCHED", 0)
    def __repr__(self) -> str: return (f"Distributed environment: {self.distributed_type}{('  Backend: ' + self.backend) if self.backend else ''}\nNum processes: {self.num_processes}\nProcess index: {self.process_index}\nLocal process index: {self.local_process_index}\nDevice: {self.device}\n")
    @staticmethod
    def _reset_state(): PartialState._shared_state.clear()
    @property
    def initialized(self) -> bool: return self._shared_state != {}
    @property
    def use_distributed(self): return self.distributed_type != DistributedType.NO and self.num_processes > 1
    @property
    def is_last_process(self) -> bool: return self.process_index == self.num_processes - 1
    @property
    def is_main_process(self) -> bool: return (self.process_index == 0 if self.distributed_type != DistributedType.MEGATRON_LM else self.is_last_process)
    @property
    def is_local_main_process(self) -> bool: return (self.local_process_index == 0 if self.distributed_type != DistributedType.MEGATRON_LM else self.is_last_process)
    def wait_for_everyone(self):
        if self.distributed_type in (DistributedType.MULTI_GPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU,
        DistributedType.MULTI_XPU, DistributedType.MULTI_CPU, DistributedType.DEEPSPEED, DistributedType.FSDP): torch.distributed.barrier()
        elif self.distributed_type == DistributedType.XLA: xm.rendezvous("sapiens_accelerator.utils.wait_for_everyone")
    def _goes_first(self, is_main: bool):
        if not is_main: self.wait_for_everyone()
        yield
        if is_main: self.wait_for_everyone()
    @contextmanager
    def split_between_processes(self, inputs: list | tuple | dict | torch.Tensor, apply_padding: bool = False):
        if self.num_processes == 1:
            yield inputs
            return
        length = len(inputs)
        if isinstance(inputs, dict):
            length = len(inputs[list(inputs.keys())[0]])
            if not all(len(v) == length for v in inputs.values()): raise ValueError("All values in the dictionary must have the same length")
        num_samples_per_process, num_extras = divmod(length, self.num_processes)
        start_index = self.process_index * num_samples_per_process + min(self.process_index, num_extras)
        end_index = start_index + num_samples_per_process + (1 if self.process_index < num_extras else 0)
        def _split_values(inputs, start_index, end_index):
            if isinstance(inputs, (list, tuple, torch.Tensor)):
                if start_index >= len(inputs): result = inputs[-1:]
                else: result = inputs[start_index:end_index]
                if apply_padding:
                    if isinstance(result, torch.Tensor):
                        from sapiens_accelerator.utils import pad_across_processes, send_to_device
                        tensorized_result = send_to_device(result, self.device)
                        result = pad_across_processes(tensorized_result, pad_index=inputs[-1])
                    else: result += [result[-1]] * (num_samples_per_process + 1 - len(result))
                return result
            elif isinstance(inputs, dict):
                for key in inputs.keys(): inputs[key] = _split_values(inputs[key], start_index, end_index)
                return inputs
            else:
                if is_datasets_available():
                    from datasets import Dataset
                    if isinstance(inputs, Dataset):
                        if start_index >= len(inputs): start_index = len(inputs) - 1
                        if end_index > len(inputs): end_index = len(inputs)
                        result_idcs = list(range(start_index, end_index))
                        if apply_padding: result_idcs += [end_index - 1] * (num_samples_per_process + 1 - len(result_idcs))
                        return inputs.select(result_idcs)
                return inputs
        yield _split_values(inputs, start_index, end_index)
    @contextmanager
    def main_process_first(self): yield from self._goes_first(self.is_main_process)
    @contextmanager
    def local_main_process_first(self): yield from self._goes_first(self.is_local_main_process)
    def on_main_process(self, function: Callable[..., Any] = None):
        if not self.initialized: raise ValueError("The `PartialState` or `Accelerator` must be initialized before calling this function.")
        if self.is_main_process or not self.use_distributed: return function
        return do_nothing
    def on_local_main_process(self, function: Callable[..., Any] = None):
        if self.is_local_main_process or not self.use_distributed: return function
        return do_nothing
    def on_last_process(self, function: Callable[..., Any]):
        if self.is_last_process or not self.use_distributed: return function
        return do_nothing
    def on_process(self, function: Callable[..., Any] = None, process_index: int = None):
        if function is None: return partial(self.on_process, process_index=process_index)
        if (self.process_index == process_index) or (not self.use_distributed): return function
        return do_nothing
    def on_local_process(self, function: Callable[..., Any] = None, local_process_index: int = None):
        if function is None: return partial(self.on_local_process, local_process_index=local_process_index)
        if (self.local_process_index == local_process_index) or (not self.use_distributed): return function
        return do_nothing
    def print(self, *args, **kwargs): pass
    @property
    def default_device(self) -> torch.device:
        if is_mps_available():
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            return torch.device("mps")
        elif is_mlu_available(): return torch.device("mlu")
        elif is_musa_available(): return torch.device("musa")
        elif is_npu_available(): return torch.device("npu")
        elif torch.cuda.is_available(): return torch.device("cuda")
        elif is_xpu_available(): return torch.device("xpu")
        else: return torch.device("cpu")
    def _prepare_backend(self, cpu: bool = False, sagemaker_dp=False, backend: str = None) -> tuple[str, DistributedType]:
        distributed_type = None
        if sagemaker_dp:
            import smdistributed.dataparallel.torch.torch_smddp
            backend = "smddp"
            distributed_type = DistributedType.MULTI_GPU
        elif is_torch_xla_available():
            backend = "xla"
            distributed_type = DistributedType.XLA
        elif int(os.environ.get("LOCAL_RANK", -1)) != -1 and not cpu:
            if is_mlu_available():
                backend = "cncl"
                distributed_type = DistributedType.MULTI_MLU
            elif is_musa_available():
                backend = "mccl"
                distributed_type = DistributedType.MULTI_MUSA
            elif is_npu_available():
                backend = "hccl"
                distributed_type = DistributedType.MULTI_NPU
            elif torch.cuda.is_available():
                if backend is None: backend = "nccl"
                distributed_type = DistributedType.MULTI_GPU
        if distributed_type is None and (int(os.environ.get("LOCAL_RANK", -1)) != -1 or get_int_from_env(["PMI_SIZE", "OMPI_COMM_WORLD_SIZE", "MV2_COMM_WORLD_SIZE", "WORLD_SIZE"], 1) > 1):
            if not cpu and is_xpu_available(): distributed_type = DistributedType.MULTI_XPU
            else: distributed_type = DistributedType.MULTI_CPU
            if (backend in (None, "ccl") and is_ccl_available() and (get_int_from_env(["CCL_WORKER_COUNT"], 0) > 0 or distributed_type == DistributedType.MULTI_XPU)):
                if get_ccl_version() >= "1.12": import oneccl_bindings_for_pytorch
                else: import torch_ccl
                backend = "ccl"
            elif backend in (None, "mpi") and torch.distributed.is_mpi_available(): backend = "mpi"
            else: backend = "gloo"
        if distributed_type is None: distributed_type = DistributedType.NO
        return backend, distributed_type
    def set_device(self):
        if self.device is not None: return
        if self.distributed_type == DistributedType.NO:
            self.device = torch.device("cpu") if self._cpu else self.default_device
            return
        device = str(self.distributed_type).split(".")[-1].replace("MULTI_", "").lower()
        if device not in ("cpu", "gpu", "mlu", "musa", "npu", "xpu", "xla"): raise ValueError(f"Can't set device for {self.distributed_type} ({device}), verify we should be calling `_set_device()` for it!")
        if device == "xla": self.device = xm.xla_device()
        else:
            if device == "gpu": device = "cuda"
            device_module = getattr(torch, device)
            device_index = self.local_process_index % device_module.device_count()
            self.device = torch.device(device, device_index)
            device_module.set_device(self.device)
    def destroy_process_group(self, group=None):
        if self.fork_launched and group is None: return
        if torch.distributed.is_initialized(): torch.distributed.destroy_process_group(group)
    def __getattr__(self, name: str):
        if name in self._known_attrs: raise AttributeError(f"`PartialState` object has no attribute `{name}`. This happens if `PartialState._reset_state()` was called and an `Accelerator` or `PartialState` was not reinitialized.")
        raise AttributeError(f"'PartialState' object has no attribute '{name}'")
class AcceleratorState:
    _shared_state = SharedDict()
    _known_attrs = PartialState._known_attrs + ["deepspeed_plugin", "use_ipex", "fsdp_plugin", "megatron_lm_plugin", "dynamo_plugin"]
    def __init__(self, mixed_precision: str = None, cpu: bool = False, dynamo_plugin=None, deepspeed_plugin=None, fsdp_plugin=None, megatron_lm_plugin=None,
    _from_accelerator: bool = False, **kwargs):
        self.__dict__ = self._shared_state
        if parse_flag_from_env("SAPIENS_ACCELERATOR_USE_CPU"): cpu = True
        if PartialState._shared_state == {}: PartialState(cpu, **kwargs)
        self.__dict__.update(PartialState._shared_state)
        self._check_initialized(mixed_precision, cpu)
        if not self.initialized:
            self.deepspeed_plugins = None
            self.use_ipex = None
            mixed_precision = (parse_choice_from_env("SAPIENS_ACCELERATOR_MIXED_PRECISION", "no") if mixed_precision is None else mixed_precision.lower())
            if mixed_precision == "fp8":
                if not is_fp8_available(): raise ValueError("Using `fp8` precision requires `transformer_engine` or `MS-AMP` to be installed.")
                elif not check_fp8_capability(): mixed_precision = "fp16"
            self.dynamo_plugin = dynamo_plugin
            if not _from_accelerator: raise ValueError("Please make sure to properly initialize your accelerator via `accelerator = Accelerator()` before using any functionality from the `sapiens_accelerator` library.")
            self._mixed_precision = "no" if self.distributed_type == DistributedType.DEEPSPEED else mixed_precision
            if self.distributed_type == DistributedType.XLA and is_torch_xla_available(check_is_tpu=True):
                if mixed_precision == "bf16":
                    if os.environ.get("SAPIENS_ACCELERATOR_DOWNCAST_BF16"):
                        os.environ["XLA_USE_BF16"] = str(0)
                        os.environ["XLA_DOWNCAST_BF16"] = str(1)
                        self.downcast_bfloat = True
                    else:
                        os.environ["XLA_USE_BF16"] = str(1)
                        os.environ["XLA_DOWNCAST_BF16"] = str(0)
                        self.downcast_bfloat = False
            elif os.environ.get("SAPIENS_ACCELERATOR_USE_DEEPSPEED", "false") == "true" and not cpu:
                self.deepspeed_plugins = deepspeed_plugin
                self.distributed_type = DistributedType.DEEPSPEED
            elif self.distributed_type in [DistributedType.MULTI_GPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU, DistributedType.MULTI_XPU]:
                if os.environ.get("SAPIENS_ACCELERATOR_USE_FSDP", "false") == "true" or fsdp_plugin is not None:
                    self.distributed_type = DistributedType.FSDP
                    if self._mixed_precision != "no": fsdp_plugin.set_mixed_precision(self._mixed_precision)
                    self.fsdp_plugin = fsdp_plugin
                if os.environ.get("SAPIENS_ACCELERATOR_USE_MEGATRON_LM", "false") == "true" and self.distributed_type not in [DistributedType.MULTI_XPU]:
                    self.distributed_type = DistributedType.MEGATRON_LM
                    megatron_lm_plugin.set_mixed_precision(self._mixed_precision)
                    self.megatron_lm_plugin = megatron_lm_plugin
            elif self.distributed_type in [DistributedType.MULTI_CPU, DistributedType.MULTI_XPU, DistributedType.NO]:
                if is_ipex_available(): self.use_ipex = parse_flag_from_env("SAPIENS_ACCELERATOR_USE_IPEX", default=True)
                else: self.use_ipex = False
            if (self.dynamo_plugin.backend != DynamoBackend.NO and self._mixed_precision == "no" and self.device.type == "cuda"): torch.backends.cuda.matmul.allow_tf32 = True
            if (self.dynamo_plugin.backend != DynamoBackend.NO and self._mixed_precision == "no" and self.device.type == "musa"): torch.backends.musa.matmul.allow_tf32 = True
            PartialState._shared_state["distributed_type"] = self.distributed_type
    @property
    def initialized(self) -> bool: return self._shared_state != PartialState._shared_state
    def __repr__(self):
        repr = PartialState().__repr__() + f"\nMixed precision type: {self.mixed_precision}\n"
        if self.distributed_type == DistributedType.DEEPSPEED: repr += f"ds_config: {self.deepspeed_plugin.deepspeed_config}\n"
        return repr
    def _check_initialized(self, mixed_precision=None, cpu=None):
        if self.initialized:
            err = "AcceleratorState has already been initialized and cannot be changed, restart your runtime completely and pass `{flag}` to `Accelerator()`."
            if cpu and self.device.type != "cpu": raise ValueError(err.format(flag="cpu=True"))
            if (mixed_precision is not None and mixed_precision != self._mixed_precision and self.distributed_type != DistributedType.DEEPSPEED): raise ValueError(err.format(flag=f"mixed_precision='{mixed_precision}'"))
    @property
    def mixed_precision(self):
        if self.distributed_type == DistributedType.DEEPSPEED:
            config = self.deepspeed_plugin.deepspeed_config
            if config.get("fp16", {}).get("enabled", False): mixed_precision = "fp16"
            elif config.get("bf16", {}).get("enabled", False): mixed_precision = "bf16"
            else: mixed_precision = "no"
        else: mixed_precision = self._mixed_precision
        return mixed_precision
    @staticmethod
    def _reset_state(reset_partial_state: bool = False):
        AcceleratorState._shared_state.clear()
        if reset_partial_state: PartialState._reset_state()
    def destroy_process_group(self, group=None): PartialState().destroy_process_group(group)
    @property
    def fork_launched(self): return PartialState().fork_launched
    @property
    def use_distributed(self): return PartialState().use_distributed
    @property
    def is_last_process(self) -> bool: return PartialState().is_last_process
    @property
    def is_main_process(self) -> bool: return PartialState().is_main_process
    @property
    def is_local_main_process(self) -> bool: return PartialState().is_local_main_process
    def wait_for_everyone(self): PartialState().wait_for_everyone()
    @contextmanager
    def split_between_processes(self, inputs: list | tuple | dict | torch.Tensor, apply_padding: bool = False):
        with PartialState().split_between_processes(inputs, apply_padding=apply_padding) as inputs: yield inputs
    @contextmanager
    def main_process_first(self):
        with PartialState().main_process_first(): yield
    @contextmanager
    def local_main_process_first(self):
        with PartialState().local_main_process_first(): yield
    @property
    def deepspeed_plugin(self):
        if self.distributed_type != DistributedType.DEEPSPEED: return None
        from sapiens_accelerator.utils.deepspeed import get_active_deepspeed_plugin
        return get_active_deepspeed_plugin(self)
    @deepspeed_required
    def get_deepspeed_plugin(self, name: str): return self.deepspeed_plugins[name]
    @deepspeed_required
    def select_deepspeed_plugin(self, name: str = None):
        for key, plugin in self.deepspeed_plugins.items():
            if key != name: plugin._unselect()
        self.deepspeed_plugins[name].select(_from_accelerator_state=True)
    def print(self, *args, **kwargs): PartialState().print(*args, **kwargs)
    def __getattr__(self, name: str):
        if name in self._known_attrs: raise AttributeError(f"`AcceleratorState` object has no attribute `{name}`. This happens if `AcceleratorState._reset_state()` was called and an `Accelerator` or `PartialState` was not reinitialized.")
        raise AttributeError(f"'AcceleratorState' object has no attribute '{name}'")
class GradientState:
    _shared_state = SharedDict()
    def __init__(self, gradient_accumulation_plugin: Optional[GradientAccumulationPlugin] = None):
        self.__dict__ = self._shared_state
        if not self.initialized:
            self.sync_gradients = True
            self.active_dataloader = None
            self.dataloader_references = [None]
            self.plugin_kwargs = (gradient_accumulation_plugin.to_kwargs() if gradient_accumulation_plugin is not None else {})
            self._is_xla_gradients_synced = False
        if gradient_accumulation_plugin is not None and self.plugin_kwargs != gradient_accumulation_plugin.to_kwargs(): self.plugin_kwargs = gradient_accumulation_plugin.to_kwargs()
    @property
    def num_steps(self) -> int: return self.plugin_kwargs.get("num_steps", 1)
    @property
    def adjust_scheduler(self) -> bool: return self.plugin_kwargs.get("adjust_scheduler", False)
    @property
    def sync_with_dataloader(self) -> bool: return self.plugin_kwargs.get("sync_with_dataloader", True)
    @property
    def initialized(self) -> bool: return GradientState._shared_state != {}
    @property
    def end_of_dataloader(self) -> bool:
        if not self.in_dataloader: return False
        return self.active_dataloader.end_of_dataloader
    @property
    def remainder(self) -> int:
        if not self.in_dataloader: return -1
        return self.active_dataloader.remainder
    def __repr__(self): return (f"Sync Gradients: {self.sync_gradients}\nAt end of current dataloader: {self.end_of_dataloader}\nExtra samples added: {self.remainder}\nGradient accumulation plugin: {self.plugin_kwargs}\n")
    @property
    def is_xla_gradients_synced(self):
        if parse_flag_from_env("SAPIENS_ACCELERATOR_USE_FSDP", default=False): return True
        return self._is_xla_gradients_synced
    @is_xla_gradients_synced.setter
    def is_xla_gradients_synced(self, is_synced): self._is_xla_gradients_synced = is_synced
    def _set_sync_gradients(self, sync_gradients):
        self.sync_gradients = sync_gradients
        if (self.sync_gradients and is_torch_xla_available(check_is_tpu=True) and PartialState().distributed_type == DistributedType.XLA): xm.mark_step()
    def _add_dataloader(self, dataloader):
        self.active_dataloader = dataloader
        self.dataloader_references.append(self.active_dataloader)
    def _remove_dataloader(self, dataloader):
        self.dataloader_references.remove(dataloader)
        self.active_dataloader = self.dataloader_references[-1]
    @property
    def in_dataloader(self) -> bool: return self.active_dataloader is not None
    @staticmethod
    def _reset_state(): GradientState._shared_state.clear()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
