"""
	########################################################################################################################################################
	# This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
__version__ = "1.0.0"
from .accelerator import Accelerator
from .big_modeling import (cpu_offload, cpu_offload_with_hook, disk_offload, dispatch_model, init_empty_weights, init_on_device, load_checkpoint_and_dispatch)
from .data_loader import skip_first_batches
from .inference import prepare_pippy
from .launchers import debug_launcher, notebook_launcher
from .state import PartialState
from .utils import (AutocastKwargs, DataLoaderConfiguration, DDPCommunicationHookType, DeepSpeedPlugin, DistributedDataParallelKwargs, DistributedType,
FullyShardedDataParallelPlugin, GradScalerKwargs, InitProcessGroupKwargs, ProfileKwargs, find_executable_batch_size, infer_auto_device_map, is_rich_available,
load_checkpoint_in_model, synchronize_rng_states)
if is_rich_available(): from .utils import rich
"""
	########################################################################################################################################################
	# This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
