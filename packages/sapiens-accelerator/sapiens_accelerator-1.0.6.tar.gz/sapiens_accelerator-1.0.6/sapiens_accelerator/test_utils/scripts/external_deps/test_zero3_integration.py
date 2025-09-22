"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import torch.distributed
from sapiens_accelerator.test_utils import require_huggingface_suite, torch_device
from sapiens_accelerator.utils import is_transformers_available
if is_transformers_available(): from transformers import AutoModel, TrainingArguments
GPT2_TINY = "sshleifer/tiny-gpt2"
@require_huggingface_suite
def init_torch_dist_then_launch_deepspeed():
    backend = "ccl" if torch_device == "xpu" else "nccl"
    torch.distributed.init_process_group(backend=backend)
    deepspeed_config = {"zero_optimization": {"stage": 3}, "train_batch_size": "auto", "train_micro_batch_size_per_gpu": "auto"}
    train_args = TrainingArguments(output_dir="./", deepspeed=deepspeed_config)
    model = AutoModel.from_pretrained(GPT2_TINY)
    assert train_args is not None
    assert model is not None
def main(): init_torch_dist_then_launch_deepspeed()
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
