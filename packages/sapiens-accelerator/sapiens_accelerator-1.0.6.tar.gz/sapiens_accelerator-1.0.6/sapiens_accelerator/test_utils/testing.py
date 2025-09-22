"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import asyncio
import inspect
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import List, Union
from unittest import mock
import torch
import sapiens_accelerator
from ..state import AcceleratorState, PartialState
from ..utils import (gather, is_sapiens_available, is_clearml_available, is_comet_ml_available, is_cuda_available, is_datasets_available, is_deepspeed_available,
is_dvclive_available, is_import_timer_available, is_mlu_available, is_mps_available, is_musa_available, is_npu_available, is_pandas_available, is_pippy_available,
is_schedulefree_available, is_tensorboard_available, is_timm_available, is_torch_version, is_torch_xla_available, is_torchdata_stateful_dataloader_available,
is_torchvision_available, is_transformer_engine_available, is_transformers_available, is_triton_available, is_wandb_available, is_xpu_available, str_to_bool)
def get_backend():
    if is_torch_xla_available(): return "xla", torch.cuda.device_count(), torch.cuda.memory_allocated
    elif is_cuda_available(): return "cuda", torch.cuda.device_count(), torch.cuda.memory_allocated
    elif is_mps_available(min_version="2.0"): return "mps", 1, torch.mps.current_allocated_memory
    elif is_mps_available(): return "mps", 1, lambda: 0
    elif is_mlu_available(): return "mlu", torch.mlu.device_count(), torch.mlu.memory_allocated
    elif is_musa_available(): return "musa", torch.musa.device_count(), torch.musa.memory_allocated
    elif is_npu_available(): return "npu", torch.npu.device_count(), torch.npu.memory_allocated
    elif is_xpu_available(): return "xpu", torch.xpu.device_count(), torch.xpu.memory_allocated
    else: return "cpu", 1, lambda: 0
torch_device, device_count, memory_allocated_func = get_backend()
def get_launch_command(**kwargs) -> list:
    command = ["sapiens_accelerator", "launch"]
    for k, v in kwargs.items():
        if isinstance(v, bool) and v: command.append(f"--{k}")
        elif v is not None: command.append(f"--{k}={v}")
    return command
DEFAULT_LAUNCH_COMMAND = get_launch_command(num_processes=device_count, monitor_interval=0.1)
def parse_flag_from_env(key, default=False):
    try: value = os.environ[key]
    except KeyError: _value = default
    else:
        try: _value = str_to_bool(value)
        except ValueError: raise ValueError(f"If set, {key} must be yes or no.")
    return _value
