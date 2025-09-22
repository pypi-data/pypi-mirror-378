"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import importlib.metadata
from typing import Union
from packaging.version import Version, parse
from .constants import STR_OPERATION_TO_FUNC
torch_version = parse(importlib.metadata.version("torch"))
def compare_versions(library_or_version: Union[str, Version], operation: str, requirement_version: str):
    if operation not in STR_OPERATION_TO_FUNC.keys(): raise ValueError(f"`operation` must be one of {list(STR_OPERATION_TO_FUNC.keys())}, received {operation}")
    operation = STR_OPERATION_TO_FUNC[operation]
    if isinstance(library_or_version, str): library_or_version = parse(importlib.metadata.version(library_or_version))
    return operation(library_or_version, parse(requirement_version))
def is_torch_version(operation: str, version: str): return compare_versions(torch_version, operation, version)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
