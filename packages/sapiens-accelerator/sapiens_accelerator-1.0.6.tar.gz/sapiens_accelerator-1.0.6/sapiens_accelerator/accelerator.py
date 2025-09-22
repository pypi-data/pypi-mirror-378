"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from __future__ import annotations
import contextlib
import functools
import json
import math
import os
import re
import shutil
import sys
import warnings
from collections import OrderedDict
from contextlib import contextmanager
from functools import partial
from types import MethodType
from typing import Any, Callable, Union
import torch
import torch.utils.hooks as hooks
from huggingface_hub import split_torch_state_dict_into_shards
from packaging import version
from .checkpointing import load_accelerator_state, load_custom_state, save_accelerator_state, save_custom_state
from .data_loader import DataLoaderDispatcher, prepare_data_loader, skip_first_batches
from .hooks import AlignDevicesHook
from .logging import get_logger
from .optimizer import SapiensAcceleratordOptimizer
from .scheduler import SapiensAcceleratordScheduler
from .state import AcceleratorState, GradientState, PartialState
from .tracking import LOGGER_TYPE_TO_CLASS, GeneralTracker, filter_trackers
from .utils import (MODEL_NAME, SAFE_WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_NAME, SAFE_WEIGHTS_PATTERN_NAME, WEIGHTS_INDEX_NAME, WEIGHTS_NAME, WEIGHTS_PATTERN_NAME,
AutocastKwargs, DataLoaderConfiguration, DeepSpeedPlugin, DistributedDataParallelKwargs, DistributedType, DynamoBackend, FP8RecipeKwargs, FullyShardedDataParallelPlugin,
GradientAccumulationPlugin, GradScalerKwargs, InitProcessGroupKwargs, KwargsHandler, LoggerType, MegatronLMPlugin, PrecisionType, ProfileKwargs, ProjectConfiguration,
RNGType, TorchDynamoPlugin, apply_fp8_autowrap, check_os_kernel, clean_state_dict_for_safetensors, compare_versions, convert_model, convert_outputs_to_fp32,
extract_model_from_parallel, gather, gather_object, get_mixed_precision_context_manager, get_pretty_name, is_bf16_available, is_sapiens_machine_multi_backend_available,
is_deepspeed_available, is_ipex_available, is_lomo_available, is_megatron_lm_available, is_mlu_available, is_msamp_available, is_musa_available, is_npu_available,
is_torch_version, is_torch_xla_available, is_transformer_engine_available, is_xpu_available, load_fsdp_model, load_fsdp_optimizer, pad_across_processes,
parse_choice_from_env, recursively_apply, reduce, release_memory, save, save_fsdp_model, save_fsdp_optimizer, wait_for_everyone)
from .utils.constants import FSDP_PYTORCH_VERSION, PROFILE_PATTERN_NAME
from .utils.modeling import get_state_dict_offloaded_model
from .utils.other import is_compiled_module
if is_deepspeed_available(): from .utils import (DeepSpeedEngineWrapper, DeepSpeedOptimizerWrapper, DeepSpeedSchedulerWrapper, DummyOptim, DummyScheduler)
if is_megatron_lm_available(): from .utils import (MegatronEngine, MegatronLMDummyDataLoader, MegatronLMDummyScheduler, MegatronLMOptimizerWrapper, MegatronLMSchedulerWrapper,
megatron_lm_initialize, megatron_lm_prepare_data_loader, megatron_lm_prepare_model_optimizer_scheduler)
from torch.distributed.algorithms.join import Join
if is_torch_xla_available():
    import torch_xla.amp as xamp
    import torch_xla.core.xla_model as xm
    import torch_xla.distributed.xla_multiprocessing as xmp