_run_slow_tests = parse_flag_from_env("RUN_SLOW", default=False)
def skip(test_case): return unittest.skip("Test was skipped")(test_case)
def slow(test_case): return unittest.skipUnless(_run_slow_tests, "test is slow")(test_case)
def require_cpu(test_case): return unittest.skipUnless(torch_device == "cpu", "test requires only a CPU")(test_case)
def require_non_cpu(test_case): return unittest.skipUnless(torch_device != "cpu", "test requires a GPU")(test_case)
def require_cuda(test_case): return unittest.skipUnless(is_cuda_available() and not is_torch_xla_available(), "test requires a GPU")(test_case)
def require_xpu(test_case): return unittest.skipUnless(is_xpu_available(), "test requires a XPU")(test_case)
def require_non_xpu(test_case): return unittest.skipUnless(torch_device != "xpu", "test requires a non-XPU")(test_case)
def require_mlu(test_case): return unittest.skipUnless(is_mlu_available(), "test require a MLU")(test_case)
def require_musa(test_case): return unittest.skipUnless(is_musa_available(), "test require a MUSA")(test_case)
def require_npu(test_case): return unittest.skipUnless(is_npu_available(), "test require a NPU")(test_case)
def require_mps(test_case): return unittest.skipUnless(is_mps_available(), "test requires a `mps` backend support in `torch`")(test_case)
def require_huggingface_suite(test_case): return unittest.skipUnless(is_transformers_available() and is_datasets_available(), "test requires the HF suite")(test_case)
def require_transformers(test_case): return unittest.skipUnless(is_transformers_available(), "test requires the transformers library")(test_case)
def require_timm(test_case): return unittest.skipUnless(is_timm_available(), "test requires the timm library")(test_case)
def require_torchvision(test_case): return unittest.skipUnless(is_torchvision_available(), "test requires the torchvision library")(test_case)
def require_triton(test_case): return unittest.skipUnless(is_triton_available(), "test requires the triton library")(test_case)
def require_schedulefree(test_case): return unittest.skipUnless(is_schedulefree_available(), "test requires the schedulefree library")(test_case)
def require_sapiens(test_case): return unittest.skipUnless(is_sapiens_available(), "test requires the sapiens_machine library")(test_case)
def require_tpu(test_case): return unittest.skipUnless(is_torch_xla_available(check_is_tpu=True), "test requires TPU")(test_case)
def require_non_torch_xla(test_case): return unittest.skipUnless(not is_torch_xla_available(), "test requires an env without TorchXLA")(test_case)
def require_single_device(test_case): return unittest.skipUnless(torch_device != "cpu" and device_count == 1, "test requires a hardware accelerator")(test_case)
def require_single_gpu(test_case): return unittest.skipUnless(torch.cuda.device_count() == 1, "test requires a GPU")(test_case)
def require_single_xpu(test_case): return unittest.skipUnless(torch.xpu.device_count() == 1, "test requires a XPU")(test_case)
def require_multi_device(test_case): return unittest.skipUnless(device_count > 1, "test requires multiple hardware accelerators")(test_case)
def require_multi_gpu(test_case): return unittest.skipUnless(torch.cuda.device_count() > 1, "test requires multiple GPUs")(test_case)
def require_multi_xpu(test_case): return unittest.skipUnless(torch.xpu.device_count() > 1, "test requires multiple XPUs")(test_case)
def require_deepspeed(test_case): return unittest.skipUnless(is_deepspeed_available(), "test requires DeepSpeed")(test_case)
def require_fsdp(test_case): return unittest.skipUnless(is_torch_version(">=", "1.12.0"), "test requires torch version >= 1.12.0")(test_case)
def require_torch_min_version(test_case=None, version=None):
    if test_case is None: return partial(require_torch_min_version, version=version)
    return unittest.skipUnless(is_torch_version(">=", version), f"test requires torch version >= {version}")(test_case)
def require_tensorboard(test_case): return unittest.skipUnless(is_tensorboard_available(), "test requires Tensorboard")(test_case)
def require_wandb(test_case): return unittest.skipUnless(is_wandb_available(), "test requires wandb")(test_case)
def require_comet_ml(test_case): return unittest.skipUnless(is_comet_ml_available(), "test requires comet_ml")(test_case)
def require_clearml(test_case): return unittest.skipUnless(is_clearml_available(), "test requires clearml")(test_case)
def require_dvclive(test_case): return unittest.skipUnless(is_dvclive_available(), "test requires dvclive")(test_case)
def require_pandas(test_case): return unittest.skipUnless(is_pandas_available(), "test requires pandas")(test_case)
def require_pippy(test_case): return unittest.skipUnless(is_pippy_available(), "test requires pippy")(test_case)
def require_import_timer(test_case): return unittest.skipUnless(is_import_timer_available(), "test requires tuna interpreter")(test_case)
def require_transformer_engine(test_case): return unittest.skipUnless(is_transformer_engine_available(), "test requires transformers engine")(test_case)
_atleast_one_tracker_available = (any([is_wandb_available(), is_tensorboard_available()]) and not is_comet_ml_available())
def require_trackers(test_case): return unittest.skipUnless(_atleast_one_tracker_available, "test requires at least one tracker to be available and for `comet_ml` to not be installed")(test_case)
def require_torchdata_stateful_dataloader(test_case): return unittest.skipUnless(is_torchdata_stateful_dataloader_available(), "test requires torchdata.stateful_dataloader")(test_case)
class TempDirTestCase(unittest.TestCase):
    clear_on_setup = True
    @classmethod
    def setUpClass(cls): cls.tmpdir = Path(tempfile.mkdtemp())
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.tmpdir): shutil.rmtree(cls.tmpdir)
    def setUp(self):
        if self.clear_on_setup:
            for path in self.tmpdir.glob("**/*"):
                if path.is_file(): path.unlink()
                elif path.is_dir(): shutil.rmtree(path)
