"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import os
import shutil
from pathlib import Path
import torch
from ..logging import get_logger
from .constants import FSDP_MODEL_NAME, OPTIMIZER_NAME, SAFE_WEIGHTS_NAME, WEIGHTS_NAME
from .modeling import is_peft_model
from .other import save
from .versions import is_torch_version
logger = get_logger(__name__)
def enable_fsdp_ram_efficient_loading():
    if "SAPIENS_ACCELERATOR_USE_FSDP" not in os.environ: os.environ["SAPIENS_ACCELERATOR_USE_FSDP"] = "True"
    os.environ["FSDP_CPU_RAM_EFFICIENT_LOADING"] = "True"
def disable_fsdp_ram_efficient_loading(): os.environ["FSDP_CPU_RAM_EFFICIENT_LOADING"] = "False"
def _get_model_state_dict(model, adapter_only=False):
    if adapter_only and is_peft_model(model):
        from peft import get_peft_model_state_dict
        return get_peft_model_state_dict(model, adapter_name=model.active_adapter)
    else: return model.state_dict()
def _set_model_state_dict(model, state_dict, adapter_only=False):
    if adapter_only and is_peft_model(model):
        from peft import set_peft_model_state_dict
        return set_peft_model_state_dict(model, state_dict, adapter_name=model.active_adapter)
    else: return model.load_state_dict(state_dict)
def save_fsdp_model(fsdp_plugin, accelerator, model, output_dir, model_index=0, adapter_only=False):
    import torch.distributed.checkpoint as dist_cp
    from torch.distributed.checkpoint.default_planner import DefaultSavePlanner
    from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp.fully_sharded_data_parallel import StateDictType
    os.makedirs(output_dir, exist_ok=True)
    if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
        is_multi_process = accelerator.num_processes > 1
        fsdp_plugin.state_dict_config.offload_to_cpu = is_multi_process
        fsdp_plugin.state_dict_config.rank0_only = is_multi_process
    with FSDP.state_dict_type(model, fsdp_plugin.state_dict_type, fsdp_plugin.state_dict_config, fsdp_plugin.optim_state_dict_config):
        state_dict = _get_model_state_dict(model, adapter_only=adapter_only)
        if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
            weights_name = f"{FSDP_MODEL_NAME}.bin" if model_index == 0 else f"{FSDP_MODEL_NAME}_{model_index}.bin"
            output_model_file = os.path.join(output_dir, weights_name)
            if accelerator.process_index == 0: torch.save(state_dict, output_model_file)
        elif fsdp_plugin.state_dict_type == StateDictType.LOCAL_STATE_DICT:
            weights_name = (f"{FSDP_MODEL_NAME}_rank{accelerator.process_index}.bin" if model_index == 0 else f"{FSDP_MODEL_NAME}_{model_index}_rank{accelerator.process_index}.bin")
            output_model_file = os.path.join(output_dir, weights_name)
            torch.save(state_dict, output_model_file)
        elif fsdp_plugin.state_dict_type == StateDictType.SHARDED_STATE_DICT:
            ckpt_dir = os.path.join(output_dir, f"{FSDP_MODEL_NAME}_{model_index}")
            os.makedirs(ckpt_dir, exist_ok=True)
            state_dict = {"model": state_dict}
            dist_cp.save_state_dict(state_dict=state_dict, storage_writer=dist_cp.FileSystemWriter(ckpt_dir), planner=DefaultSavePlanner())
def load_fsdp_model(fsdp_plugin, accelerator, model, input_dir, model_index=0, adapter_only=False):
    import torch.distributed.checkpoint as dist_cp
    from torch.distributed.checkpoint.default_planner import DefaultLoadPlanner
    from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp.fully_sharded_data_parallel import StateDictType
    accelerator.wait_for_everyone()
    if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
        is_multi_process = accelerator.num_processes > 1
        fsdp_plugin.state_dict_config.offload_to_cpu = is_multi_process
        fsdp_plugin.state_dict_config.rank0_only = is_multi_process
    with FSDP.state_dict_type(model, fsdp_plugin.state_dict_type, fsdp_plugin.state_dict_config, fsdp_plugin.optim_state_dict_config):
        if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
            if type(model) is not FSDP and accelerator.process_index != 0:
                if not fsdp_plugin.sync_module_states: raise ValueError("Set the `sync_module_states` flag to `True` so that model states are synced across processes when initializing FSDP object")
                return
            weights_name = f"{FSDP_MODEL_NAME}.bin" if model_index == 0 else f"{FSDP_MODEL_NAME}_{model_index}.bin"
            input_model_file = os.path.join(input_dir, weights_name)
            state_dict = torch.load(input_model_file)
        elif fsdp_plugin.state_dict_type == StateDictType.LOCAL_STATE_DICT:
            weights_name = (f"{FSDP_MODEL_NAME}_rank{accelerator.process_index}.bin" if model_index == 0 else f"{FSDP_MODEL_NAME}_{model_index}_rank{accelerator.process_index}.bin")
            input_model_file = os.path.join(input_dir, weights_name)
            state_dict = torch.load(input_model_file)
        elif fsdp_plugin.state_dict_type == StateDictType.SHARDED_STATE_DICT:
            ckpt_dir = (os.path.join(input_dir, f"{FSDP_MODEL_NAME}_{model_index}") if f"{FSDP_MODEL_NAME}" not in input_dir else input_dir)
            state_dict = {"model": _get_model_state_dict(model, adapter_only=adapter_only)}
            dist_cp.load_state_dict(state_dict=state_dict, storage_reader=dist_cp.FileSystemReader(ckpt_dir), planner=DefaultLoadPlanner())
            state_dict = state_dict["model"]
        load_result = _set_model_state_dict(model, state_dict, adapter_only=adapter_only)
    return load_result
