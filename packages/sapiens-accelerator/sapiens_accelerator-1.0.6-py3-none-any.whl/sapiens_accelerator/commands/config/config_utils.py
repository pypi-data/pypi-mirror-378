"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
from ...utils.dataclasses import (ComputeEnvironment, DistributedType, DynamoBackend, FP8BackendType, PrecisionType, SageMakerDistributedType)
from ..menu import BulletMenu
DYNAMO_BACKENDS = ["EAGER", "AOT_EAGER", "INDUCTOR", "AOT_TS_NVFUSER", "NVPRIMS_NVFUSER", "CUDAGRAPHS", "OFI", "FX2TRT", "ONNXRT", "TENSORRT",
"AOT_TORCHXLA_TRACE_ONCE", "TORHCHXLA_TRACE_ONCE", "IPEX", "TVM"]
def _ask_field(input_text, convert_value=None, default=None, error_message=None):
    ask_again = True
    while ask_again:
        result = input(input_text)
        try:
            if default is not None and len(result) == 0: return default
            return convert_value(result) if convert_value is not None else result
        except Exception: pass
def _ask_options(input_text, options=[], convert_value=None, default=0):
    menu = BulletMenu(input_text, options)
    result = menu.run(default_choice=default)
    return convert_value(result) if convert_value is not None else result
def _convert_compute_environment(value):
    value = int(value)
    return ComputeEnvironment(["LOCAL_MACHINE", "AMAZON_SAGEMAKER"][value])
def _convert_distributed_mode(value):
    value = int(value)
    return DistributedType(["NO", "MULTI_CPU", "MULTI_XPU", "MULTI_GPU", "MULTI_NPU", "MULTI_MLU", "MULTI_MUSA", "XLA"][value])
def _convert_dynamo_backend(value):
    value = int(value)
    return DynamoBackend(DYNAMO_BACKENDS[value]).value
def _convert_mixed_precision(value):
    value = int(value)
    return PrecisionType(["no", "fp16", "bf16", "fp8"][value])
def _convert_sagemaker_distributed_mode(value):
    value = int(value)
    return SageMakerDistributedType(["NO", "DATA_PARALLEL", "MODEL_PARALLEL"][value])
def _convert_fp8_backend(value):
    value = int(value)
    return FP8BackendType(["TE", "MSAMP"][value])
def _convert_yes_no_to_bool(value): return {"yes": True, "no": False}[value.lower()]
class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        usage = super()._format_usage(usage, actions, groups, prefix)
        usage = usage.replace("<command> [<args>] ", "")
        return usage
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