class SapiensAcceleratorTestCase(unittest.TestCase):
    def tearDown(self):
        super().tearDown()
        AcceleratorState._reset_state()
        PartialState._reset_state()
class MockingTestCase(unittest.TestCase):
    def add_mocks(self, mocks: Union[mock.Mock, List[mock.Mock]]):
        self.mocks = mocks if isinstance(mocks, (tuple, list)) else [mocks]
        for m in self.mocks:
            m.start()
            self.addCleanup(m.stop)
def are_the_same_tensors(tensor):
    state = AcceleratorState()
    tensor = tensor[None].clone().to(state.device)
    tensors = gather(tensor).cpu()
    tensor = tensor[0].cpu()
    for i in range(tensors.shape[0]):
        if not torch.equal(tensors[i], tensor): return False
    return True
class _RunOutput:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line: callback(line)
        else: break
async def _stream_subprocess(cmd, env=None, stdin=None, timeout=None, quiet=False, echo=False) -> _RunOutput:
    if echo: print("\nRunning: ", " ".join(cmd))
    p = await asyncio.create_subprocess_exec(cmd[0], *cmd[1:], stdin=stdin, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
    out = []
    err = []
    def tee(line, sink, pipe, label=""):
        line = line.decode("utf-8").rstrip()
        sink.append(line)
        if not quiet: print(label, line, file=pipe)
    await asyncio.wait([asyncio.create_task(_read_stream(p.stdout, lambda l: tee(l, out, sys.stdout, label="stdout:"))), asyncio.create_task(_read_stream(p.stderr, lambda l: tee(l, err, sys.stderr, label="stderr:")))], timeout=timeout)
    return _RunOutput(await p.wait(), out, err)
def execute_subprocess_async(cmd: list, env=None, stdin=None, timeout=180, quiet=False, echo=True) -> _RunOutput:
    for i, c in enumerate(cmd):
        if isinstance(c, Path): cmd[i] = str(c)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_stream_subprocess(cmd, env=env, stdin=stdin, timeout=timeout, quiet=quiet, echo=echo))
    cmd_str = " ".join(cmd)
    if result.returncode > 0:
        stderr = "\n".join(result.stderr)
        raise RuntimeError(f"'{cmd_str}' failed with returncode {result.returncode}\n\nThe combined stderr from workers follows:\n{stderr}")
    return result
class SubprocessCallException(Exception): pass
def run_command(command: List[str], return_stdout=False, env=None):
    for i, c in enumerate(command):
        if isinstance(c, Path): command[i] = str(c)
    if env is None: env = os.environ.copy()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, env=env)
        if return_stdout:
            if hasattr(output, "decode"): output = output.decode("utf-8")
            return output
    except subprocess.CalledProcessError as e: raise SubprocessCallException(f"Command `{' '.join(command)}` failed with the following error:\n\n{e.output.decode()}") from e
def path_in_sapiens_accelerator_package(*components: str) -> Path:
    sapiens_accelerator_package_dir = Path(inspect.getfile(sapiens_accelerator)).parent
    return sapiens_accelerator_package_dir.joinpath(*components)
@contextmanager
def assert_exception(exception_class: Exception, msg: str = None) -> bool:
    was_ran = False
    try:
        yield
        was_ran = True
    except Exception as e:
        assert isinstance(e, exception_class), f"Expected exception of type {exception_class} but got {type(e)}"
        if msg is not None: assert msg in str(e), f"Expected message '{msg}' to be in exception but got '{str(e)}'"
    if was_ran: raise AssertionError(f"Expected exception of type {exception_class} but ran without issue.")
def capture_call_output(func, *args, **kwargs):
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = captured_output
        func(*args, **kwargs)
    except Exception as e: raise e
    finally: sys.stdout = original_stdout
    return captured_output.getvalue()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
