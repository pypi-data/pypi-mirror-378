"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import contextlib
import io
import math
import time
from copy import deepcopy
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from sapiens_accelerator import Accelerator
from sapiens_accelerator.data_loader import SeedableRandomSampler, prepare_data_loader
from sapiens_accelerator.state import AcceleratorState
from sapiens_accelerator.test_utils import RegressionDataset, are_the_same_tensors
from sapiens_accelerator.utils import (DataLoaderConfiguration, DistributedType, gather, is_bf16_available, is_datasets_available, is_ipex_available,
is_mlu_available, is_musa_available, is_npu_available, is_pytest_available, is_xpu_available, set_seed, synchronize_rng_states)
if is_xpu_available(): from sapiens_accelerator.test_utils import RegressionModel4XPU as RegressionModel
else: from sapiens_accelerator.test_utils import RegressionModel
def generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler=False):
    if use_seedable_sampler:
        sampler = SeedableRandomSampler(generator=generator, data_source=train_set, num_samples=len(train_set))
        return DataLoader(train_set, batch_size=batch_size, sampler=sampler)
    else: return DataLoader(train_set, batch_size=batch_size, shuffle=True, generator=generator)
def print_main(state): pass
def print_local_main(state): pass
def print_last(state): pass
def print_on(state, process_idx): pass
def process_execution_check():
    accelerator = Accelerator()
    num_processes = accelerator.num_processes
    path = Path("check_main_process_first.txt")
    with accelerator.main_process_first():
        if accelerator.is_main_process:
            time.sleep(0.1)
            with open(path, "a+") as f: f.write("Currently in the main process\n")
        else:
            with open(path, "a+") as f: f.write("Now on another process\n")
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        with open(path) as f: text = "".join(f.readlines())
        try:
            assert text.startswith("Currently in the main process\n"), "Main process was not first"
            if num_processes > 1: assert text.endswith("Now on another process\n"), "Main process was not first"
            assert (text.count("Now on another process\n") == accelerator.num_processes - 1), f"Only wrote to file {text.count('Now on another process') + 1} times, not {accelerator.num_processes}"
        except AssertionError:
            path.unlink()
            raise
    if accelerator.is_main_process and path.exists(): path.unlink()
    accelerator.wait_for_everyone()
    f = io.StringIO()
    with contextlib.redirect_stdout(f): accelerator.on_main_process(print_main)(accelerator.state)
    result = f.getvalue().rstrip()
    if accelerator.is_main_process: assert result == "Printing from the main process 0", f"{result} != Printing from the main process 0"
    else: assert f.getvalue().rstrip() == "", f'{result} != ""'
    f.truncate(0)
    f.seek(0)
    with contextlib.redirect_stdout(f): accelerator.on_local_main_process(print_local_main)(accelerator.state)
    if accelerator.is_local_main_process: assert f.getvalue().rstrip() == "Printing from the local main process 0"
    else: assert f.getvalue().rstrip() == ""
    f.truncate(0)
    f.seek(0)
    with contextlib.redirect_stdout(f): accelerator.on_last_process(print_last)(accelerator.state)
    if accelerator.is_last_process: assert f.getvalue().rstrip() == f"Printing from the last process {accelerator.state.num_processes - 1}"
    else: assert f.getvalue().rstrip() == ""
    f.truncate(0)
    f.seek(0)
    for process_idx in range(num_processes):
        with contextlib.redirect_stdout(f): accelerator.on_process(print_on, process_index=process_idx)(accelerator.state, process_idx)
        if accelerator.process_index == process_idx: assert f.getvalue().rstrip() == f"Printing from process {process_idx}: {accelerator.process_index}"
        else: assert f.getvalue().rstrip() == ""
        f.truncate(0)
        f.seek(0)
def init_state_check(): state = AcceleratorState()
def rng_sync_check():
    state = AcceleratorState()
    synchronize_rng_states(["torch"])
    assert are_the_same_tensors(torch.get_rng_state()), "RNG states improperly synchronized on CPU."
    if state.distributed_type == DistributedType.MULTI_GPU:
        synchronize_rng_states(["cuda"])
        assert are_the_same_tensors(torch.cuda.get_rng_state()), "RNG states improperly synchronized on GPU."
    elif state.distributed_type == DistributedType.MULTI_XPU:
        synchronize_rng_states(["xpu"])
        assert are_the_same_tensors(torch.xpu.get_rng_state()), "RNG states improperly synchronized on XPU."
    generator = torch.Generator()
    synchronize_rng_states(["generator"], generator=generator)
    assert are_the_same_tensors(generator.get_state()), "RNG states improperly synchronized in generator."
