"""
	########################################################################################################################################################
	# This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
from .testing import (DEFAULT_LAUNCH_COMMAND, are_the_same_tensors, assert_exception, capture_call_output, device_count, execute_subprocess_async,
get_launch_command, memory_allocated_func, path_in_sapiens_accelerator_package, require_sapiens, require_cpu, require_cuda, require_huggingface_suite, require_mlu,
require_mps, require_multi_device, require_multi_gpu, require_multi_xpu, require_musa, require_non_cpu, require_non_torch_xla, require_non_xpu, require_npu,
require_pippy, require_single_device, require_single_gpu, require_single_xpu, require_torch_min_version, require_torchvision, require_tpu, require_transformer_engine,
require_xpu, skip, slow, torch_device)
from .training import RegressionDataset, RegressionModel, RegressionModel4XPU
from .scripts import test_script, test_sync, test_ops
"""
	########################################################################################################################################################
	# This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
	# or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
	########################################################################################################################################################
"""
