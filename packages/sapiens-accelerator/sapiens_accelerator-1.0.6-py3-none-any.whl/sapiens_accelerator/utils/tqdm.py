"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from .imports import is_tqdm_available
if is_tqdm_available(): from tqdm.auto import tqdm as _tqdm
from ..state import PartialState
def tqdm(*args, main_process_only: bool = True, **kwargs):
    if not is_tqdm_available(): raise ImportError("SapiensAccelerator's `tqdm` module requires `tqdm` to be installed. Please run `pip install tqdm`.")
    if len(args) > 0 and isinstance(args[0], bool): raise ValueError("Passing `True` or `False` as the first argument to SapiensAccelerator's `tqdm` wrapper is unsupported. Please use the `main_process_only` keyword argument instead.")
    disable = kwargs.pop("disable", False)
    if main_process_only and not disable: disable = PartialState().local_process_index != 0
    return _tqdm(*args, **kwargs, disable=disable)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