def dl_preparation_check():
    state = AcceleratorState()
    length = 32 * state.num_processes
    dl = DataLoader(range(length), batch_size=8)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result)
    assert torch.equal(result.cpu(), torch.arange(0, length).long()), "Wrong non-shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, split_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result)
    assert torch.equal(result.cpu(), torch.arange(0, length).long()), "Wrong non-shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8, shuffle=True)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result).tolist()
    result.sort()
    assert result == list(range(length)), "Wrong shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8, shuffle=True)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, split_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result).tolist()
    result.sort()
    assert result == list(range(length)), "Wrong shuffled dataloader result."
def central_dl_preparation_check():
    state = AcceleratorState()
    length = 32 * state.num_processes
    dl = DataLoader(range(length), batch_size=8)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, dispatch_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result)
    assert torch.equal(result.cpu(), torch.arange(0, length).long()), "Wrong non-shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, split_batches=True, dispatch_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result)
    assert torch.equal(result.cpu(), torch.arange(0, length).long()), "Wrong non-shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8, shuffle=True)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, dispatch_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result).tolist()
    result.sort()
    assert result == list(range(length)), "Wrong shuffled dataloader result."
    dl = DataLoader(range(length), batch_size=8, shuffle=True)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index, put_on_device=True, split_batches=True, dispatch_batches=True)
    result = []
    for batch in dl: result.append(gather(batch))
    result = torch.cat(result).tolist()
    result.sort()
    assert result == list(range(length)), "Wrong shuffled dataloader result."
def custom_sampler_check():
    state = AcceleratorState()
    class CustomDataset(Dataset):
        def __init__(self, data): self.data = data
        def __len__(self): return len(self.data)
        def __getitem__(self, index): return self.data[index]
    class CustomBatchSampler:
        def __init__(self, dataset_length: int, batch_size: int, shuffle: bool = True):
            self.batch_size = batch_size
            self.data_index = np.arange(dataset_length)
            self.shuffle = shuffle
        def __iter__(self):
            num_batches = len(self)
            if self.shuffle: index = np.random.permutation(self.data_index)
            else: index = self.data_index
            output = np.array_split(index, num_batches)
            yield from output
        def __len__(self): return math.ceil(len(self.data_index) / self.batch_size)
    dataset = CustomDataset(range(32 * state.num_processes))
    sampler = CustomBatchSampler(len(dataset), batch_size=8)
    dl = DataLoader(dataset, batch_sampler=sampler)
    dl = prepare_data_loader(dl, state.device, state.num_processes, state.process_index)
    if hasattr(dl.batch_sampler, "batch_sampler"): assert isinstance(dl.batch_sampler.batch_sampler, CustomBatchSampler), "Custom sampler was changed after calling `prepare_data_loader`"
    else: assert isinstance(dl.batch_sampler, CustomBatchSampler), "Custom sampler was changed after calling `prepare_data_loader`"
def check_seedable_sampler():
    set_seed(42)
    train_set = RegressionDataset(length=10, seed=42)
    train_dl = DataLoader(train_set, batch_size=2, shuffle=True)
    config = DataLoaderConfiguration(use_seedable_sampler=True)
    accelerator = Accelerator(dataloader_config=config)
    train_dl = accelerator.prepare(train_dl)
    original_items = []
    for _ in range(3):
        for batch in train_dl: original_items.append(batch["x"])
    original_items = torch.cat(original_items)
    set_seed(42)
    train_dl.set_epoch(0)
    new_items = []
    for _ in range(3):
        for batch in train_dl: new_items.append(batch["x"])
    new_items = torch.cat(new_items)
    assert torch.allclose(original_items, new_items), "Did not obtain the same items with the same seed and epoch."