if is_npu_available(check_device=False): import torch_npu
try: from torch.optim.lr_scheduler import LRScheduler
except ImportError: from torch.optim.lr_scheduler import _LRScheduler as LRScheduler
logger = get_logger(__name__)
_split_batches = object()
_dispatch_batches = object()
_even_batches = object()
_use_seedable_sampler = object()
class Accelerator:
    def __init__(self, device_placement: bool = True, split_batches: bool = _split_batches, mixed_precision: PrecisionType | str | None = None, gradient_accumulation_steps: int = 1,
    cpu: bool = False, dataloader_config: DataLoaderConfiguration | None = None, deepspeed_plugin: DeepSpeedPlugin | dict[str, DeepSpeedPlugin] | None = None,
    fsdp_plugin: FullyShardedDataParallelPlugin | None = None, megatron_lm_plugin: MegatronLMPlugin | None = None, rng_types: list[str | RNGType] | None = None,
    log_with: str | LoggerType | GeneralTracker | list[str | LoggerType | GeneralTracker] | None = None, project_dir: str | os.PathLike | None = None,
    project_config: ProjectConfiguration | None = None, gradient_accumulation_plugin: GradientAccumulationPlugin | None = None, step_scheduler_with_optimizer: bool = True,
    kwargs_handlers: list[KwargsHandler] | None = None, dynamo_backend: DynamoBackend | str | None = None, deepspeed_plugins: DeepSpeedPlugin | dict[str, DeepSpeedPlugin] | None = None):
        self.trackers = []
        if project_config is not None: self.project_configuration = project_config
        else: self.project_configuration = ProjectConfiguration(project_dir=project_dir)
        if project_dir is not None and self.project_dir is None: self.project_configuration.set_directories(project_dir)
        if mixed_precision is not None:
            mixed_precision = str(mixed_precision)
            if mixed_precision not in PrecisionType: raise ValueError(f"Unknown mixed_precision mode: {mixed_precision}. Choose between {PrecisionType.list()}")
        dynamo_plugin = TorchDynamoPlugin() if dynamo_backend is None else TorchDynamoPlugin(backend=dynamo_backend)
        if deepspeed_plugins is not None and deepspeed_plugin is not None: raise ValueError("You cannot pass in both `deepspeed_plugins` and `deepspeed_plugin`.")
        elif deepspeed_plugin is not None: deepspeed_plugins = deepspeed_plugin
        if deepspeed_plugins is None:
            if PartialState._shared_state != {} and PartialState().distributed_type == DistributedType.DEEPSPEED: deepspeed_plugins = AcceleratorState().deepspeed_plugins
            else: deepspeed_plugins = (DeepSpeedPlugin() if os.environ.get("SAPIENS_ACCELERATOR_USE_DEEPSPEED", "false") == "true" else None)
        else:
            if (PartialState().distributed_type == DistributedType.DEEPSPEED and AcceleratorState._shared_state != {} and AcceleratorState().deepspeed_plugins is not None): raise NotImplementedError("You cannot pass in a `deepspeed_plugin` when creating a second `Accelerator`. Please make sure the first `Accelerator` is initialized with all the plugins you want to use.")
            if isinstance(deepspeed_plugins, dict):
                for plugin in deepspeed_plugins.values():
                    if not isinstance(plugin, DeepSpeedPlugin): raise TypeError("`deepspeed_plugin` must be a DeepSpeedPlugin object.")
        if deepspeed_plugins is not None:
            os.environ["SAPIENS_ACCELERATOR_USE_DEEPSPEED"] = "true"
            if not is_deepspeed_available(): raise ImportError("DeepSpeed is not installed => run `pip install deepspeed` or build it from source.")
            if is_mlu_available():
                if compare_versions("deepspeed-mlu", "<", "0.10.1"): raise ImportError("DeepSpeed MLU version must be >= 0.10.1. Please update DeepSpeed MLU.")
            elif is_musa_available():
                if compare_versions("deepspeed", ">", "0.14.3"): raise ImportError("DeepSpeed MUSA version must be <= 0.14.3. Please downgrade DeepSpeed.")
            elif compare_versions("deepspeed", "<", "0.9.3"): raise ImportError("DeepSpeed version must be >= 0.9.3. Please update DeepSpeed.")
            mixed_precision = (os.environ.get("SAPIENS_ACCELERATOR_MIXED_PRECISION", "no") if mixed_precision is None else mixed_precision)
            if not isinstance(deepspeed_plugins, dict):
                deepspeed_plugins.set_mixed_precision(mixed_precision)
                deepspeed_plugins.select(_from_accelerator_state=True)
            else:
                for plugin in deepspeed_plugins.values(): plugin.set_mixed_precision(mixed_precision)
                first_plugin = next(iter(deepspeed_plugins.values()))
                first_plugin.select(_from_accelerator_state=True)
            self.deepspeed_engine_wrapped = None
        if os.environ.get("SAPIENS_ACCELERATOR_USE_FSDP", "false") == "true" or isinstance(fsdp_plugin, FullyShardedDataParallelPlugin):
            if not is_torch_version(">=", FSDP_PYTORCH_VERSION): raise ValueError(f"FSDP requires PyTorch >= {FSDP_PYTORCH_VERSION}")
        if fsdp_plugin is None: fsdp_plugin = (FullyShardedDataParallelPlugin() if os.environ.get("SAPIENS_ACCELERATOR_USE_FSDP", "false") == "true" else None)
        else:
            if not isinstance(fsdp_plugin, FullyShardedDataParallelPlugin): raise TypeError("`fsdp_plugin` must be a FullyShardedDataParallelPlugin object.")
            os.environ["SAPIENS_ACCELERATOR_USE_FSDP"] = "true"
        if megatron_lm_plugin is None: megatron_lm_plugin = (MegatronLMPlugin() if os.environ.get("SAPIENS_ACCELERATOR_USE_MEGATRON_LM", "false") == "true" else None)
        else:
            if not isinstance(megatron_lm_plugin, MegatronLMPlugin): raise TypeError("`megatron_lm_plugin` must be a MegatronLMPlugin object.")
            os.environ["SAPIENS_ACCELERATOR_USE_MEGATRON_LM"] = "true"
        if megatron_lm_plugin:
            if not is_megatron_lm_available(): raise ImportError("Megatron is not installed. please build it from source.")
        self.ddp_handler = None
        self.scaler_handler = None
        self.init_handler = None
        self.fp8_recipe_handler = None
        self.autocast_handler = None
        self.profile_handler = None
        self.has_lomo_optimizer = False
        if kwargs_handlers is not None:
            for handler in kwargs_handlers:
                assert isinstance(handler, KwargsHandler), f"Unsupported kwargs handler passed: {handler}, must be one that inherits `sapiens_accelerator.utils.KwargsHandler`."
                if isinstance(handler, DistributedDataParallelKwargs):
                    if self.ddp_handler is not None: raise ValueError("You can only pass one `DistributedDataParallelKwargs` in `kwargs_handler`.")
                    else: self.ddp_handler = handler
                elif isinstance(handler, GradScalerKwargs):
                    if self.scaler_handler is not None: raise ValueError("You can only pass one `GradScalerKwargs` in `kwargs_handler`.")
                    else: self.scaler_handler = handler
                elif isinstance(handler, InitProcessGroupKwargs):
                    if self.init_handler is not None: raise ValueError("You can only pass one `InitProcessGroupKwargs` in `kwargs_handler`.")
                    else: self.init_handler = handler
                elif isinstance(handler, FP8RecipeKwargs):
                    if self.fp8_recipe_handler is not None: raise ValueError("You can only pass one `FP8RecipeKwargs` in `kwargs_handler`.")
                    else: self.fp8_recipe_handler = handler
                elif isinstance(handler, AutocastKwargs):
                    if self.autocast_handler is not None: raise ValueError("You can only pass one `AutocastKwargs` in `kwargs_handler`.")
                    else: self.autocast_handler = handler
                elif isinstance(handler, ProfileKwargs):
                    if self.profile_handler is not None: raise ValueError("You can only pass one `ProfileKwargs` in `kwargs_handler`.")
                    else: self.profile_handler = handler
        kwargs = self.init_handler.to_kwargs() if self.init_handler is not None else {}
        self.state = AcceleratorState(mixed_precision=mixed_precision, cpu=cpu, dynamo_plugin=dynamo_plugin, deepspeed_plugin=deepspeed_plugins,
        fsdp_plugin=fsdp_plugin, megatron_lm_plugin=megatron_lm_plugin, _from_accelerator=True, **kwargs)
        if self.state.mixed_precision == "fp8" and self.fp8_recipe_handler is None: self.fp8_recipe_handler = FP8RecipeKwargs()
        self.delayed_fp8_autocast = False
        if self.fp8_recipe_handler is not None:
            if self.state.mixed_precision != "fp8" and (self.distributed_type not in (DistributedType.FSDP, DistributedType.DEEPSPEED)): raise ValueError("Passing in a `FP8RecipeKwargs` object requires setting `mixed_precision='fp8'`.")
            self.delayed_fp8_autocast = self.fp8_recipe_handler.backend == "TE" and self.distributed_type in (DistributedType.MULTI_GPU, DistributedType.FSDP)
        trackers = filter_trackers(log_with, self.logging_dir)
        self.log_with = trackers
        if ((mixed_precision != "bf16") and getattr(self.state, "downcast_bfloat", False) and (self.state.distributedType != DistributedType.XLA)): raise ValueError("Can only use `downcast_bf16` when using `mixed_precision='bf16'` and on a TPU")
        if gradient_accumulation_plugin is not None:
            if gradient_accumulation_steps != 1: raise ValueError("You can only pass one of `gradient_accumulation_steps` and `gradient_accumulation_plugin`. Please only pass in the created `GradientAccumulationPlugin` object.")
        else:
            gradient_accumulation_steps = int(parse_choice_from_env("SAPIENS_ACCELERATOR_GRADIENT_ACCUMULATION_STEPS", gradient_accumulation_steps))
            gradient_accumulation_plugin = GradientAccumulationPlugin(num_steps=gradient_accumulation_steps)
        self.gradient_state = GradientState(gradient_accumulation_plugin=gradient_accumulation_plugin)
        self.device_placement = device_placement
        if dataloader_config is None: dataloader_config = DataLoaderConfiguration()
        self.dataloader_config = dataloader_config
        self.step_scheduler_with_optimizer = step_scheduler_with_optimizer
        self.scaler = None
        self.native_amp = False
        if (self.state.mixed_precision == "fp16" and self.device.type != "cpu" and self.distributed_type not in (DistributedType.DEEPSPEED, DistributedType.MEGATRON_LM)):
            self.native_amp = True
            if self.device.type not in ("xpu", "cuda", "npu", "xla", "mlu", "musa") or is_torch_xla_available(check_is_tpu=True): raise ValueError(f"fp16 mixed precision requires a GPU (not {self.device.type!r}).")
            kwargs = self.scaler_handler.to_kwargs() if self.scaler_handler is not None else {}
            if self.distributed_type == DistributedType.FSDP:
                from torch.distributed.fsdp.sharded_grad_scaler import ShardedGradScaler
                self.scaler = ShardedGradScaler(**kwargs)
            elif is_torch_xla_available(check_is_gpu=True): self.scaler = xamp.GradScaler(**kwargs)
            elif is_mlu_available(): self.scaler = torch.mlu.amp.GradScaler(**kwargs)
            elif is_musa_available(): self.scaler = torch.musa.amp.GradScaler(**kwargs)
            elif is_npu_available(): self.scaler = torch.npu.amp.GradScaler(**kwargs)
            elif is_xpu_available(): self.scaler = torch.amp.GradScaler("xpu", **kwargs)
            else:
                if version.parse(torch.__version__) > version.parse("2.3"): self.scaler = torch.amp.GradScaler("cuda", **kwargs)
                else: self.scaler = torch.cuda.amp.GradScaler(**kwargs)
        elif self.state.mixed_precision == "bf16" and self.distributed_type not in (DistributedType.DEEPSPEED, DistributedType.MEGATRON_LM):
            if self.device.type in ["cpu", "xpu"]: self.native_amp = True
            else: self.native_amp = is_bf16_available(True)
            if mixed_precision == "bf16" and not self.native_amp and not is_torch_xla_available(): raise ValueError("bf16 mixed precision requires PyTorch >= 1.10 and a supported device.")
        elif self.state.mixed_precision == "fp8":
            self.native_amp = True
            if self.fp8_backend == "MSAMP":
                if self.distributed_type == DistributedType.FSDP: raise NotImplementedError("`sapiens_accelerator` + `MS-AMP` + `FSDP` is not supported at this time. Please consider using deepspeed, which is supported.")
                elif self.distributed_type != DistributedType.DEEPSPEED:
                    if version.parse(torch.__version__) > version.parse("2.3"): self.scaler = torch.amp.GradScaler("cuda")
                    else: self.scaler = torch.cuda.amp.GradScaler()
        self.step = 0
        self._optimizers = []
        self._models = []
        self._schedulers = []
        self._dataloaders = []
        self._custom_objects = []
        self._load_model_state_pre_hook = OrderedDict()
        self._save_model_state_pre_hook = OrderedDict()
        self.rng_types = rng_types
        if self.rng_types is None: self.rng_types = ["generator"]
        self.flag_tensor = None
        check_os_kernel()
    @property
    def deepspeed_plugin(self): return self.state.deepspeed_plugin
    @property
    def use_distributed(self): return self.state.use_distributed
    @property
    def distributed_type(self): return self.state.distributed_type
    @property
    def num_processes(self): return self.state.num_processes
    @property
    def process_index(self): return self.state.process_index
    @property
    def local_process_index(self): return self.state.local_process_index
    @property
    def device(self): return self.state.device
    @property
    def split_batches(self): return self.dataloader_config.split_batches
    @property
    def dispatch_batches(self): return self.dataloader_config.dispatch_batches
    @property
    def even_batches(self): return self.dataloader_config.even_batches
    @even_batches.setter
    def even_batches(self, value: bool): self.dataloader_config.even_batches = value
    @property
    def use_seedable_sampler(self): return self.dataloader_config.use_seedable_sampler
    @property
    def non_blocking(self): return self.dataloader_config.non_blocking
    @property
    def use_stateful_dataloader(self):
        if hasattr(self.dataloader_config, "use_stateful_dataloader"): return self.dataloader_config.use_stateful_dataloader
        return False
    @property
    def project_dir(self): return self.project_configuration.project_dir
    @property
    def logging_dir(self): return self.project_configuration.logging_dir
    @property
    def save_iteration(self): return self.project_configuration.iteration
    @property
    def is_main_process(self): return self.state.is_main_process
    @property
    def is_local_main_process(self): return self.state.is_local_main_process
    @property
    def is_last_process(self): return self.process_index == self.num_processes - 1
    @property
    def mixed_precision(self): return self.state.mixed_precision
    @contextmanager
    def split_between_processes(self, inputs: list | tuple | dict | torch.Tensor, apply_padding: bool = False):
        with PartialState().split_between_processes(inputs, apply_padding=apply_padding) as inputs: yield inputs
    def on_main_process(self, function: Callable[..., Any] = None):
        if function is None:
            if "Accelerator." in self.__qualname__: function = self
            else: raise ValueError("The `on_main_process` decorator must be called with a function on an instantiated `Accelerator` object.")
        def _inner(*args, **kwargs): return PartialState().on_main_process(function)(*args, **kwargs)
        return _inner
    def on_local_main_process(self, function: Callable[..., Any] = None):
        if function is None:
            if "Accelerator." in self.__qualname__: function = self
            else: raise ValueError("The `on_local_main_process` decorator must be called with a function on an instantiated `Accelerator` object.")
        def _inner(*args, **kwargs): return PartialState().on_local_main_process(function)(*args, **kwargs)
        return _inner
    def on_last_process(self, function: Callable[..., Any]):
        if function is None:
            if "Accelerator." in self.__qualname__: function = self
            else: raise ValueError("The `on_last_process` decorator must be called with a function on an instantiated `Accelerator` object.")
        def _inner(*args, **kwargs): return PartialState().on_last_process(function)(*args, **kwargs)
        return _inner
    def on_process(self, function: Callable[..., Any] = None, process_index: int = None):
        if (self is not None) and (process_index is not None) and (function is None): return partial(self.on_process, process_index=process_index)
        if function is None:
            if "Accelerator." in self.__qualname__: function = self
            else: raise ValueError("The `on_main_process` decorator must be called with a function on an instantiated `Accelerator` object.")
        def _inner(*args, **kwargs): return PartialState().on_process(function, process_index)(*args, **kwargs)
        return _inner
    def on_local_process(self, function: Callable[..., Any] = None, local_process_index: int = None):
        if (self is not None) and (local_process_index is not None) and (function is None): return partial(self.on_local_process, local_process_index=local_process_index)
        if function is None:
            if "Accelerator." in self.__qualname__: function = self
            else: raise ValueError("The `on_main_process` decorator must be called with a function on an instantiated `Accelerator` object.")
        def _inner(*args, **kwargs): return PartialState().on_local_process(function, local_process_index)(*args, **kwargs)
        return _inner
    @contextmanager
    def main_process_first(self):
        with self.state.main_process_first(): yield
    @contextmanager
    def local_main_process_first(self):
        with self.state.local_main_process_first(): yield
    @contextmanager
    def no_sync(self, model):
        context = contextlib.nullcontext
        if self.use_distributed: context = getattr(model, "no_sync", context)
        with context(): yield
    @staticmethod
    @contextmanager
    def trigger_sync_in_backward(model):
        if not isinstance(model, torch.nn.parallel.DistributedDataParallel):
            yield
            return
        old_require_backward_grad_sync = model.require_backward_grad_sync
        old_require_forward_param_sync = model.require_forward_param_sync
        model.require_backward_grad_sync = True
        model.require_forward_param_sync = True
        model.reducer.prepare_for_backward([])
        try: yield
        finally:
            model.require_backward_grad_sync = old_require_backward_grad_sync
            model.require_forward_param_sync = old_require_forward_param_sync
    def _do_sync(self):
        if self.gradient_state.sync_with_dataloader and self.gradient_state.end_of_dataloader:
            self.step = 0
            self.gradient_state._set_sync_gradients(True)
        else:
            self.step += 1
            self.gradient_state._set_sync_gradients((self.step % self.gradient_state.num_steps) == 0)
    @property
    def sync_gradients(self): return self.gradient_state.sync_gradients
    @sync_gradients.setter
    def sync_gradients(self, sync_gradients): self.gradient_state.sync_gradients = sync_gradients
    @property
    def gradient_accumulation_steps(self): return self.gradient_state.num_steps
    @gradient_accumulation_steps.setter
    def gradient_accumulation_steps(self, gradient_accumulation_steps): self.gradient_state.plugin_kwargs.update({"num_steps": gradient_accumulation_steps})
    @contextmanager
    def accumulate(self, *models):
        self._do_sync()
        allow_gradient_sync = (self.sync_gradients or (self.use_distributed and self.gradient_state.plugin_kwargs.get("sync_each_batch", False)))
        with contextlib.ExitStack() as cm_stack:
            for m in models: cm_stack.enter_context(contextlib.nullcontext() if allow_gradient_sync else self.no_sync(m))
            yield
    @contextmanager
    def join_uneven_inputs(self, joinables, even_batches=None):
        if self.distributed_type in (DistributedType.MULTI_GPU, DistributedType.MULTI_NPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_XPU):
            dl_even_batches_values = []
            if even_batches is not None:
                iterable_dl_seen = False
                for dl_idx, dl in enumerate(self._dataloaders):
                    if isinstance(dl, DataLoaderDispatcher):
                        iterable_dl_seen = True
                        continue
                    dl_even_batches_values.append((dl_idx, dl.batch_sampler.even_batches))
                    dl.batch_sampler.even_batches = even_batches
            else: even_batches = self.even_batches
            enable_join = False if even_batches else True
            try:
                with Join(joinables, enable=enable_join, throw_on_early_termination=False): yield
            finally:
                for dl_idx, even_batches_value in dl_even_batches_values: self._dataloaders[dl_idx].batch_sampler.even_batches = even_batches_value
        else:
            with contextlib.nullcontext(joinables): yield
    def print(self, *args, **kwargs): self.state.print(*args, **kwargs)
    def _prepare_one(self, obj, first_pass=False, device_placement=None):
        if first_pass:
            if isinstance(obj, torch.utils.data.DataLoader): return self.prepare_data_loader(obj, device_placement=device_placement)
            elif isinstance(obj, torch.nn.Module): return self.prepare_model(obj, device_placement=device_placement)
            elif isinstance(obj, torch.optim.Optimizer):
                optimizer = self.prepare_optimizer(obj, device_placement=device_placement)
                return optimizer
        elif isinstance(obj, LRScheduler):
            scheduler = self.prepare_scheduler(obj)
            return scheduler
        return obj
    def prepare(self, *args, device_placement=None):
        if device_placement is None: device_placement = [None for _ in args]
        elif self.distributed_type in (DistributedType.DEEPSPEED, DistributedType.MEGATRON_LM): raise ValueError("You can't customize device placements with DeepSpeed or Megatron-LM.")
        elif len(device_placement) != len(args): raise ValueError(f"`device_placement` should be a list with {len(args)} elements (the number of objects passed).")
        for obj in args:
            if (isinstance(obj, torch.nn.Module) and self.verify_device_map(obj) and self.distributed_type != DistributedType.NO and os.environ.get("SAPIENS_ACCELERATOR_BYPASS_DEVICE_MAP", "false") != "true"): raise ValueError("You can't train a model that has been loaded with `device_map='auto'` in any distributed mode. Please rerun your script specifying `--num_processes=1` or by launching with `python {{myscript.py}}`.")
        if self.distributed_type == DistributedType.DEEPSPEED:
            model_count = 0
            for obj in args:
                if isinstance(obj, torch.nn.Module): model_count += 1
            if model_count > 1: raise AssertionError("You can't use same `Accelerator()` instance with multiple models when using DeepSpeed")
        if self.distributed_type == DistributedType.XLA:
            model_device, optimizer_device = self._get_devices()
            if model_device is not None and optimizer_device is not None and model_device != optimizer_device: raise ValueError("The model and the optimizer parameters are not on the same device, which probably means you created an optimizer around your model **before** putting on the device. Make sure the line model.to(device) is before the optimizer creation in your script or remove it entirely and use the flag default value for `device_placement` in your `Accelerator` to let it handle that part for you.")
        tpu_should_fix_optimizer = self.device_placement and self.distributed_type == DistributedType.XLA
        if tpu_should_fix_optimizer: old_named_params = self._get_named_parameters(*args)
        if self.distributed_type in [DistributedType.MULTI_CPU, DistributedType.MULTI_XPU, DistributedType.NO]:
            if self.device.type == "cpu" and self.state.use_ipex: args = self._prepare_ipex_or_xpu(*args)
            elif self.device.type == "xpu" and is_xpu_available(): args = self._prepare_ipex_or_xpu(*args)
        if self.fp8_backend == "TE": args = self._prepare_te(*args)
        if self.distributed_type == DistributedType.DEEPSPEED: result = self._prepare_deepspeed(*args)
        elif self.distributed_type == DistributedType.MEGATRON_LM: result = self._prepare_megatron_lm(*args)
        else:
            if self.fp8_backend == "MSAMP": args, device_placement = self._prepare_msamp(*args, device_placement=device_placement)
            result = tuple(self._prepare_one(obj, first_pass=True, device_placement=d) for obj, d in zip(args, device_placement))
            result = tuple(self._prepare_one(obj, device_placement=d) for obj, d in zip(result, device_placement))
        if tpu_should_fix_optimizer:
            new_named_params = self._get_named_parameters(*result)
            mapping = {p: new_named_params[n] for n, p in old_named_params.items()}
            for obj in result:
                if isinstance(obj, torch.optim.Optimizer): obj._switch_parameters(mapping)
        for item in result:
            if any(item in container for container in (self._dataloaders, self._models, self._optimizers, self._schedulers)): item._is_sapiens_accelerator_prepared = True
        return result if len(result) > 1 else result[0]
    def prepare_model(self, model: torch.nn.Module, device_placement: bool = None, evaluation_mode: bool = False):
        if device_placement is None: device_placement = self.device_placement and self.distributed_type != DistributedType.FSDP
        self._models.append(model)
        if (self.verify_device_map(model) and self.distributed_type != DistributedType.NO and os.environ.get("SAPIENS_ACCELERATOR_BYPASS_DEVICE_MAP", "false") != "true"): raise ValueError("You can't train a model that has been loaded with `device_map='auto'` in any distributed mode. Please rerun your script specifying `--num_processes=1` or by launching with `python {{myscript.py}}`.")
        if self.native_amp:
            model._original_forward = model.forward
            autocast_context = get_mixed_precision_context_manager(self.native_amp, self.autocast_handler)
            if self.fp8_backend == "MSAMP" or not hasattr(model.forward, "__func__"):
                model_forward_func = model.forward
                model.forward = convert_outputs_to_fp32(autocast_context(model_forward_func))
            else:
                model_forward_func = model.forward.__func__
                new_forward = autocast_context(model_forward_func)
                model.forward = MethodType(new_forward, model)
                model.forward = MethodType(convert_outputs_to_fp32(model.forward.__func__), model)
        if self.fp8_backend == "TE" and not self.delayed_fp8_autocast: model = apply_fp8_autowrap(model, self.fp8_recipe_handler)
        if (getattr(model, "is_loaded_in_8bit", False) or getattr(model, "is_loaded_in_4bit", False)) and getattr(model, "hf_device_map", False):
            model_devices = set(model.hf_device_map.values())
            if len(model_devices) > 1 and self.distributed_type != DistributedType.NO: raise ValueError("You can't train a model that has been loaded in 8-bit or 4-bit precision on multiple devices in any distributed mode. In order to use 8-bit or 4-bit models that have been loaded across multiple GPUs the solution is to use Naive Pipeline Parallelism. Therefore you should not specify that you are under any distributed regime in your sapiens_accelerator config.")
            elif len(model_devices) == 1:
                current_device = list(model_devices)[0]
                current_device_index = (current_device.index if isinstance(current_device, torch.device) else current_device)
                if torch.device(current_device_index) != self.device:
                    if (self.device.index is not None) or (current_device_index != 0): raise ValueError("You can't train a model that has been loaded in 8-bit or 4-bit precision on a different device than the one you're training on. Make sure you loaded the model on the correct device using for example `device_map={'':torch.cuda.current_device()}` or `device_map={'':torch.xpu.current_device()}`")
            if ("cpu" in model_devices and not is_sapiens_machine_multi_backend_available()) or "disk" in model_devices:
                raise ValueError("You can't train a model that has been loaded in 8-bit or 4-bit precision with CPU or disk offload. If you want train the 8-bit or 4-bit model in CPU, please install sapiens_machine with multi-backend.")
        elif device_placement and not self.verify_device_map(model): model = model.to(self.device)
        if not evaluation_mode:
            if self.distributed_type in (DistributedType.MULTI_GPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU, DistributedType.MULTI_XPU):
                if any(p.requires_grad for p in model.parameters()):
                    kwargs = self.ddp_handler.to_kwargs() if self.ddp_handler is not None else {}
                    if os.environ.get("SAPIENS_ACCELERATOR_BYPASS_DEVICE_MAP", "false") != "true": device_ids, output_device = [self.local_process_index], self.local_process_index
                    else: device_ids, output_device = None, None
                    model = torch.nn.parallel.DistributedDataParallel(model, device_ids=device_ids, output_device=output_device, **kwargs)
                    if self.ddp_handler is not None: self.ddp_handler.register_comm_hook(model)
            elif self.distributed_type == DistributedType.FSDP:
                from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
                is_type_fsdp = isinstance(model, FSDP) or (is_compiled_module(model) and isinstance(model._orig_mod, FSDP))
                if not is_type_fsdp:
                    self.state.fsdp_plugin.set_auto_wrap_policy(model)
                    fsdp_plugin = self.state.fsdp_plugin
                    kwargs = {"sharding_strategy": fsdp_plugin.sharding_strategy, "cpu_offload": fsdp_plugin.cpu_offload, "auto_wrap_policy": fsdp_plugin.auto_wrap_policy,
                    "mixed_precision": fsdp_plugin.mixed_precision_policy, "sync_module_states": fsdp_plugin.sync_module_states, "backward_prefetch": fsdp_plugin.backward_prefetch,
                    "forward_prefetch": fsdp_plugin.forward_prefetch, "use_orig_params": fsdp_plugin.use_orig_params, "param_init_fn": fsdp_plugin.param_init_fn,
                    "ignored_modules": fsdp_plugin.ignored_modules, "limit_all_gathers": fsdp_plugin.limit_all_gathers, "device_id": self.device}
                    model = FSDP(model, **kwargs)
                    if fsdp_plugin.activation_checkpointing:
                        from torch.distributed.algorithms._checkpoint.checkpoint_wrapper import (CheckpointImpl, apply_activation_checkpointing, checkpoint_wrapper)
                        apply_activation_checkpointing(model, checkpoint_wrapper_fn=functools.partial(checkpoint_wrapper, checkpoint_impl=CheckpointImpl.NO_REENTRANT), auto_wrap_policy=fsdp_plugin.auto_wrap_policy)
                if self.mixed_precision != "no":
                    upcasted_log = []
                    for module in FSDP.fsdp_modules(model):
                        if not module._has_params: continue
                        param = module._flat_param
                        if (param.dtype != torch.float32 and param.device != torch.device("meta") and param.requires_grad):
                            name_param_log = (module.module.__class__.__name__, ", ".join(module._flat_param._fqns))
                            if name_param_log not in upcasted_log: upcasted_log.append(name_param_log)
                            param.data = param.data.to(torch.float32)
                            module._handle._orig_param_dtype = torch.float32
                if len(self._models) > 1 and (self._models[-2] is self._models[-1]): del self._models[-2]
                self._models[-1] = model
            elif self.distributed_type == DistributedType.MULTI_CPU:
                kwargs = self.ddp_handler.to_kwargs() if self.ddp_handler is not None else {}
                model = torch.nn.parallel.DistributedDataParallel(model, **kwargs)
                if self.ddp_handler is not None: self.ddp_handler.register_comm_hook(model)
            elif self.distributed_type == DistributedType.XLA and self.state.fork_launched: model = xmp.MpModelWrapper(model).to(self.device)
        if self.delayed_fp8_autocast: model = apply_fp8_autowrap(model, self.fp8_recipe_handler)
        if self.state.dynamo_plugin.backend != DynamoBackend.NO and not is_compiled_module(model):
            if not is_torch_version(">=", "2.0"): raise ValueError("Using `torch.compile` requires PyTorch 2.0 or higher.")
            model = torch.compile(model, **self.state.dynamo_plugin.to_kwargs())
        return model
    def _prepare_te(self, *args):
        if not is_transformer_engine_available(): raise ImportError("`transformer_engine` was not found on your system. Please ensure that `transformer_engine` is installed")
        model, optimizer = None, None
        num_models, num_optimizers = 0, 0
        result = [obj for obj in args]
        for obj in result:
            if isinstance(obj, torch.nn.Module):
                model = obj
                num_models += 1
            elif isinstance(obj, (torch.optim.Optimizer)):
                optimizer = obj
                num_optimizers += 1
        if optimizer is None and model is None: return result
        elif optimizer is None or model is None: raise ValueError("You must pass a model and an optimizer together to `sapiens_accelerator.prepare()` when using TransformerEngine.")
        elif num_models > 1 or num_optimizers > 1: raise ValueError(f"You can't use multiple models ({num_models}) or optimizers {num_optimizers} with TransformerEngine.")
        old_named_params = self._get_named_parameters(model)
        with torch.no_grad(): convert_model(model)
        new_named_params = self._get_named_parameters(model)
        mapping = {p: new_named_params[n] for n, p in old_named_params.items()}
        for param_group in optimizer.param_groups: param_group["params"] = [mapping[p] for p in param_group["params"]]
        return result
    def _prepare_deepspeed(self, *args):
        import deepspeed
        ds_initialize = deepspeed.initialize
        if self.fp8_backend == "MSAMP":
            from msamp import deepspeed as msamp_deepspeed
            ds_initialize = msamp_deepspeed.initialize
        deepspeed_plugin = self.deepspeed_plugin
        is_dataloader_present = any(isinstance(obj, torch.utils.data.DataLoader) for obj in args)
        result = [self._prepare_one(obj, first_pass=True) if isinstance(obj, torch.utils.data.DataLoader) else obj for obj in args]
        if deepspeed_plugin.is_auto("train_micro_batch_size_per_gpu"):
            if is_dataloader_present:
                batch_sizes = [obj.batch_size for obj in args if hasattr(obj, "batch_size")]
                if any(bs is None for bs in batch_sizes): raise ValueError("At least one of the dataloaders passed to `sapiens_accelerator.prepare()` has `None` as batch size. Please set an integer value in `train_micro_batch_size_per_gpu` in the deepspeed config file or assign integer value to `AcceleratorState().deepspeed_plugin.deepspeed_config['train_micro_batch_size_per_gpu']`.")
                if self.split_batches: batch_sizes = [batch_size // self.num_processes for batch_size in batch_sizes]
                batch_size_per_device = min(batch_sizes) if deepspeed_plugin.is_train_batch_min else max(batch_sizes)
            else: raise ValueError("When using DeepSpeed, `sapiens_accelerator.prepare()` requires you to pass at least one of training or evaluation dataloaders with `batch_size` attribute returning an integer value or alternatively set an integer value in `train_micro_batch_size_per_gpu` in the deepspeed config file or assign integer value to `AcceleratorState().deepspeed_plugin.deepspeed_config['train_micro_batch_size_per_gpu']`.")
        else: batch_size_per_device = deepspeed_plugin.get_value("train_micro_batch_size_per_gpu")
        deepspeed_plugin.fill_match("gradient_accumulation_steps", must_match=False, gradient_accumulation_steps=self.gradient_accumulation_steps)
        config_kwargs = {"gradient_clipping": 1.0, "zero_optimization.stage3_gather_16bit_weights_on_model_save": False}
        if batch_size_per_device is not None:
            config_kwargs["train_micro_batch_size_per_gpu"] = batch_size_per_device
            config_kwargs["train_batch_size"] = (batch_size_per_device * deepspeed_plugin.get_value("gradient_accumulation_steps") * self.num_processes)
        model = None
        optimizer = None
        scheduler = None
        for obj in result:
            if isinstance(obj, torch.nn.Module): model = obj
            elif isinstance(obj, (torch.optim.Optimizer, DummyOptim)): optimizer = obj
            elif (isinstance(obj, (LRScheduler, DummyScheduler))) or (type(obj).__name__ in deepspeed.runtime.lr_schedules.VALID_LR_SCHEDULES): scheduler = obj
        if optimizer is not None:
            if "optimizer" in deepspeed_plugin.deepspeed_config and not isinstance(optimizer, (DummyOptim)): raise ValueError("You cannot specify an optimizer in the config file and in the code at the same time. Please remove the optimizer from the config file or create `sapiens_accelerator.utils.DummyOptim` in the code.")
            elif "optimizer" not in deepspeed_plugin.deepspeed_config and isinstance(optimizer, (DummyOptim)): raise ValueError("You cannot create a `DummyOptim` without specifying an optimizer in the config file.")
            if isinstance(optimizer, (torch.optim.Optimizer)): deepspeed_plugin.deepspeed_config["zero_allow_untested_optimizer"] = True
        if scheduler is not None:
            if "scheduler" in deepspeed_plugin.deepspeed_config and not isinstance(scheduler, (DummyScheduler)): raise ValueError("You cannot specify a scheduler in the config file and in the code at the same time. Please remove the scheduler from the config file or create `sapiens_accelerator.utils.DummyScheduler` in the code.")
            elif ("scheduler" not in deepspeed_plugin.deepspeed_config and isinstance(scheduler, (DummyScheduler)) and scheduler.lr_scheduler_callable is None): raise ValueError("Either specify a scheduler in the config file or pass in the `lr_scheduler_callable` parameter when using `sapiens_accelerator.utils.DummyScheduler`.")
        if optimizer is not None and scheduler is not None:
            if isinstance(optimizer, (DummyOptim)) and not isinstance(scheduler, (DummyScheduler)): raise ValueError("You can only specify `sapiens_accelerator.utils.DummyScheduler` in the code when using `sapiens_accelerator.utils.DummyOptim`.")
        if model is not None:
            if getattr(self.fp8_recipe_handler, "backend", None) == "TE": model = apply_fp8_autowrap(model, self.fp8_recipe_handler)
            deepspeed_plugin.set_moe_leaf_modules(model)
            hidden_size_based_keys = ["zero_optimization.reduce_bucket_size", "zero_optimization.stage3_prefetch_bucket_size", "zero_optimization.stage3_param_persistence_threshold"]
            hidden_size_auto_keys = [x for x in hidden_size_based_keys if deepspeed_plugin.is_auto(x)]
            if len(hidden_size_auto_keys) > 0:
                reasoning = ("therefore it's not possible to automatically fill out the following `auto` entries " + f"in the DeepSpeed config file: {hidden_size_auto_keys}. You can fix that by replacing " + "`auto` values for these keys with an integer value of your choice.")
                if not hasattr(model, "config"): raise ValueError("Can't find `model.config` entry, " + reasoning)
                if hasattr(model.config, "hidden_size"): hidden_size = model.config.hidden_size
                elif hasattr(model.config, "hidden_sizes"): hidden_size = max(model.config.hidden_sizes)
                else: raise ValueError("Can find neither `model.config.hidden_size` nor `model.config.hidden_sizes`, " + reasoning)
                config_kwargs.update({"zero_optimization.reduce_bucket_size": hidden_size * hidden_size, "zero_optimization.stage3_prefetch_bucket_size": int(0.9 * hidden_size * hidden_size),
                "zero_optimization.stage3_param_persistence_threshold": 10 * hidden_size})
            if isinstance(optimizer, (DummyOptim)): config_kwargs.update({"optimizer.params.lr": optimizer.lr, "optimizer.params.weight_decay": optimizer.weight_decay})
            if isinstance(scheduler, (DummyScheduler)) and scheduler.lr_scheduler_callable is None:
                max_lr = (getattr(scheduler.optimizer, "lr", None) if getattr(scheduler.optimizer, "defaults", None) is None else scheduler.optimizer.defaults["lr"])
                config_kwargs.update({"scheduler.params.warmup_min_lr": 0, "scheduler.params.warmup_max_lr": max_lr, "scheduler.params.warmup_num_steps": scheduler.warmup_num_steps})
                if scheduler.total_num_steps is not None: config_kwargs["scheduler.params.total_num_steps"] = (math.ceil(scheduler.total_num_steps / self.num_processes) if not self.split_batches else scheduler.total_num_steps)
            deepspeed_plugin.deepspeed_config_process(must_match=False, **config_kwargs)
            self.deepspeed_config = deepspeed_plugin.deepspeed_config
            kwargs = dict(model=model, config_params=self.deepspeed_config)
            if optimizer is not None:
                if isinstance(optimizer, (DummyOptim)):
                    kwargs["model_parameters"] = optimizer.params
                    if isinstance(scheduler, (DummyScheduler)) and scheduler.lr_scheduler_callable is not None: kwargs["lr_scheduler"] = scheduler.lr_scheduler_callable
                else:
                    if self.deepspeed_config["zero_optimization"].get("offload_optimizer", {}).get("device", "none") != "none" and self.deepspeed_config.get("zero_force_ds_cpu_optimizer", True):
                        from deepspeed.ops.adam import DeepSpeedCPUAdam
                        defaults = {k: v for k, v in optimizer.defaults.items() if k in ["lr", "weight_decay"]}
                        optimizer = DeepSpeedCPUAdam(optimizer.param_groups, **defaults)
                    kwargs["optimizer"] = optimizer
                    if scheduler is not None:
                        if type(scheduler).__name__ in deepspeed.runtime.lr_schedules.VALID_LR_SCHEDULES: kwargs["lr_scheduler"] = scheduler
            engine, optimizer, _, lr_scheduler = ds_initialize(**kwargs)
            if optimizer is not None: optimizer = DeepSpeedOptimizerWrapper(optimizer)
            if scheduler is not None:
                if lr_scheduler is None: scheduler = SapiensAcceleratordScheduler(scheduler, optimizer, step_with_optimizer=self.step_scheduler_with_optimizer, split_batches=self.split_batches)
                else: scheduler = DeepSpeedSchedulerWrapper(lr_scheduler, optimizer)
            for i in range(len(result)):
                if isinstance(result[i], torch.nn.Module): result[i] = engine
                elif isinstance(result[i], (torch.optim.Optimizer, DummyOptim)): result[i] = optimizer
                elif (isinstance(result[i], (LRScheduler, DummyScheduler))) or (type(result[i]).__name__ in deepspeed.runtime.lr_schedules.VALID_LR_SCHEDULES): result[i] = scheduler
            if self.deepspeed_engine_wrapped is None: self.deepspeed_engine_wrapped = DeepSpeedEngineWrapper(engine)
            self._models.append(engine)
            if optimizer is not None: self._optimizers.append(optimizer)
            if scheduler is not None: self._schedulers.append(scheduler)
        return tuple(result)
    def _prepare_megatron_lm(self, *args):
        megatron_lm_plugin = self.state.megatron_lm_plugin
        micro_batch_size = None
        if not megatron_lm_plugin.megatron_dataset_flag:
            batch_sizes = [obj.batch_size for obj in args if hasattr(obj, "batch_size")]
            if len(batch_sizes) == 0: raise ValueError("You must specify a training or evaluation dataloader in `sapiens_accelerator.prepare()` when using Megatron-LM.")
            micro_batch_size = min(batch_sizes) if megatron_lm_plugin.is_train_batch_min else max(batch_sizes)
        else:
            for obj in args:
                if isinstance(obj, MegatronLMDummyDataLoader):
                    micro_batch_size = obj.dataset_args["micro_batch_size"]
                    break
        if micro_batch_size is not None:
            dp_degree = self.num_processes // (megatron_lm_plugin.tp_degree * megatron_lm_plugin.pp_degree)
            megatron_lm_plugin.set_training_args(micro_batch_size, dp_degree)
        else: raise ValueError("When you do not pass the dataloader parameter, the `data_parallel_size`, `micro_batch_size`, and `global_batch_size` megatron parameters will not be updated.")
        model = None
        optimizer = None
        scheduler = None
        batch_data = None
        for obj in args:
            if isinstance(obj, torch.utils.data.DataLoader) and batch_data is None: batch_data = next(iter(obj))
            elif isinstance(obj, torch.nn.Module): model = obj
            elif isinstance(obj, (torch.optim.Optimizer)): optimizer = obj
            elif isinstance(obj, (LRScheduler, MegatronLMDummyScheduler)): scheduler = obj
        if model is not None: megatron_lm_plugin.set_network_size_args(model, batch_data)
        if optimizer is not None: megatron_lm_plugin.set_optimizer_type(optimizer)
        if scheduler is not None:
            if not isinstance(scheduler, MegatronLMDummyScheduler): raise ValueError("You can't use a custom scheduler with Megatron-LM. Please use the `sapiens_accelerator.utils.MegatronLMDummyScheduler` instead.")
            megatron_lm_plugin.set_scheduler_args(scheduler)
        megatron_lm_initialize(self, args_defaults=megatron_lm_plugin.megatron_lm_default_args)
        (model, optimizer, scheduler) = megatron_lm_prepare_model_optimizer_scheduler(self)
        self.wait_for_everyone()
        counter = 0
        result = []
        for obj in args:
            if isinstance(obj, torch.utils.data.DataLoader):
                result.append(megatron_lm_prepare_data_loader(self, obj))
                counter += 1
            elif isinstance(obj, MegatronLMDummyDataLoader):
                if counter == 0:
                    obj.set_megatron_data_args()
                    dataloaders = megatron_lm_prepare_data_loader(self, obj)
                result.append(dataloaders[counter])
                counter += 1
            else: result.append(obj)
        if model is not None: model = MegatronEngine(self, model, optimizer, scheduler)
        if optimizer is not None: optimizer = MegatronLMOptimizerWrapper(optimizer)
        if scheduler is not None: scheduler = MegatronLMSchedulerWrapper(scheduler, optimizer)
        for i in range(len(result)):
            if isinstance(result[i], torch.nn.Module): result[i] = model
            elif isinstance(result[i], torch.optim.Optimizer): result[i] = optimizer
            elif isinstance(result[i], MegatronLMDummyScheduler): result[i] = scheduler
        if model is not None:
            self._models.append(model)
            if len(self._models) > 1: raise AssertionError("You can't use same `Accelerator()` instance with multiple models when using Megatron-LM")
        if optimizer is not None: self._optimizers.append(optimizer)
        if scheduler is not None: self._schedulers.append(scheduler)
        return tuple(result)
    def _prepare_ipex_or_xpu(self, *args):
        if self.state.use_ipex:
            if not is_ipex_available(): raise ImportError("IPEX is not installed or IPEX's version does not match current PyTorch version. Please refer to https://github.com/intel/intel-extension-for-pytorch.")
        model = None
        optimizer = None
        result = [obj for obj in args]
        for obj in result:
            if isinstance(obj, torch.nn.Module):
                model = obj
                model.train()
            elif isinstance(obj, (torch.optim.Optimizer)): optimizer = obj
        if optimizer is not None and model is not None:
            dtype = torch.bfloat16 if self.state.mixed_precision == "bf16" else None
            if self.device.type == "xpu" and model.device.type == "cpu": model = model.to(self.device)
            if is_ipex_available():
                import intel_extension_for_pytorch as ipex
                model, optimizer = ipex.optimize(model, optimizer=optimizer, dtype=dtype, inplace=True, level="O1")
        for i in range(len(result)):
            if isinstance(result[i], torch.nn.Module): result[i] = model
            elif isinstance(result[i], (torch.optim.Optimizer)): result[i] = optimizer
        return tuple(result)
    def _prepare_msamp(self, *args, device_placement):
        if not is_msamp_available(): raise ImportError("MS-AMP was not found on your system. Please ensure that MS-AMP is available or choose `'te'` as the backend for FP8 mixed precision training.")
        import msamp
        model, optimizer = None, None
        optimizer_index = None
        num_models, num_optimizers = 0, 0
        result = [obj for obj in args]
        for i, obj in enumerate(result):
            if isinstance(obj, torch.nn.Module):
                model = obj
                num_models += 1
            elif isinstance(obj, (torch.optim.Optimizer)):
                optimizer = obj
                optimizer_index = i
                num_optimizers += 1
        if optimizer is None and model is None: return result, device_placement
        elif optimizer is None or model is None: raise ValueError("You must pass a model and an optimizer together to `sapiens_accelerator.prepare()` when using MS-AMP.")
        elif num_models > 1 or num_optimizers > 1: raise ValueError(f"You can't use multiple models ({num_models}) or optimizers {num_optimizers} with MS-AMP.")
        else: model, optimizer = msamp.initialize(model, optimizer, opt_level=self.fp8_recipe_handler.opt_level)
        for i in range(len(result)):
            if isinstance(result[i], torch.nn.Module): result[i] = model
            elif isinstance(result[i], (torch.optim.Optimizer)): result[i] = optimizer
        if optimizer_index is not None: device_placement[optimizer_index] = False
        return tuple(result), device_placement
    def prepare_data_loader(self, data_loader: torch.utils.data.DataLoader, device_placement=None, slice_fn_for_dispatch=None):
        if getattr(data_loader, "_is_sapiens_accelerator_prepared", False):
            if data_loader not in self._dataloaders: self._dataloaders.append(data_loader)
            return data_loader
        if device_placement is None: device_placement = self.device_placement if self.distributed_type != DistributedType.XLA else False
        prepared_data_loader = prepare_data_loader(data_loader, self.device, num_processes=self.num_processes, process_index=self.process_index,
        split_batches=self.split_batches, put_on_device=device_placement, rng_types=self.rng_types.copy(), dispatch_batches=self.dispatch_batches,
        even_batches=self.even_batches, slice_fn_for_dispatch=slice_fn_for_dispatch, use_seedable_sampler=self.use_seedable_sampler,
        non_blocking=self.non_blocking, use_stateful_dataloader=self.use_stateful_dataloader)
        self._dataloaders.append(prepared_data_loader)
        return prepared_data_loader
    def prepare_optimizer(self, optimizer: torch.optim.Optimizer, device_placement=None):
        if is_lomo_available():
            from lomo_optim import AdaLomo, Lomo
            self.has_lomo_optimizer |= isinstance(optimizer, (Lomo, AdaLomo))
        if getattr(optimizer, "_is_sapiens_accelerator_prepared", False):
            if optimizer not in self._optimizers: self._optimizers.append(optimizer)
            return optimizer
        if device_placement is None: device_placement = self.device_placement
        scaler = None if self.fp8_backend == "MSAMP" else self.scaler
        optimizer = SapiensAcceleratordOptimizer(optimizer, device_placement=device_placement, scaler=scaler)
        self._optimizers.append(optimizer)
        return optimizer
    def prepare_scheduler(self, scheduler: LRScheduler):
        if getattr(scheduler, "_is_sapiens_accelerator_prepared", False):
            if scheduler not in self._schedulers: self._schedulers.append(scheduler)
            return scheduler
        optimizer = self._optimizers
        for opt in self._optimizers:
            if getattr(scheduler, "optimizer", None) == opt.optimizer:
                optimizer = opt
                break
        scheduler = SapiensAcceleratordScheduler(scheduler, optimizer, step_with_optimizer=self.step_scheduler_with_optimizer, split_batches=self.split_batches)
        self._schedulers.append(scheduler)
        return scheduler
    def backward(self, loss, **kwargs):
        learning_rate = kwargs.get("learning_rate")
        if self.distributed_type != DistributedType.DEEPSPEED: loss = loss / self.gradient_accumulation_steps
        if self.distributed_type == DistributedType.DEEPSPEED: self.deepspeed_engine_wrapped.backward(loss, **kwargs)
        elif self.distributed_type == DistributedType.MEGATRON_LM: return
        elif self.scaler is not None: self.scaler.scale(loss).backward(**kwargs)
        elif learning_rate is not None and self.has_lomo_optimizer: self.lomo_backward(loss, learning_rate)
        else: loss.backward(**kwargs)
    def set_trigger(self): self.flag_tensor = torch.tensor(1, device=self.device)
    def check_trigger(self):
        if self.flag_tensor is None: self.flag_tensor = torch.tensor(0, device=self.device)
        flag_tensor = self.reduce(self.flag_tensor)
        if flag_tensor.item() >= 1:
            self.flag_tensor = torch.tensor(0, device=self.device)
            return True
        return False
    def unscale_gradients(self, optimizer=None):
        if self.native_amp and self.mixed_precision == "fp16":
            if optimizer is None: optimizer = self._optimizers
            elif not isinstance(optimizer, (tuple, list)): optimizer = [optimizer]
            for opt in optimizer:
                while isinstance(opt, SapiensAcceleratordOptimizer): opt = opt.optimizer
                self.scaler.unscale_(opt)
    def clip_grad_norm_(self, parameters, max_norm, norm_type=2):
        if self.distributed_type == DistributedType.FSDP:
            self.unscale_gradients()
            parameters = [p for p in parameters]
            for model in self._models:
                if parameters == [p for p in model.parameters()]: return model.clip_grad_norm_(max_norm, norm_type)
        elif self.distributed_type == DistributedType.DEEPSPEED: return None
        elif self.distributed_type == DistributedType.XLA:
            for acc_opt in self._optimizers:
                if not acc_opt.gradient_state.is_xla_gradients_synced:
                    opt = acc_opt
                    while isinstance(opt, SapiensAcceleratordOptimizer): opt = opt.optimizer
                    gradients = xm._fetch_gradients(opt)
                    xm.all_reduce("sum", gradients, scale=1.0 / self.num_processes)
                    acc_opt.gradient_state.is_xla_gradients_synced = True
            if os.environ.get("SAPIENS_ACCELERATOR_USE_FSDP", "false") == "true":
                self.unscale_gradients()
                parameters = [p for p in parameters]
                for model in self._models:
                    if parameters == [p for p in model.parameters()]: return model.clip_grad_norm_(max_norm, norm_type)
        self.unscale_gradients()
        return torch.nn.utils.clip_grad_norm_(parameters, max_norm, norm_type=norm_type)
    def clip_grad_value_(self, parameters, clip_value):
        if self.distributed_type in [DistributedType.DEEPSPEED, DistributedType.FSDP]: raise Exception("DeepSpeed and FSDP  do not support `clip_grad_value_`. Use `clip_grad_norm_` instead.")
        self.unscale_gradients()
        torch.nn.utils.clip_grad_value_(parameters, clip_value)
    def gather(self, tensor): return gather(tensor)
    def gather_for_metrics(self, input_data, use_gather_object=False):
        try:
            recursively_apply(lambda x: x, input_data, error_on_other_type=True)
            all_tensors = True
        except TypeError: all_tensors = False
        use_gather_object = use_gather_object or not all_tensors
        if use_gather_object: data = gather_object(input_data)
        else: data = self.gather(input_data)
        try:
            if self.gradient_state.end_of_dataloader:
                if self.gradient_state.remainder == -1: return data
                elif self.gradient_state.remainder > 0:
                    def _adjust_samples(tensor): return tensor[: self.gradient_state.remainder]
                    if use_gather_object: return _adjust_samples(data)
                    else: return recursively_apply(_adjust_samples, data)
                else: return data
            else: return data
        except Exception: return data
    def reduce(self, tensor, reduction="sum", scale=1.0): return reduce(tensor, reduction, scale)
    def pad_across_processes(self, tensor, dim=0, pad_index=0, pad_first=False): return pad_across_processes(tensor, dim=dim, pad_index=pad_index, pad_first=pad_first)
    def unwrap_model(self, model, keep_fp32_wrapper: bool = True): return extract_model_from_parallel(model, keep_fp32_wrapper)
    def wait_for_everyone(self): wait_for_everyone()
    @on_main_process
    def init_trackers(self, project_name: str, config: dict | None = None, init_kwargs: dict | None = {}):
        for tracker in self.log_with:
            if issubclass(type(tracker), GeneralTracker): self.trackers.append(tracker)
            else:
                tracker_init = LOGGER_TYPE_TO_CLASS[str(tracker)]
                if tracker_init.requires_logging_directory: self.trackers.append(tracker_init(project_name, self.logging_dir, **init_kwargs.get(str(tracker), {})))
                else: self.trackers.append(tracker_init(project_name, **init_kwargs.get(str(tracker), {})))
        if config is not None:
            for tracker in self.trackers: tracker.store_init_configuration(config)
    def get_tracker(self, name: str, unwrap: bool = False):
        if len(self.trackers) > 0:
            for tracker in self.trackers:
                if tracker.name == name: return tracker.tracker if unwrap else tracker
            raise ValueError(f"{name} is not an available tracker stored inside the `Accelerator`.")
        return GeneralTracker(_blank=True)
    @on_main_process
    def log(self, values: dict, step: int | None = None, log_kwargs: dict | None = {}):
        for tracker in self.trackers: tracker.log(values, step=step, **log_kwargs.get(tracker.name, {}))
    def end_training(self):
        for tracker in self.trackers: tracker.finish()
        self.state.destroy_process_group()
    def save(self, obj, f, safe_serialization=False): save(obj, f, save_on_each_node=self.project_configuration.save_on_each_node, safe_serialization=safe_serialization)
    def save_model(self, model: torch.nn.Module, save_directory: Union[str, os.PathLike], max_shard_size: Union[int, str] = "10GB", safe_serialization: bool = True):
        if os.path.isfile(save_directory): return
        os.makedirs(save_directory, exist_ok=True)
        if any([module._hf_hook.offload for module in model.modules() if hasattr(module, "_hf_hook") and isinstance(module._hf_hook, AlignDevicesHook)]): state_dict = get_state_dict_offloaded_model(model)
        else:
            if any(param.device == torch.device("meta") for param in model.parameters()): raise RuntimeError("You can't save the model since some parameters are on the meta device.")
            state_dict = self.get_state_dict(model)
        if safe_serialization: state_dict = clean_state_dict_for_safetensors(state_dict)
        weights_name = SAFE_WEIGHTS_NAME if safe_serialization else WEIGHTS_NAME
        filename_pattern = SAFE_WEIGHTS_PATTERN_NAME if safe_serialization else WEIGHTS_PATTERN_NAME
        state_dict_split = split_torch_state_dict_into_shards(state_dict, filename_pattern=filename_pattern, max_shard_size=max_shard_size)
        for filename in os.listdir(save_directory):
            full_filename = os.path.join(save_directory, filename)
            weights_no_suffix = weights_name.replace(".bin", "")
            filename_no_suffix = filename.replace(".bin", "")
            reg = re.compile(r"(.*?)-\d{5}-of-\d{5}")
            if (filename.startswith(weights_no_suffix) and os.path.isfile(full_filename) and filename not in state_dict_split.filename_to_tensors.keys()
            and reg.fullmatch(filename_no_suffix) is not None and PartialState().is_main_process): os.remove(full_filename)
        for filename, tensors in state_dict_split.filename_to_tensors.items():
            shard = {tensor: state_dict[tensor] for tensor in tensors}
            self.save(shard, os.path.join(save_directory, filename), safe_serialization=safe_serialization)
        if state_dict_split.is_sharded:
            index = {"metadata": state_dict_split.metadata, "weight_map": state_dict_split.tensor_to_filename}
            save_index_file = SAFE_WEIGHTS_INDEX_NAME if safe_serialization else WEIGHTS_INDEX_NAME
            save_index_file = os.path.join(save_directory, save_index_file)
            with open(save_index_file, "w", encoding="utf-8") as f:
                content = json.dumps(index, indent=2, sort_keys=True) + "\n"
                f.write(content)
        else: path_to_weights = os.path.join(save_directory, WEIGHTS_NAME)
    def register_save_state_pre_hook(self, hook: Callable[..., None]) -> hooks.RemovableHandle:
        handle = hooks.RemovableHandle(self._save_model_state_pre_hook)
        self._save_model_state_pre_hook[handle.id] = hook
        return handle
    def save_state(self, output_dir: str = None, safe_serialization: bool = True, **save_model_func_kwargs):
        if self.project_configuration.automatic_checkpoint_naming: output_dir = os.path.join(self.project_dir, "checkpoints")
        os.makedirs(output_dir, exist_ok=True)
        if self.project_configuration.automatic_checkpoint_naming:
            folders = [os.path.join(output_dir, folder) for folder in os.listdir(output_dir)]
            if (self.project_configuration.total_limit is not None and (len(folders) + 1 > self.project_configuration.total_limit) and self.is_main_process):
                def _inner(folder): return list(map(int, re.findall(r"[\/]?([0-9]+)(?=[^\/]*$)", folder)))[0]
                folders.sort(key=_inner)
                for folder in folders[: len(folders) + 1 - self.project_configuration.total_limit]: shutil.rmtree(folder)
            output_dir = os.path.join(output_dir, f"checkpoint_{self.save_iteration}")
            if os.path.exists(output_dir): raise ValueError(f"Checkpoint directory {output_dir} ({self.save_iteration}) already exists. Please manually override `self.save_iteration` with what iteration to start with.")
            self.wait_for_everyone()
        os.makedirs(output_dir, exist_ok=True)
        if self.distributed_type == DistributedType.XLA: xm.mark_step()
        weights = []
        for i, model in enumerate(self._models):
            if self.distributed_type == DistributedType.FSDP: save_fsdp_model(self.state.fsdp_plugin, self, model, output_dir, i)
            elif self.distributed_type == DistributedType.DEEPSPEED:
                ckpt_id = f"{MODEL_NAME}" if i == 0 else f"{MODEL_NAME}_{i}"
                model.save_checkpoint(output_dir, ckpt_id, **save_model_func_kwargs)
            elif self.distributed_type == DistributedType.MEGATRON_LM: model.save_checkpoint(output_dir)
            else: weights.append(self.get_state_dict(model, unwrap=False))
        optimizers = []
        if self.distributed_type == DistributedType.FSDP:
            for i, opt in enumerate(self._optimizers): save_fsdp_optimizer(self.state.fsdp_plugin, self, opt, self._models[i], output_dir, i)
        elif self.distributed_type not in [DistributedType.DEEPSPEED, DistributedType.MEGATRON_LM]: optimizers = self._optimizers
        schedulers = []
        if self.distributed_type == DistributedType.DEEPSPEED:
            for i, scheduler in enumerate(self._schedulers):
                if isinstance(scheduler, DeepSpeedSchedulerWrapper): continue
                schedulers.append(scheduler)
        elif self.distributed_type not in [DistributedType.MEGATRON_LM]: schedulers = self._schedulers
        dataloaders = self._dataloaders
        for hook in self._save_model_state_pre_hook.values(): hook(self._models, weights, output_dir)
        save_location = save_accelerator_state(output_dir, weights, optimizers, schedulers, dataloaders, self.state.process_index, self.step,
        self.scaler, save_on_each_node=self.project_configuration.save_on_each_node, safe_serialization=safe_serialization)
        for i, obj in enumerate(self._custom_objects): save_custom_state(obj, output_dir, i, save_on_each_node=self.project_configuration.save_on_each_node)
        self.project_configuration.iteration += 1
        return save_location
    def register_load_state_pre_hook(self, hook: Callable[..., None]) -> hooks.RemovableHandle:
        handle = hooks.RemovableHandle(self._load_model_state_pre_hook)
        self._load_model_state_pre_hook[handle.id] = hook
        return handle
    def load_state(self, input_dir: str = None, **load_model_func_kwargs):
        if input_dir is not None:
            input_dir = os.path.expanduser(input_dir)
            if not os.path.isdir(input_dir): raise ValueError(f"Tried to find {input_dir} but folder does not exist")
        elif self.project_configuration.automatic_checkpoint_naming:
            input_dir = os.path.join(self.project_dir, "checkpoints")
            folders = [os.path.join(input_dir, folder) for folder in os.listdir(input_dir)]
            def _inner(folder): return list(map(int, re.findall(r"[\/]?([0-9]+)(?=[^\/]*$)", folder)))[0]
            folders.sort(key=_inner)
            input_dir = folders[-1]
        else: raise ValueError("No input_dir provided and automatic checkpoint naming is disabled.")
        models = []
        for i, model in enumerate(self._models):
            if self.distributed_type == DistributedType.FSDP: load_fsdp_model(self.state.fsdp_plugin, self, model, input_dir, i)
            elif self.distributed_type == DistributedType.DEEPSPEED:
                ckpt_id = f"{MODEL_NAME}" if i == 0 else f"{MODEL_NAME}_{i}"
                model.load_checkpoint(input_dir, ckpt_id, **load_model_func_kwargs)
            elif self.distributed_type == DistributedType.MEGATRON_LM: model.load_checkpoint(input_dir)
            else: models.append(model)
        optimizers = []
        if self.distributed_type == DistributedType.FSDP:
            for i, opt in enumerate(self._optimizers): load_fsdp_optimizer(self.state.fsdp_plugin, self, opt, self._models[i], input_dir, i)
        elif self.distributed_type not in [DistributedType.DEEPSPEED, DistributedType.MEGATRON_LM]: optimizers = self._optimizers
        schedulers = []
        if self.distributed_type == DistributedType.DEEPSPEED:
            for i, scheduler in enumerate(self._schedulers):
                if isinstance(scheduler, DeepSpeedSchedulerWrapper): continue
                schedulers.append(scheduler)
        elif self.distributed_type not in [DistributedType.MEGATRON_LM]: schedulers = self._schedulers
        dataloaders = self._dataloaders
        for hook in self._load_model_state_pre_hook.values(): hook(models, input_dir)
        map_location = load_model_func_kwargs.pop("map_location", None)
        if map_location is None:
            if self.num_processes > 1 and self.distributed_type in (DistributedType.MULTI_GPU, DistributedType.MULTI_MLU, DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU): map_location = "on_device"
            else: map_location = "cpu"
        override_attributes = load_accelerator_state(input_dir, models, optimizers, schedulers, dataloaders, self.state.process_index, self.scaler, map_location, **load_model_func_kwargs)
        if "step" in override_attributes: self.step = override_attributes["step"]
        custom_checkpoints = [f for f in os.listdir(input_dir) if re.search(r"^custom_checkpoint_\d+\.pkl$", f) is not None]
        if len(custom_checkpoints) != len(self._custom_objects):
            err = (f"Number of custom checkpoints in folder {input_dir} does not match the number of registered objects:")
            err += f"\n\tFound checkpoints: {len(custom_checkpoints)}"
            err += f"\n\tRegistered objects: {len(self._custom_objects)}\n"
            err += "Please make sure to only load checkpoints from folders that were created with the same set of registered objects,"
            err += "or avoid using `custom_checkpoint` in the filename for files in that same directory and load them in manually."
            raise RuntimeError(err)
        else:
            for index, obj in enumerate(self._custom_objects): load_custom_state(obj, input_dir, index)
    def free_memory(self, *objects):
        if hasattr(self, "deepspeed_engine_wrapped"):
            if self.deepspeed_engine_wrapped is not None: self.deepspeed_engine_wrapped.engine.destroy()
            self.deepspeed_engine_wrapped = None
        objects = release_memory(*objects)
        self._schedulers = []
        self._optimizers = []
        self._models = []
        self._dataloaders = []
        self.step = 0
        return objects
    def clear(self, *objects): return self.free_memory(*objects)
    def _get_named_parameters(self, *args):
        named_parameters = {}
        for obj in args:
            if isinstance(obj, torch.nn.Module):
                obj = extract_model_from_parallel(obj)
                named_parameters.update({n: p for n, p in obj.named_parameters()})
        return named_parameters
    def _get_devices(self, *args):
        model_device = None
        optimizer_device = None
        for obj in args:
            if isinstance(obj, torch.nn.Module):
                for param in obj.parameters():
                    model_device = param.device
                    break
            if isinstance(obj, torch.optim.Optimizer):
                for param_group in obj.param_groups:
                    if len(param_group["params"]) > 0:
                        optimizer_device = param_group["params"][0].device
                        break
        return (model_device, optimizer_device)
    def get_state_dict(self, model, unwrap=True):
        if self.distributed_type == DistributedType.DEEPSPEED:
            if self.deepspeed_config["zero_optimization"]["stage"] == 3:
                if model.zero_gather_16bit_weights_on_model_save(): state_dict = model._zero3_consolidated_16bit_state_dict()
                else: raise ValueError("Cannot get 16bit model weights because `stage3_gather_16bit_weights_on_model_save` in DeepSpeed config is False. To save the model weights in 16bit, set `stage3_gather_16bit_weights_on_model_save` to True in DeepSpeed config file or set `zero3_save_16bit_model` to True when using `sapiens_accelerator config`. To save the full checkpoint, run `model.save_checkpoint(save_dir)` and use `zero_to_fp32.py` to recover weights.")
            else:
                from deepspeed.checkpoint.utils import clone_tensors_for_torch_save
                state_dict = clone_tensors_for_torch_save(self.unwrap_model(model).state_dict())
        elif self.distributed_type == DistributedType.FSDP:
            from torch.distributed.fsdp import FullStateDictConfig, StateDictType
            from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
            full_state_dict_config = FullStateDictConfig(offload_to_cpu=True, rank0_only=True)
            with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT, full_state_dict_config): state_dict = model.state_dict()
        else:
            if unwrap: model = self.unwrap_model(model)
            state_dict = model.state_dict()
        return state_dict
    def register_for_checkpointing(self, *objects):
        invalid_objects = []
        for obj in objects:
            if not hasattr(obj, "state_dict") or not hasattr(obj, "load_state_dict"): invalid_objects.append(obj)
        if len(invalid_objects) > 0:
            err = "All `objects` must include a `state_dict` and `load_state_dict` function to be stored. The following inputs are invalid:"
            for index, obj in enumerate(invalid_objects): err += f"\n\t- Item at index {index}, `{get_pretty_name(obj)}`"
            raise ValueError(err)
        self._custom_objects.extend(objects)
    @contextmanager
    def autocast(self, autocast_handler: AutocastKwargs = None):
        if autocast_handler is None: autocast_handler = self.autocast_handler
        autocast_context = get_mixed_precision_context_manager(self.native_amp, autocast_handler)
        autocast_context.__enter__()
        yield
        autocast_context.__exit__(*sys.exc_info())
    @contextmanager
    def profile(self, profile_handler: ProfileKwargs | None = None):
        profile_handler = profile_handler or self.profile_handler or ProfileKwargs()
        with profile_handler.build() as profiler: yield profiler
        if profile_handler.output_trace_dir is None: return
        os.makedirs(profile_handler.output_trace_dir, exist_ok=True)
        profiler.export_chrome_trace(os.path.join(profile_handler.output_trace_dir, PROFILE_PATTERN_NAME.format(suffix=self.process_index)))
        self.wait_for_everyone()
    @property
    def optimizer_step_was_skipped(self):
        for optimizer in self._optimizers:
            if optimizer.step_was_skipped: return True
        return False
    def skip_first_batches(self, dataloader, num_batches: int = 0): return skip_first_batches(dataloader, num_batches=num_batches)
    def __deepcopy__(self, memo): return self
    def verify_device_map(self, model: torch.nn.Module) -> bool:
        for m in model.modules():
            if hasattr(m, "hf_device_map") and len(m.hf_device_map) > 1: return True
        return False
    def lomo_backward(self, loss: torch.Tensor, learning_rate: float) -> None:
        if is_lomo_available(): from lomo_optim import AdaLomo, Lomo
        if learning_rate is None: raise ValueError("A learning rate must be passed in order to call backward pass with LOMO optimizers.")
        _backward_called = False
        for optimizer in self._optimizers:
            if isinstance(optimizer.optimizer, (Lomo, AdaLomo)):
                optimizer.optimizer.fused_backward(loss, learning_rate)
                _backward_called = True
        if not _backward_called: raise ValueError("Backward pass not properly called on LOMO optimizers. Are you sure you passed a LOMO optimizer in accelerator.prepare()?")
    @property
    def fp8_backend(self):
        if self.mixed_precision == "fp8" and self.fp8_recipe_handler is not None: return self.fp8_recipe_handler.backend
        elif self.state.deepspeed_plugin is not None and self.state.deepspeed_plugin.enable_msamp: return "MSAMP"
        return None
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
