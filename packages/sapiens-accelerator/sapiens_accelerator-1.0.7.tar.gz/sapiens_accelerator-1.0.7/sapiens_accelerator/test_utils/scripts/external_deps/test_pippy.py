"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import torch
from transformers import (BertConfig, BertForMaskedLM, GPT2Config, GPT2ForSequenceClassification)
from sapiens_accelerator import PartialState
from sapiens_accelerator.inference import prepare_pippy
from sapiens_accelerator.utils import DistributedType, set_seed
model_to_config = {"bert": (BertForMaskedLM, BertConfig, 512), "gpt2": (GPT2ForSequenceClassification, GPT2Config, 1024)}
def get_model_and_data_for_text(model_name, device, num_processes: int = 2):
    initializer, config, seq_len = model_to_config[model_name]
    config_args = {}
    model_config = config(**config_args)
    model = initializer(model_config)
    kwargs = dict(low=0, high=model_config.vocab_size, device=device, dtype=torch.int64, requires_grad=False)
    trace_input = torch.randint(size=(1, seq_len), **kwargs)
    inference_inputs = torch.randint(size=(num_processes, seq_len), **kwargs)
    return model, trace_input, inference_inputs
def test_bert(batch_size: int = 2):
    set_seed(42)
    state = PartialState()
    model, trace_input, inference_inputs = get_model_and_data_for_text("bert", "cpu", batch_size)
    model = prepare_pippy(model, example_args=(trace_input,), no_split_module_classes=model._no_split_modules)
    inputs = inference_inputs.to("cuda")
    with torch.no_grad(): output = model(inputs)
    if not state.is_last_process: assert output is None, "Output was not generated on just the last process!"
    else: assert output is not None, "Output was not generated in the last process!"
def test_gpt2(batch_size: int = 2):
    set_seed(42)
    state = PartialState()
    model, trace_input, inference_inputs = get_model_and_data_for_text("gpt2", "cpu", batch_size)
    model = prepare_pippy(model, example_args=(trace_input,), no_split_module_classes=model._no_split_modules)
    inputs = inference_inputs.to("cuda")
    with torch.no_grad(): output = model(inputs)
    if not state.is_last_process: assert output is None, "Output was not generated on just the last process!"
    else: assert output is not None, "Output was not generated in the last process!"
if __name__ == "__main__":
    state = PartialState()
    state.print("Testing pippy integration...")
    try:
        if state.distributed_type == DistributedType.MULTI_GPU:
            test_gpt2()
            test_bert()
    finally: state.destroy_process_group()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