def check_seedable_sampler_in_batch_sampler_shard():
    set_seed(42)
    config = DataLoaderConfiguration(use_seedable_sampler=True)
    accelerator = Accelerator(dataloader_config=config)
    assert accelerator.num_processes > 1, "This test requires more than one process."
    dataloader = DataLoader(list(range(10)), batch_size=1, shuffle=True)
    prepared_data_loader = prepare_data_loader(dataloader=dataloader, use_seedable_sampler=True)
    target_sampler = prepared_data_loader.batch_sampler.batch_sampler.sampler
    assert isinstance(target_sampler, SeedableRandomSampler), "Sampler in BatchSamplerShard is not SeedableRandomSampler."
def mock_training(length, batch_size, generator, use_seedable_sampler=False):
    set_seed(42)
    generator.manual_seed(42)
    train_set = RegressionDataset(length=length, seed=42)
    train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
    model = RegressionModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    for epoch in range(3):
        for batch in train_dl:
            model.zero_grad()
            output = model(batch["x"])
            loss = torch.nn.functional.mse_loss(output, batch["y"])
            loss.backward()
            optimizer.step()
    return train_set, model
def training_check(use_seedable_sampler=False):
    state = AcceleratorState()
    generator = torch.Generator()
    batch_size = 8
    length = batch_size * 4 * state.num_processes
    train_set, old_model = mock_training(length, batch_size * state.num_processes, generator, use_seedable_sampler)
    assert are_the_same_tensors(old_model.a), "Did not obtain the same model on both processes."
    assert are_the_same_tensors(old_model.b), "Did not obtain the same model on both processes."
    accelerator = Accelerator()
    train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
    model = RegressionModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
    set_seed(42)
    generator.manual_seed(42)
    for _ in range(3):
        for batch in train_dl:
            model.zero_grad()
            output = model(batch["x"])
            loss = torch.nn.functional.mse_loss(output, batch["y"])
            accelerator.backward(loss)
            optimizer.step()
    model = accelerator.unwrap_model(model).cpu()
    assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on CPU or distributed training."
    assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on CPU or distributed training."
    dataloader_config = DataLoaderConfiguration(split_batches=True, use_seedable_sampler=use_seedable_sampler)
    accelerator = Accelerator(dataloader_config=dataloader_config)
    train_dl = generate_baseline_dataloader(train_set, generator, batch_size * state.num_processes, use_seedable_sampler)
    model = RegressionModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
    set_seed(42)
    generator.manual_seed(42)
    for _ in range(3):
        for batch in train_dl:
            model.zero_grad()
            output = model(batch["x"])
            loss = torch.nn.functional.mse_loss(output, batch["y"])
            accelerator.backward(loss)
            optimizer.step()
    model = accelerator.unwrap_model(model).cpu()
    assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on CPU or distributed training."
    assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on CPU or distributed training."
    if torch.cuda.is_available() or is_npu_available() or is_mlu_available() or is_musa_available():
        AcceleratorState._reset_state()
        dataloader_config = DataLoaderConfiguration(use_seedable_sampler=use_seedable_sampler)
        accelerator = Accelerator(mixed_precision="fp16", dataloader_config=dataloader_config)
        train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
        model = RegressionModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
        set_seed(42)
        generator.manual_seed(42)
        for _ in range(3):
            for batch in train_dl:
                model.zero_grad()
                output = model(batch["x"])
                loss = torch.nn.functional.mse_loss(output, batch["y"])
                accelerator.backward(loss)
                optimizer.step()
        model = accelerator.unwrap_model(model).cpu()
        assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on CPU or distributed training."
        assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on CPU or distributed training."
    if torch.cuda.is_available():
        AcceleratorState._reset_state()
        accelerator = Accelerator(mixed_precision="fp16")
        model = torch.nn.Linear(2, 4)
        model = accelerator.prepare(model)
        model_with_fp32_wrapper = accelerator.unwrap_model(model, keep_fp32_wrapper=True)
        input_tensor = torch.Tensor([1, 2]).to(dtype=torch.float16, device=accelerator.device)
        output = model_with_fp32_wrapper(input_tensor)
    if is_bf16_available():
        AcceleratorState._reset_state()
        dataloader_config = DataLoaderConfiguration(use_seedable_sampler=use_seedable_sampler)
        accelerator = Accelerator(mixed_precision="bf16", dataloader_config=dataloader_config)
        train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
        model = RegressionModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
        set_seed(42)
        generator.manual_seed(42)
        for _ in range(3):
            for batch in train_dl:
                model.zero_grad()
                output = model(batch["x"])
                loss = torch.nn.functional.mse_loss(output, batch["y"])
                accelerator.backward(loss)
                optimizer.step()
        model = accelerator.unwrap_model(model).cpu()
        assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on CPU or distributed training."
        assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on CPU or distributed training."
    if is_ipex_available():
        AcceleratorState._reset_state()
        dataloader_config = DataLoaderConfiguration(use_seedable_sampler=use_seedable_sampler)
        accelerator = Accelerator(mixed_precision="bf16", cpu=True, dataloader_config=dataloader_config)
        train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
        model = RegressionModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
        set_seed(42)
        generator.manual_seed(42)
        for _ in range(3):
            for batch in train_dl:
                model.zero_grad()
                output = model(batch["x"])
                loss = torch.nn.functional.mse_loss(output, batch["y"])
                accelerator.backward(loss)
                optimizer.step()
        model = accelerator.unwrap_model(model).cpu()
        assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on CPU or distributed training."
        assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on CPU or distributed training."
    if is_xpu_available():
        AcceleratorState._reset_state()
        dataloader_config = DataLoaderConfiguration(use_seedable_sampler=use_seedable_sampler)
        accelerator = Accelerator(mixed_precision="bf16", cpu=False, dataloader_config=dataloader_config)
        train_dl = generate_baseline_dataloader(train_set, generator, batch_size, use_seedable_sampler)
        model = RegressionModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
        set_seed(42)
        generator.manual_seed(42)
        for _ in range(3):
            for batch in train_dl:
                model.zero_grad()
                output = model(batch["x"])
                loss = torch.nn.functional.mse_loss(output, batch["y"])
                accelerator.backward(loss)
                optimizer.step()
        model = accelerator.unwrap_model(model).cpu()
        assert torch.allclose(old_model.a, model.a), "Did not obtain the same model on XPU or distributed training."
        assert torch.allclose(old_model.b, model.b), "Did not obtain the same model on XPU or distributed training."
