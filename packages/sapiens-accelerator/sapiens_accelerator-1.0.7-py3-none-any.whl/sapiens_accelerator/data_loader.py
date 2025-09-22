"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import math
from contextlib import suppress
from typing import Callable, List, Optional, Union
import torch
from torch.utils.data import BatchSampler, DataLoader, IterableDataset, RandomSampler
from .logging import get_logger
from .state import DistributedType, GradientState, PartialState, is_torch_xla_available
from .utils import (RNGType, broadcast, broadcast_object_list, concatenate, find_batch_size, get_data_structure, initialize_tensors, is_torch_version,
is_torchdata_stateful_dataloader_available, send_to_device, slice_tensors, synchronize_rng_states)
logger = get_logger(__name__)
_PYTORCH_DATALOADER_KWARGS = {"batch_size": 1, "shuffle": False, "sampler": None, "batch_sampler": None, "num_workers": 0, "collate_fn": None, "pin_memory": False,
"drop_last": False, "timeout": 0, "worker_init_fn": None, "multiprocessing_context": None, "generator": None, "prefetch_factor": 2, "persistent_workers": False}
_PYTORCH_DATALOADER_ADDITIONAL_KWARGS = {}
for v, additional_kwargs in _PYTORCH_DATALOADER_ADDITIONAL_KWARGS.items():
    if is_torch_version(">=", v): _PYTORCH_DATALOADER_KWARGS.update(additional_kwargs)
