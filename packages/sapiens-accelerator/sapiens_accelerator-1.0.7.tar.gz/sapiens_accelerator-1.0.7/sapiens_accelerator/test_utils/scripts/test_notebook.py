"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import os
import time
from multiprocessing import Queue
from pytest import mark, raises
from torch.distributed.elastic.multiprocessing.errors import ChildFailedError
from sapiens_accelerator import PartialState, notebook_launcher
from sapiens_accelerator.test_utils import require_sapiens
from sapiens_accelerator.utils import is_sapiens_available
def basic_function(): pass
def tough_nut_function(queue: Queue):
    if queue.empty(): return
    trial = queue.get()
    if trial > 0:
        queue.put(trial - 1)
        raise RuntimeError("The nut hasn't cracked yet! Try again.")
def bipolar_sleep_function(sleep_sec: int):
    state = PartialState()
    if state.process_index % 2 == 0: raise RuntimeError("I'm an even process. I don't like to sleep.")
    else: time.sleep(sleep_sec)
NUM_PROCESSES = int(os.environ.get("SAPIENS_ACCELERATOR_NUM_PROCESSES", 1))
def test_can_initialize(): notebook_launcher(basic_function, (), num_processes=NUM_PROCESSES)
@mark.skipif(NUM_PROCESSES < 2, reason="Need at least 2 processes to test static rendezvous backends")
def test_static_rdzv_backend(): notebook_launcher(basic_function, (), num_processes=NUM_PROCESSES, rdzv_backend="static")
@mark.skipif(NUM_PROCESSES < 2, reason="Need at least 2 processes to test c10d rendezvous backends")
def test_c10d_rdzv_backend(): notebook_launcher(basic_function, (), num_processes=NUM_PROCESSES, rdzv_backend="c10d")
@mark.skipif(NUM_PROCESSES < 2, reason="Need at least 2 processes to test fault tolerance")
def test_fault_tolerant(max_restarts: int = 3):
    queue = Queue()
    queue.put(max_restarts)
    notebook_launcher(tough_nut_function, (queue,), num_processes=NUM_PROCESSES, max_restarts=max_restarts)
@mark.skipif(NUM_PROCESSES < 2, reason="Need at least 2 processes to test monitoring")
def test_monitoring(monitor_interval: float = 0.01, sleep_sec: int = 100):
    start_time = time.time()
    with raises(ChildFailedError, match="I'm an even process. I don't like to sleep."): notebook_launcher(bipolar_sleep_function, (sleep_sec,), num_processes=NUM_PROCESSES, monitor_interval=monitor_interval)
    assert time.time() - start_time < sleep_sec, "Monitoring did not stop the process in time."
@require_sapiens
def test_problematic_imports():
    with raises(RuntimeError, match="Please keep these imports"):
        import sapiens_machine as sapiens
        notebook_launcher(basic_function, (), num_processes=NUM_PROCESSES)
def main():
    test_can_initialize()
    test_static_rdzv_backend()
    test_c10d_rdzv_backend()
    test_fault_tolerant()
    test_monitoring()
    if is_sapiens_available(): test_problematic_imports()
    if NUM_PROCESSES > 1: PartialState().destroy_process_group()
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