def test_split_between_processes_dataset(datasets_Dataset):
    state = AcceleratorState()
    data = datasets_Dataset.from_list([dict(k=v) for v in range(2 * state.num_processes)])
    with state.split_between_processes(data, apply_padding=False) as results: assert (len(results) == 2), f"Each process did not have two items. Process index: {state.process_index}; Length: {len(results)}"
    data = datasets_Dataset.from_list([dict(k=v) for v in range(2 * state.num_processes - 1)])
    with state.split_between_processes(data, apply_padding=False) as results:
        if state.is_last_process: assert (len(results) == 1), f"Last process did not receive a single item. Process index: {state.process_index}; Length: {len(results)}"
        else: assert (len(results) == 2), f"One of the intermediate processes did not receive two items. Process index: {state.process_index}; Length: {len(results)}"
    data = datasets_Dataset.from_list([dict(k=v) for v in range(2 * state.num_processes - 1)])
    with state.split_between_processes(data, apply_padding=True) as results:
        if state.num_processes == 1: assert (len(results) == 1), f"Single process did not receive a single item. Process index: {state.process_index}; Length: {len(results)}"
        else: assert (len(results) == 2), f"Each process did not have two items. Process index: {state.process_index}; Length: {len(results)}"
    state.wait_for_everyone()
def test_split_between_processes_list():
    state = AcceleratorState()
    data = list(range(0, 2 * state.num_processes))
    with state.split_between_processes(data) as results: assert (len(results) == 2), f"Each process did not have two items. Process index: {state.process_index}; Length: {len(results)}"
    data = list(range(0, (3 * state.num_processes) - 1))
    with state.split_between_processes(data, apply_padding=True) as results:
        if state.is_last_process:
            num_samples_per_device = math.ceil(len(data) / state.num_processes)
            assert (len(results) == num_samples_per_device), f"Last process did not get the extra item(s). Process index: {state.process_index}; Length: {len(results)}"
    state.wait_for_everyone()
