"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import random
from typing import List, Optional, Union
import numpy as np
import torch
from ..state import AcceleratorState
from .constants import CUDA_DISTRIBUTED_TYPES
from .dataclasses import DistributedType, RNGType
from .imports import is_mlu_available, is_musa_available, is_npu_available, is_torch_xla_available, is_xpu_available
if is_torch_xla_available(): import torch_xla.core.xla_model as xm
def set_seed(seed: int, device_specific: bool = False, deterministic: bool = False):
    if device_specific: seed += AcceleratorState().process_index
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if is_xpu_available(): torch.xpu.manual_seed_all(seed)
    elif is_npu_available(): torch.npu.manual_seed_all(seed)
    elif is_mlu_available(): torch.mlu.manual_seed_all(seed)
    elif is_musa_available(): torch.musa.manual_seed_all(seed)
    else: torch.cuda.manual_seed_all(seed)
    if is_torch_xla_available(): xm.set_rng_state(seed)
    if deterministic: torch.use_deterministic_algorithms(True)
def synchronize_rng_state(rng_type: Optional[RNGType] = None, generator: Optional[torch.Generator] = None):
    if rng_type == RNGType.TORCH: rng_state = torch.get_rng_state()
    elif rng_type == RNGType.CUDA: rng_state = torch.cuda.get_rng_state()
    elif rng_type == RNGType.XLA:
        assert is_torch_xla_available(), "Can't synchronize XLA seeds as torch_xla is unavailable."
        rng_state = torch.tensor(xm.get_rng_state())
    elif rng_type == RNGType.NPU:
        assert is_npu_available(), "Can't synchronize NPU seeds on an environment without NPUs."
        rng_state = torch.npu.get_rng_state()
    elif rng_type == RNGType.MLU:
        assert is_mlu_available(), "Can't synchronize MLU seeds on an environment without MLUs."
        rng_state = torch.mlu.get_rng_state()
    elif rng_type == RNGType.MUSA:
        assert is_musa_available(), "Can't synchronize MUSA seeds on an environment without MUSAs."
        rng_state = torch.musa.get_rng_state()
    elif rng_type == RNGType.XPU:
        assert is_xpu_available(), "Can't synchronize XPU seeds on an environment without XPUs."
        rng_state = torch.xpu.get_rng_state()
    elif rng_type == RNGType.GENERATOR:
        assert generator is not None, "Need a generator to synchronize its seed."
        rng_state = generator.get_state()
    state = AcceleratorState()
    if state.distributed_type == DistributedType.XLA:
        rng_state = rng_state.to(xm.xla_device())
        xm.collective_broadcast([rng_state])
        xm.mark_step()
        rng_state = rng_state.cpu()
    elif (state.distributed_type in CUDA_DISTRIBUTED_TYPES or state.distributed_type == DistributedType.MULTI_MLU or state.distributed_type == DistributedType.MULTI_MUSA
    or state.distributed_type == DistributedType.MULTI_NPU or state.distributed_type == DistributedType.MULTI_XPU):
        rng_state = rng_state.to(state.device)
        torch.distributed.broadcast(rng_state, 0)
        rng_state = rng_state.cpu()
    elif state.distributed_type == DistributedType.MULTI_CPU: torch.distributed.broadcast(rng_state, 0)
    if rng_type == RNGType.TORCH: torch.set_rng_state(rng_state)
    elif rng_type == RNGType.CUDA: torch.cuda.set_rng_state(rng_state)
    elif rng_type == RNGType.NPU: torch.npu.set_rng_state(rng_state)
    elif rng_type == RNGType.MLU: torch.mlu.set_rng_state(rng_state)
    elif rng_type == RNGType.MUSA: torch.musa.set_rng_state(rng_state)
    elif rng_type == RNGType.XPU: torch.xpu.set_rng_state(rng_state)
    elif rng_type == RNGType.XLA: xm.set_rng_state(rng_state.item())
    elif rng_type == RNGType.GENERATOR: generator.set_state(rng_state)
def synchronize_rng_states(rng_types: List[Union[str, RNGType]], generator: Optional[torch.Generator] = None):
    for rng_type in rng_types: synchronize_rng_state(RNGType(rng_type), generator=generator)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