def save_fsdp_optimizer(fsdp_plugin, accelerator, optimizer, model, output_dir, optimizer_index=0):
    import torch.distributed.checkpoint as dist_cp
    from torch.distributed.checkpoint.default_planner import DefaultSavePlanner
    from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp.fully_sharded_data_parallel import StateDictType
    os.makedirs(output_dir, exist_ok=True)
    with FSDP.state_dict_type(model, fsdp_plugin.state_dict_type, fsdp_plugin.state_dict_config, fsdp_plugin.optim_state_dict_config):
        optim_state = FSDP.optim_state_dict(model, optimizer)
        if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
            if accelerator.process_index == 0:
                optim_state_name = (f"{OPTIMIZER_NAME}.bin" if optimizer_index == 0 else f"{OPTIMIZER_NAME}_{optimizer_index}.bin")
                output_optimizer_file = os.path.join(output_dir, optim_state_name)
                torch.save(optim_state, output_optimizer_file)
        else:
            ckpt_dir = os.path.join(output_dir, f"{OPTIMIZER_NAME}_{optimizer_index}")
            os.makedirs(ckpt_dir, exist_ok=True)
            dist_cp.save_state_dict(state_dict={"optimizer": optim_state}, storage_writer=dist_cp.FileSystemWriter(ckpt_dir), planner=DefaultSavePlanner())
def load_fsdp_optimizer(fsdp_plugin, accelerator, optimizer, model, input_dir, optimizer_index=0, adapter_only=False):
    import torch.distributed.checkpoint as dist_cp
    from torch.distributed.checkpoint.optimizer import load_sharded_optimizer_state_dict
    from torch.distributed.fsdp.fully_sharded_data_parallel import FullyShardedDataParallel as FSDP
    from torch.distributed.fsdp.fully_sharded_data_parallel import StateDictType
    accelerator.wait_for_everyone()
    with FSDP.state_dict_type(model, fsdp_plugin.state_dict_type, fsdp_plugin.state_dict_config, fsdp_plugin.optim_state_dict_config):
        if fsdp_plugin.state_dict_type == StateDictType.FULL_STATE_DICT:
            optim_state = None
            if accelerator.process_index == 0 or not fsdp_plugin.optim_state_dict_config.rank0_only:
                optimizer_name = (f"{OPTIMIZER_NAME}.bin" if optimizer_index == 0 else f"{OPTIMIZER_NAME}_{optimizer_index}.bin")
                input_optimizer_file = os.path.join(input_dir, optimizer_name)
                optim_state = torch.load(input_optimizer_file)
        else:
            ckpt_dir = (os.path.join(input_dir, f"{OPTIMIZER_NAME}_{optimizer_index}") if f"{OPTIMIZER_NAME}" not in input_dir else input_dir)
            optim_state = load_sharded_optimizer_state_dict(model_state_dict=_get_model_state_dict(model, adapter_only=adapter_only), optimizer_key="optimizer", storage_reader=dist_cp.FileSystemReader(ckpt_dir))
            optim_state = optim_state["optimizer"]
        flattened_osd = FSDP.optim_state_dict_to_load(model=model, optim=optimizer, optim_state_dict=optim_state)
        optimizer.load_state_dict(flattened_osd)
def _distributed_checkpoint_to_merged_weights(checkpoint_dir: str, save_path: str, safe_serialization: bool = True):
    import torch.distributed.checkpoint as dist_cp
    import torch.distributed.checkpoint.format_utils as dist_cp_format_utils
    state_dict = {}
    save_path = Path(save_path)
    save_path.mkdir(exist_ok=True)
    dist_cp_format_utils._load_state_dict(state_dict, storage_reader=dist_cp.FileSystemReader(checkpoint_dir), planner=dist_cp_format_utils._EmptyStateDictLoadPlanner(), no_dist=True)
    save_path = save_path / SAFE_WEIGHTS_NAME if safe_serialization else save_path / WEIGHTS_NAME
    if len(state_dict.keys()) == 1: state_dict = state_dict[list(state_dict)[0]]
    save(state_dict, save_path, safe_serialization=safe_serialization)
    return save_path
def merge_fsdp_weights(checkpoint_dir: str, output_path: str, safe_serialization: bool = True, remove_checkpoint_dir: bool = False):
    checkpoint_dir = Path(checkpoint_dir)
    from sapiens_accelerator.state import PartialState
    if not is_torch_version(">=", "2.3.0"): raise ValueError("`merge_fsdp_weights` requires PyTorch >= 2.3.0`")
    if not checkpoint_dir.exists():
        model_path_exists = (checkpoint_dir / "pytorch_model_fsdp_0").exists()
        optimizer_path_exists = (checkpoint_dir / "optimizer_0").exists()
        err = f"Tried to load from {checkpoint_dir} but couldn't find a valid metadata file."
        if model_path_exists and optimizer_path_exists:
            err += " However, potential model and optimizer checkpoint directories exist."
            err += f"Please pass in either {checkpoint_dir}/pytorch_model_fsdp_0 or {checkpoint_dir}/optimizer_0"
            err += "instead."
        elif model_path_exists:
            err += " However, a potential model checkpoint directory exists."
            err += f"Please try passing in {checkpoint_dir}/pytorch_model_fsdp_0 instead."
        elif optimizer_path_exists:
            err += " However, a potential optimizer checkpoint directory exists."
            err += f"Please try passing in {checkpoint_dir}/optimizer_0 instead."
        raise ValueError(err)
    state = PartialState()
    if state.is_main_process:
        save_path = _distributed_checkpoint_to_merged_weights(checkpoint_dir, output_path, safe_serialization)
        if remove_checkpoint_dir: shutil.rmtree(checkpoint_dir)
    state.wait_for_everyone()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
