"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import warnings
from .state import AcceleratorState, GradientState
class SapiensAcceleratordScheduler:
    def __init__(self, scheduler, optimizers, step_with_optimizer: bool = True, split_batches: bool = False):
        self.scheduler = scheduler
        self.optimizers = optimizers if isinstance(optimizers, (list, tuple)) else [optimizers]
        self.split_batches = split_batches
        self.step_with_optimizer = step_with_optimizer
        self.gradient_state = GradientState()
    def step(self, *args, **kwargs):
        if not self.step_with_optimizer:
            self.scheduler.step(*args, **kwargs)
            return
        if not self.gradient_state.sync_gradients:
            if self.gradient_state.adjust_scheduler: self.scheduler._step_count += 1
            return
        for opt in self.optimizers:
            if opt.step_was_skipped: return
        if self.split_batches: self.scheduler.step(*args, **kwargs)
        else:
            num_processes = AcceleratorState().num_processes
            for _ in range(num_processes):
                if hasattr(self.scheduler, "total_steps"):
                    if self.scheduler._step_count <= self.scheduler.total_steps: self.scheduler.step(*args, **kwargs)
                else: self.scheduler.step(*args, **kwargs)
    def get_last_lr(self): return self.scheduler.get_last_lr()
    def state_dict(self): return self.scheduler.state_dict()
    def load_state_dict(self, state_dict): self.scheduler.load_state_dict(state_dict)
    def get_lr(self): return self.scheduler.get_lr()
    def print_lr(self, *args, **kwargs): return self.scheduler.print_lr(*args, **kwargs)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
