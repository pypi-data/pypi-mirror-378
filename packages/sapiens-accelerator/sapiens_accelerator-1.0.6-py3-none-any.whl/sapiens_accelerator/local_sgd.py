"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import torch
from sapiens_accelerator import Accelerator, DistributedType
class LocalSGD:
    def __enter__(self):
        if self.enabled:
            self.model_sync_obj = self.model.no_sync()
            self.model_sync_obj.__enter__()
        return self
    def __exit__(self, type, value, tb):
        if self.enabled:
            self._sync_and_avg_model_params()
            self.model_sync_obj.__exit__(type, value, tb)
    def __init__(self, accelerator: Accelerator, model: torch.nn.Module, local_sgd_steps: int, enabled: bool = True):
        if accelerator.distributed_type not in [DistributedType.NO, DistributedType.MULTI_CPU, DistributedType.MULTI_GPU, DistributedType.MULTI_MLU,
        DistributedType.MULTI_MUSA, DistributedType.MULTI_NPU]: raise NotImplementedError("LocalSGD is supported only for CPUs and GPUs (no DeepSpeed or MegatronLM)")
        self.enabled = enabled and accelerator.distributed_type != DistributedType.NO
        self.num_steps = 0
        if self.enabled:
            self.accelerator = accelerator
            self.model = model
            self.local_sgd_steps = local_sgd_steps
    def step(self):
        self.num_steps += 1
        if not self.enabled: return
        if self.num_steps % self.local_sgd_steps == 0: self._sync_and_avg_model_params()
    def _sync_and_avg_model_params(self):
        self.accelerator.wait_for_everyone()
        with self.accelerator.autocast():
            for param in self.model.parameters(): param.data = self.accelerator.reduce(param.data, reduction="mean")
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