def test_split_between_processes_nested_dict():
    state = AcceleratorState()
    a = [1, 2, 3, 4, 5, 6, 7, 8]
    b = ["a", "b", "c", "d", "e", "f", "g", "h"]
    c = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8])
    if state.num_processes in (1, 2, 4):
        data = {"a": a, "b": b, "c": c}
        data_copy = deepcopy(data)
        with state.split_between_processes(data) as results:
            if state.process_index == 0: assert results["a"] == data_copy["a"][: 8 // state.num_processes]
            elif state.num_processes == 2: assert results["a"] == data_copy["a"][4:]
            elif state.process_index == 3: assert results["a"] == data_copy["a"][-2:], f'Expected: {data_copy["a"][-2]}, Actual: {results["a"]}'
            if state.process_index == 0: assert results["b"] == data_copy["b"][: 8 // state.num_processes]
            elif state.num_processes == 2: assert results["b"] == data_copy["b"][4:]
            elif state.process_index == 3: assert results["b"] == data_copy["b"][-2:]
            if state.process_index == 0: assert torch.allclose(results["c"], data_copy["c"][: 8 // state.num_processes]), f"Did not obtain expected values on process 0, expected `{data['c'][:8 // state.num_processes]}`, received: {results['c']}"
            elif state.num_processes == 2: assert torch.allclose(results["c"], data_copy["c"][4:]), f"Did not obtain expected values on process 2, expected `{data['c'][4:]}`, received: {results['c']}"
            elif state.process_index == 3: assert torch.allclose(results["c"], data_copy["c"][-2:]), f"Did not obtain expected values on process 4, expected `{data['c'][-2:]}`, received: {results['c']}"
    state.wait_for_everyone()
def test_split_between_processes_tensor():
    state = AcceleratorState()
    if state.num_processes > 1:
        data = torch.tensor([[0, 1, 2, 3], [4, 5, 6, 7]]).to(state.device)
        with state.split_between_processes(data) as results:
            if state.process_index == 0: assert torch.allclose(results, torch.tensor([0, 1, 2, 3]).to(state.device))
            else: assert torch.allclose(results, torch.tensor([4, 5, 6, 7]).to(state.device))
    state.wait_for_everyone()
def test_split_between_processes_evenly():
    state = AcceleratorState()
    if state.num_processes in (1, 2, 4, 8):
        data = list(range(17))
        num_samples_per_process = len(data) // state.num_processes
        num_extras = len(data) % state.num_processes
        with state.split_between_processes(data) as results:
            if state.process_index < num_extras: assert (len(results) == num_samples_per_process + 1), f"Each Process should have even elements. Expected: {num_samples_per_process + 1}, Actual: {len(results)}"
            else: assert (len(results) == num_samples_per_process), f"Each Process should have even elements. Expected: {num_samples_per_process}, Actual: {len(results)}"
    state.wait_for_everyone()
def test_trigger():
    accelerator = Accelerator()
    assert accelerator.check_trigger() is False
    if accelerator.is_main_process: accelerator.set_trigger()
    assert accelerator.check_trigger() is True
    assert accelerator.check_trigger() is False
def test_reinstantiated_state():
    import pytest
    AcceleratorState._reset_state()
    simple_model = torch.nn.Linear(1, 1)
    accelerator = Accelerator()
    AcceleratorState._reset_state()
    with pytest.raises(AttributeError) as cm: accelerator.prepare(simple_model)
    assert "`AcceleratorState` object has no attribute" in str(cm.value.args[0])
    assert "This happens if `AcceleratorState._reset_state()`" in str(cm.value.args[0])
def main():
    accelerator = Accelerator()
    state = accelerator.state
    init_state_check()
    state.wait_for_everyone()
    if state.distributed_type == DistributedType.MULTI_GPU: num_processes_per_node = torch.cuda.device_count()
    else: num_processes_per_node = state.num_processes
    if num_processes_per_node == state.num_processes:
        process_execution_check()
        test_split_between_processes_list()
        test_split_between_processes_nested_dict()
        test_split_between_processes_tensor()
        test_split_between_processes_evenly()
        if is_datasets_available():
            from datasets import Dataset as datasets_Dataset
            test_split_between_processes_dataset(datasets_Dataset)
    rng_sync_check()
    dl_preparation_check()
    if state.distributed_type != DistributedType.XLA:
        central_dl_preparation_check()
        custom_sampler_check()
        check_seedable_sampler()
    if state.num_processes > 1: check_seedable_sampler_in_batch_sampler_shard()
    if state.distributed_type == DistributedType.DEEPSPEED: return
    training_check(use_seedable_sampler=False)
    training_check(use_seedable_sampler=True)
    test_trigger()
    if is_pytest_available(): test_reinstantiated_state()
    state.destroy_process_group()
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