class SeedableRandomSampler(RandomSampler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epoch = 0
        self.initial_seed = torch.random.initial_seed()
    def __iter__(self):
        if self.generator is None:
            self.generator = torch.Generator()
            self.generator.manual_seed(self.initial_seed)
        seed = self.epoch + self.initial_seed
        self.generator.manual_seed(seed)
        yield from super().__iter__()
        self.set_epoch(self.epoch + 1)
    def set_epoch(self, epoch: int): self.epoch = epoch
class BatchSamplerShard(BatchSampler):
    def __init__(self, batch_sampler: BatchSampler, num_processes: int = 1, process_index: int = 0, split_batches: bool = False, even_batches: bool = True):
        if split_batches and batch_sampler.batch_size % num_processes != 0: raise ValueError(f"To use `BatchSamplerShard` in `split_batches` mode, the batch size ({batch_sampler.batch_size}) needs to be a round multiple of the number of processes ({num_processes}).")
        self.batch_sampler = batch_sampler
        self.num_processes = num_processes
        self.process_index = process_index
        self.split_batches = split_batches
        self.even_batches = even_batches
        self.batch_size = getattr(batch_sampler, "batch_size", None)
        self.drop_last = getattr(batch_sampler, "drop_last", False)
        if self.batch_size is None and self.even_batches: raise ValueError("You need to use `even_batches=False` when the batch sampler has no batch size. If you are not calling this method directly, set `accelerator.even_batches=False` instead.")
    @property
    def total_length(self): return len(self.batch_sampler)
    def __len__(self):
        if self.split_batches: return len(self.batch_sampler)
        if len(self.batch_sampler) % self.num_processes == 0: return len(self.batch_sampler) // self.num_processes
        length = len(self.batch_sampler) // self.num_processes
        if self.drop_last: return length
        elif self.even_batches: return length + 1
        else: return length + 1 if self.process_index < len(self.batch_sampler) % self.num_processes else length
    def __iter__(self): return self._iter_with_split() if self.split_batches else self._iter_with_no_split()
    def _iter_with_split(self):
        initial_data = []
        batch_length = self.batch_sampler.batch_size // self.num_processes
        for idx, batch in enumerate(self.batch_sampler):
            if idx == 0: initial_data = batch
            if len(batch) == self.batch_size: yield batch[batch_length * self.process_index : batch_length * (self.process_index + 1)]
        if not self.drop_last and len(initial_data) > 0 and len(batch) < self.batch_size:
            if not self.even_batches:
                if len(batch) > batch_length * self.process_index: yield batch[batch_length * self.process_index : batch_length * (self.process_index + 1)]
            else:
                while len(initial_data) < self.batch_size: initial_data += initial_data
                batch = batch + initial_data
                yield batch[batch_length * self.process_index : batch_length * (self.process_index + 1)]
    def _iter_with_no_split(self):
        initial_data = []
        batch_to_yield = []
        for idx, batch in enumerate(self.batch_sampler):
            if not self.drop_last and idx < self.num_processes: initial_data += batch
            if idx % self.num_processes == self.process_index: batch_to_yield = batch
            if idx % self.num_processes == self.num_processes - 1 and (self.batch_size is None or len(batch) == self.batch_size):
                yield batch_to_yield
                batch_to_yield = []
        if not self.drop_last and len(initial_data) > 0:
            if not self.even_batches:
                if len(batch_to_yield) > 0: yield batch_to_yield
            else:
                if len(batch_to_yield) == self.batch_size: yield batch_to_yield
                while len(initial_data) < self.num_processes * self.batch_size: initial_data += initial_data
                if len(batch) == self.batch_size:
                    batch = []
                    idx += 1
                cycle_index = 0
                while idx % self.num_processes != 0 or len(batch) > 0:
                    end_index = cycle_index + self.batch_size - len(batch)
                    batch += initial_data[cycle_index:end_index]
                    if idx % self.num_processes == self.process_index: yield batch
                    cycle_index = end_index
                    batch = []
                    idx += 1
class IterableDatasetShard(IterableDataset):
    def __init__(self, dataset: IterableDataset, batch_size: int = 1, drop_last: bool = False, num_processes: int = 1, process_index: int = 0, split_batches: bool = False):
        if split_batches and batch_size > 1 and batch_size % num_processes != 0: raise ValueError(f"To use `IterableDatasetShard` in `split_batches` mode, the batch size ({batch_size}) needs to be a round multiple of the number of processes ({num_processes}).")
        self.dataset = dataset
        self.batch_size = batch_size
        self.drop_last = drop_last
        self.num_processes = num_processes
        self.process_index = process_index
        self.split_batches = split_batches
    def set_epoch(self, epoch):
        self.epoch = epoch
        if hasattr(self.dataset, "set_epoch"): self.dataset.set_epoch(epoch)
    def __len__(self):
        if self.drop_last: return (len(self.dataset) // (self.batch_size * self.num_processes)) * self.batch_size
        else: return math.ceil(len(self.dataset) / (self.batch_size * self.num_processes)) * self.batch_size
    def __iter__(self):
        if (not hasattr(self.dataset, "set_epoch") and hasattr(self.dataset, "generator") and isinstance(self.dataset.generator, torch.Generator)): self.dataset.generator.manual_seed(self.epoch)
        real_batch_size = self.batch_size if self.split_batches else (self.batch_size * self.num_processes)
        process_batch_size = (self.batch_size // self.num_processes) if self.split_batches else self.batch_size
        process_slice = range(self.process_index * process_batch_size, (self.process_index + 1) * process_batch_size)
        first_batch = None
        current_batch = []
        for element in self.dataset:
            current_batch.append(element)
            if len(current_batch) == real_batch_size:
                for i in process_slice: yield current_batch[i]
                if first_batch is None: first_batch = current_batch.copy()
                current_batch = []
        if not self.drop_last and len(current_batch) > 0:
            if first_batch is None: first_batch = current_batch.copy()
            while len(current_batch) < real_batch_size: current_batch += first_batch
            for i in process_slice: yield current_batch[i]
class DataLoaderStateMixin:
    def __init_subclass__(cls, **kwargs):
        cls.end_of_dataloader = False
        cls.remainder = -1
    def reset(self):
        self.end_of_dataloader = False
        self.remainder = -1
    def begin(self):
        self.reset()
        with suppress(Exception):
            if not self._drop_last:
                length = getattr(self.dataset, "total_dataset_length", len(self.dataset))
                self.remainder = length % self.total_batch_size
        self.gradient_state._add_dataloader(self)
    def end(self): self.gradient_state._remove_dataloader(self)
class DataLoaderAdapter:
    def __init__(self, dataset, use_stateful_dataloader=False, batch_sampler=None, **kwargs):
        self.use_stateful_dataloader = use_stateful_dataloader
        if is_torchdata_stateful_dataloader_available(): from torchdata.stateful_dataloader import StatefulDataLoader
        if use_stateful_dataloader and not is_torchdata_stateful_dataloader_available(): raise ImportError("StatefulDataLoader is not available. Please install torchdata version 0.8.0 or higher to use it.")
        if use_stateful_dataloader: self.base_dataloader = StatefulDataLoader(dataset, batch_sampler=batch_sampler, **kwargs)
        else: self.base_dataloader = DataLoader(dataset, batch_sampler=batch_sampler, **kwargs)
        if hasattr(self.base_dataloader, "state_dict"): self.dl_state_dict = self.base_dataloader.state_dict()
    def __getattr__(self, name):
        if name == "base_dataloader": raise AttributeError()
        return getattr(self.base_dataloader, name)
    def state_dict(self): return self.dl_state_dict
    def load_state_dict(self, state_dict): self.base_dataloader.load_state_dict(state_dict)
    @property
    def __class__(self): return self.base_dataloader.__class__
    def __len__(self): return len(self.base_dataloader)
    def adjust_state_dict_for_prefetch(self):
        if PartialState().distributed_type != DistributedType.NO:
            factor = PartialState().num_processes - 1
            if self.dl_state_dict["_sampler_iter_yielded"] > 0: self.dl_state_dict["_sampler_iter_yielded"] -= factor
            if self.dl_state_dict["_num_yielded"] > 0: self.dl_state_dict["_num_yielded"] -= factor
            if self.dl_state_dict["_index_sampler_state"] is not None:
                if ("samples_yielded" in self.dl_state_dict["_index_sampler_state"] and self.dl_state_dict["_index_sampler_state"]["samples_yielded"] > 0): self.dl_state_dict["_index_sampler_state"]["samples_yielded"] -= self.batch_size * factor
    def _update_state_dict(self):
        if hasattr(self.base_dataloader, "state_dict"):
            self.dl_state_dict = self.base_dataloader.state_dict()
            self.adjust_state_dict_for_prefetch()
            self.dl_state_dict["_iterator_finished"] = self.end_of_dataloader
class DataLoaderShard(DataLoaderAdapter, DataLoaderStateMixin):
    def __init__(self, dataset, device=None, rng_types=None, synchronized_generator=None, skip_batches=0, use_stateful_dataloader=False,
    _drop_last: bool = False, _non_blocking: bool = False, **kwargs):
        super().__init__(dataset, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
        self.device = device
        self.rng_types = rng_types
        self.synchronized_generator = synchronized_generator
        self.skip_batches = skip_batches
        self.gradient_state = GradientState()
        self._drop_last = _drop_last
        self._non_blocking = _non_blocking
        self.iteration = 0
    def __iter__(self):
        if self.rng_types is not None: synchronize_rng_states(self.rng_types, self.synchronized_generator)
        self.begin()
        self.set_epoch(self.iteration)
        dataloader_iter = self.base_dataloader.__iter__()
        try: current_batch = next(dataloader_iter)
        except StopIteration: yield
        batch_index = 0
        while True:
            try:
                if self.device is not None: current_batch = send_to_device(current_batch, self.device, non_blocking=self._non_blocking)
                self._update_state_dict()
                next_batch = next(dataloader_iter)
                if batch_index >= self.skip_batches: yield current_batch
                batch_index += 1
                current_batch = next_batch
            except StopIteration:
                self.end_of_dataloader = True
                self._update_state_dict()
                if batch_index >= self.skip_batches: yield current_batch
                break
        self.iteration += 1
        self.end()
    def __reduce__(self):
        args = super().__reduce__()
        return (DataLoaderShard, *args[1:])
    def set_epoch(self, epoch: int):
        if self.iteration != epoch: self.iteration = epoch
        if hasattr(self.batch_sampler, "sampler") and hasattr(self.batch_sampler.sampler, "set_epoch"): self.batch_sampler.sampler.set_epoch(epoch)
        elif hasattr(self.dataset, "set_epoch"): self.dataset.set_epoch(epoch)
    @property
    def total_batch_size(self):
        batch_sampler = self.sampler if isinstance(self.sampler, BatchSampler) else self.batch_sampler
        return (batch_sampler.batch_size if getattr(batch_sampler, "split_batches", False) else (batch_sampler.batch_size * getattr(batch_sampler, "num_processes", 1)))
    @property
    def total_dataset_length(self):
        if hasattr(self.dataset, "total_length"): return self.dataset.total_length
        else: return len(self.dataset)
    def get_sampler(self): return get_sampler(self)
    def set_sampler(self, sampler):
        sampler_is_batch_sampler = isinstance(self.sampler, BatchSampler)
        if sampler_is_batch_sampler: self.sampler.sampler = sampler
        else:
            self.batch_sampler.sampler = sampler
            if hasattr(self.batch_sampler, "batch_sampler"): self.batch_sampler.batch_sampler.sampler = sampler
if is_torch_xla_available():
    import torch_xla.distributed.parallel_loader as xpl
    class MpDeviceLoaderWrapper(xpl.MpDeviceLoader):
        def __init__(self, dataloader: DataLoaderShard, device: torch.device):
            super().__init__(dataloader, device)
            self._rng_types = self._loader.rng_types
            self._loader.rng_types = None
            self.device = device
        def __iter__(self):
            if self._rng_types is not None: synchronize_rng_states(self._rng_types, self._loader.synchronized_generator)
            return super().__iter__()
        def set_epoch(self, epoch: int):
            if hasattr(self.dataloader, "set_epoch"): self.dataloader.set_epoch(epoch)
        @property
        def total_batch_size(self): return self._loader.total_batch_size
        @property
        def total_dataset_length(self): return self._loader.total_dataset_length
        @property
        def batch_sampler(self): return self._loader.batch_sampler
        @property
        def dataloader(self): return self._loader
class DataLoaderDispatcher(DataLoaderAdapter, DataLoaderStateMixin):
    def __init__(self, dataset, split_batches: bool = False, skip_batches=0, use_stateful_dataloader=False, _drop_last: bool = False, _non_blocking: bool = False, slice_fn=None, **kwargs):
        shuffle = False
        if is_torch_version(">=", "1.11.0"):
            from torch.utils.data.datapipes.iter.combinatorics import ShufflerIterDataPipe
            if isinstance(dataset, ShufflerIterDataPipe): shuffle = dataset._shuffle_enabled
        super().__init__(dataset, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
        self.split_batches = split_batches
        if shuffle: torch.utils.data.graph_settings.apply_shuffle_settings(dataset, shuffle=shuffle)
        self.gradient_state = GradientState()
        self.state = PartialState()
        self._drop_last = _drop_last
        self._non_blocking = _non_blocking
        self.skip_batches = skip_batches
        self.slice_fn = slice_tensors if slice_fn is None else slice_fn
        self.iteration = 0
    def _fetch_batches(self, iterator):
        batches, batch = None, None
        if self.state.process_index == 0:
            try:
                if self.split_batches:
                    self._update_state_dict()
                    batch = next(iterator)
                else:
                    batches = []
                    for _ in range(self.state.num_processes):
                        self._update_state_dict()
                        batches.append(next(iterator))
                    try: batch = concatenate(batches, dim=0)
                    except RuntimeError as e: raise RuntimeError("You can't use batches of different size with `dispatch_batches=True` or when using an `IterableDataset`. Either pass `dispatch_batches=False` and have each process fetch its own batch or pass `split_batches=True`. By doing so, the main process will fetch a full batch and slice it into `num_processes` batches for each process.") from e
                batch_info = [get_data_structure(batch), False]
            except StopIteration: batch_info = [None, True]
        else: batch_info = [None, self._stop_iteration]
        broadcast_object_list(batch_info)
        self._stop_iteration = batch_info[1]
        if self._stop_iteration:
            if not self.split_batches and not self._drop_last:
                if self.state.process_index == 0 and len(batches) > 0:
                    batch = concatenate(batches, dim=0)
                    batch_info = [get_data_structure(batch), False]
                else: batch_info = [None, True]
                broadcast_object_list(batch_info)
        return batch, batch_info
    def __iter__(self):
        self.begin()
        self.set_epoch(self.iteration)
        main_iterator = None
        if is_torch_version(">=", "2.0.1"): main_iterator = self.base_dataloader.__iter__()
        elif self.state.process_index == 0: main_iterator = self.base_dataloader.__iter__()
        stop_iteration = False
        self._stop_iteration = False
        first_batch = None
        next_batch, next_batch_info = self._fetch_batches(main_iterator)
        batch_index = 0
        while not stop_iteration:
            batch, batch_info = next_batch, next_batch_info
            if self.state.process_index != 0: batch = initialize_tensors(batch_info[0])
            batch = send_to_device(batch, self.state.device, non_blocking=self._non_blocking)
            batch = broadcast(batch, from_process=0)
            if not self._drop_last and first_batch is None: first_batch = self.slice_fn(batch, slice(0, self.state.num_processes), process_index=self.state.process_index, num_processes=self.state.num_processes)
            if batch is None: raise ValueError(f"Batch does not contain any data (`{batch}`). At the end of all iterable data available before expected stop iteration.")
            observed_batch_size = find_batch_size(batch)
            batch_size = observed_batch_size // self.state.num_processes
            stop_iteration = self._stop_iteration
            if not stop_iteration:
                next_batch, next_batch_info = self._fetch_batches(main_iterator)
                if self._stop_iteration and next_batch_info[0] is None: stop_iteration = True
            if not self._drop_last and stop_iteration and observed_batch_size % self.state.num_processes != 0:
                batch = concatenate([batch, first_batch], dim=0)
                batch_size += 1
            data_slice = slice(self.state.process_index * batch_size, (self.state.process_index + 1) * batch_size)
            batch = self.slice_fn(batch, data_slice, process_index=self.state.process_index, num_processes=self.state.num_processes)
            if stop_iteration:
                self.end_of_dataloader = True
                self._update_state_dict()
                self.remainder = observed_batch_size
            if batch_index >= self.skip_batches: yield batch
            batch_index += 1
        self.iteration += 1
        self.end()
    def set_epoch(self, epoch: int):
        if self.iteration != epoch: self.iteration = epoch
        if hasattr(self.batch_sampler, "sampler") and hasattr(self.batch_sampler.sampler, "set_epoch"): self.batch_sampler.sampler.set_epoch(epoch)
        elif hasattr(self.dataset, "set_epoch"): self.dataset.set_epoch(epoch)
    def __len__(self):
        whole_length = len(self.base_dataloader)
        if self.split_batches: return whole_length
        elif self._drop_last: return whole_length // self.state.num_processes
        else: return math.ceil(whole_length / self.state.num_processes)
    def __reduce__(self):
        args = super().__reduce__()
        return (DataLoaderDispatcher, *args[1:])
    @property
    def total_batch_size(self): return (self.dataset.batch_size if self.split_batches else (self.dataset.batch_size * self.dataset.num_processes))
    @property
    def total_dataset_length(self): return len(self.dataset)
    def get_sampler(self): return get_sampler(self)
    def set_sampler(self, sampler):
        sampler_is_batch_sampler = isinstance(self.sampler, BatchSampler)
        if sampler_is_batch_sampler: self.sampler.sampler = sampler
        else:
            self.batch_sampler.sampler = sampler
            if hasattr(self.batch_sampler, "batch_sampler"): self.batch_sampler.batch_sampler.sampler = sampler
def get_sampler(dataloader):
    sampler_is_batch_sampler = isinstance(dataloader.sampler, BatchSampler)
    if sampler_is_batch_sampler: sampler = getattr(dataloader.sampler, "sampler", None)
    else: sampler = getattr(dataloader.batch_sampler, "sampler", None)
    return sampler
def prepare_data_loader(dataloader: DataLoader, device: Optional[torch.device] = None, num_processes: Optional[int] = None, process_index: Optional[int] = None,
split_batches: bool = False, put_on_device: bool = False, rng_types: Optional[List[Union[str, RNGType]]] = None, dispatch_batches: Optional[bool] = None,
even_batches: bool = True, slice_fn_for_dispatch: Optional[Callable] = None, use_seedable_sampler: bool = False, non_blocking: bool = False, use_stateful_dataloader: bool = False) -> DataLoader:
    if dispatch_batches is None:
        if not put_on_device: dispatch_batches = False
        else: dispatch_batches = isinstance(dataloader.dataset, IterableDataset)
    if dispatch_batches and not put_on_device: raise ValueError("Using `dispatch_batches=True` requires `put_on_device=True`.")
    state = PartialState()
    if num_processes is None: num_processes = state.num_processes
    if process_index is None: process_index = state.process_index
    if split_batches:
        if dataloader.batch_size is not None: batch_size_for_check = dataloader.batch_size
        else:
            if hasattr(dataloader.batch_sampler, "batch_size"): batch_size_for_check = dataloader.batch_sampler.batch_size
            else: raise ValueError(f"In order to use `split_batches==True` you must have a `batch_size` attribute either in the passed `dataloader` or `dataloader.batch_sampler` objects, and it has to return a natural number. Your `dataloader.batch_size` is None and `dataloader.batch_sampler` (`{type(dataloader.batch_sampler)}`) does not have the `batch_size` attribute set.")
        if batch_size_for_check > 1 and batch_size_for_check % num_processes != 0: raise ValueError(f"To use a `DataLoader` in `split_batches` mode, the batch size ({dataloader.batch_size}) needs to be a round multiple of the number of processes ({num_processes}).")
    new_dataset = dataloader.dataset
    new_batch_sampler = dataloader.batch_sampler if not isinstance(new_dataset, IterableDataset) else None
    sampler_is_batch_sampler = isinstance(dataloader.sampler, BatchSampler)
    synchronized_generator = None
    sampler = get_sampler(dataloader)
    if isinstance(sampler, RandomSampler) and use_seedable_sampler: sampler = SeedableRandomSampler(data_source=sampler.data_source, replacement=sampler.replacement, num_samples=sampler._num_samples, generator=getattr(sampler, "generator", torch.Generator()))
    if isinstance(dataloader.sampler, RandomSampler) and state.distributed_type == DistributedType.XLA:
        generator = torch.Generator().manual_seed(42)
        dataloader.generator = generator
        dataloader.sampler.generator = generator
    if (num_processes != 1 or state.distributed_type == DistributedType.MEGATRON_LM) and not dispatch_batches:
        if isinstance(new_dataset, IterableDataset):
            if getattr(dataloader.dataset, "generator", None) is not None: synchronized_generator = dataloader.dataset.generator
            new_dataset = IterableDatasetShard(new_dataset, batch_size=dataloader.batch_size, drop_last=dataloader.drop_last, num_processes=num_processes,
            process_index=process_index, split_batches=split_batches)
        else:
            if not use_seedable_sampler and hasattr(sampler, "generator"):
                if sampler.generator is None: sampler.generator = torch.Generator()
                synchronized_generator = sampler.generator
            batch_sampler = dataloader.sampler if sampler_is_batch_sampler else dataloader.batch_sampler
            new_batch_sampler = BatchSamplerShard(batch_sampler, num_processes=num_processes, process_index=process_index, split_batches=split_batches, even_batches=even_batches)
    ignore_kwargs = ["batch_size", "shuffle", "sampler", "batch_sampler", "drop_last"]
    if rng_types is not None and synchronized_generator is None and "generator" in rng_types: rng_types.remove("generator")
    kwargs = {k: getattr(dataloader, k, _PYTORCH_DATALOADER_KWARGS[k]) for k in _PYTORCH_DATALOADER_KWARGS if k not in ignore_kwargs}
    if new_batch_sampler is None:
        kwargs["drop_last"] = dataloader.drop_last
        kwargs["batch_size"] = (dataloader.batch_size // num_processes if split_batches and not dispatch_batches else dataloader.batch_size)
    if dispatch_batches:
        kwargs.pop("generator")
        dataloader = DataLoaderDispatcher(new_dataset, split_batches=split_batches, batch_sampler=new_batch_sampler, _drop_last=dataloader.drop_last,
        _non_blocking=non_blocking, slice_fn=slice_fn_for_dispatch, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
    elif sampler_is_batch_sampler: dataloader = DataLoaderShard(new_dataset, device=device if put_on_device and state.distributed_type != DistributedType.XLA else None,
    sampler=new_batch_sampler, batch_size=dataloader.batch_size, rng_types=rng_types, _drop_last=dataloader.drop_last, _non_blocking=non_blocking,
    synchronized_generator=synchronized_generator, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
    else: dataloader = DataLoaderShard(new_dataset, device=device if put_on_device and state.distributed_type != DistributedType.XLA else None,
    batch_sampler=new_batch_sampler, rng_types=rng_types, synchronized_generator=synchronized_generator, _drop_last=dataloader.drop_last,
    _non_blocking=non_blocking, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
    if isinstance(sampler, SeedableRandomSampler) and use_seedable_sampler: dataloader.set_sampler(sampler)
    if state.distributed_type == DistributedType.XLA: return MpDeviceLoaderWrapper(dataloader, device)
    return dataloader
class SkipBatchSampler(BatchSampler):
    def __init__(self, batch_sampler, skip_batches=0):
        self.batch_sampler = batch_sampler
        self.skip_batches = skip_batches
    def __iter__(self):
        for index, samples in enumerate(self.batch_sampler):
            if index >= self.skip_batches: yield samples
    @property
    def total_length(self): return len(self.batch_sampler)
    def __len__(self): return len(self.batch_sampler) - self.skip_batches
class SkipDataLoader(DataLoaderAdapter, DataLoaderStateMixin):
    def __init__(self, dataset, skip_batches=0, use_stateful_dataloader=False, **kwargs):
        super().__init__(dataset, use_stateful_dataloader=use_stateful_dataloader, **kwargs)
        self.skip_batches = skip_batches
        self.gradient_state = GradientState()
    def __iter__(self):
        self.begin()
        for index, batch in enumerate(self.base_dataloader.__iter__()):
            if index >= self.skip_batches:
                self._update_state_dict()
                yield batch
        self.end()
    def __len__(self): return len(self.base_dataloader) - self.skip_batches
    def __reduce__(self):
        args = super().__reduce__()
        return (SkipDataLoader, *args[1:])
def skip_first_batches(dataloader, num_batches=0):
    state = PartialState()
    if state.distributed_type == DistributedType.XLA:
        device = dataloader.device
        dataloader = dataloader.dataloader
    dataset = dataloader.dataset
    sampler_is_batch_sampler = False
    if isinstance(dataset, IterableDataset): new_batch_sampler = None
    else:
        sampler_is_batch_sampler = isinstance(dataloader.sampler, BatchSampler)
        batch_sampler = dataloader.sampler if sampler_is_batch_sampler else dataloader.batch_sampler
        new_batch_sampler = SkipBatchSampler(batch_sampler, skip_batches=num_batches)
    ignore_kwargs = ["batch_size", "shuffle", "sampler", "batch_sampler", "drop_last"]
    kwargs = {k: getattr(dataloader, k, _PYTORCH_DATALOADER_KWARGS[k]) for k in _PYTORCH_DATALOADER_KWARGS if k not in ignore_kwargs}
    if new_batch_sampler is None:
        kwargs["drop_last"] = dataloader.drop_last
        kwargs["batch_size"] = dataloader.batch_size
    if isinstance(dataloader, DataLoaderDispatcher):
        if new_batch_sampler is None: kwargs["skip_batches"] = num_batches
        dataloader = DataLoaderDispatcher(dataset, split_batches=dataloader.split_batches, batch_sampler=new_batch_sampler, _drop_last=dataloader._drop_last, **kwargs)
    elif isinstance(dataloader, DataLoaderShard):
        if new_batch_sampler is None: kwargs["skip_batches"] = num_batches
        elif sampler_is_batch_sampler:
            kwargs["sampler"] = new_batch_sampler
            kwargs["batch_size"] = dataloader.batch_size
        else: kwargs["batch_sampler"] = new_batch_sampler
        dataloader = DataLoaderShard(dataset, device=dataloader.device, rng_types=dataloader.rng_types, synchronized_generator=dataloader.synchronized_generator, **kwargs)
    else:
        if new_batch_sampler is None: dataloader = SkipDataLoader(dataset, skip_batches=num_batches, **kwargs)
        else: dataloader = DataLoader(dataset, batch_sampler=new_batch_sampler, **kwargs)
    if state.distributed_type == DistributedType.XLA: dataloader = MpDeviceLoaderWrapper(dataloader, device)
    return dataloader
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
