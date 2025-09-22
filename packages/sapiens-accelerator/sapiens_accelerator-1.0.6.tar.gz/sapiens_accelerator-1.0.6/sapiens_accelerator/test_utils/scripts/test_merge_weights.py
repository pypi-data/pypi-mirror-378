"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import gc
import logging
import shutil
from pathlib import Path
import torch
from safetensors.torch import load_file
from torch.distributed.fsdp.fully_sharded_data_parallel import ShardingStrategy, StateDictType
from torch.utils.data import DataLoader
from sapiens_accelerator import Accelerator, FullyShardedDataParallelPlugin
from sapiens_accelerator.commands.merge import merge_command, merge_command_parser
from sapiens_accelerator.state import AcceleratorState
from sapiens_accelerator.test_utils.training import RegressionDataset
from sapiens_accelerator.utils import merge_fsdp_weights, patch_environment, save_fsdp_model
logging.basicConfig(level=logging.INFO)
parser = merge_command_parser()
class TinyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = torch.nn.Linear(16, 16)
        self.activation = torch.nn.ReLU()
        self.linear2 = torch.nn.Linear(16, 16)
        self.softmax = torch.nn.Softmax()
    def forward(self, x): return self.linear2(self.activation(self.linear1(x)))
def setup():
    if AcceleratorState._shared_state != {}: AcceleratorState()._reset_state()
    plugin = FullyShardedDataParallelPlugin(sharding_strategy=ShardingStrategy.FULL_SHARD, state_dict_type=StateDictType.SHARDED_STATE_DICT)
    model = TinyModel()
    with patch_environment(fsdp_auto_wrap_policy="SIZE_BASED_WRAP"): plugin.set_auto_wrap_policy(model)
    accelerator = Accelerator(fsdp_plugin=plugin)
    model = accelerator.prepare(model)
    return model, plugin, accelerator
def mock_training(accelerator, model):
    train_set = RegressionDataset(length=128, seed=42)
    train_dl = DataLoader(train_set, batch_size=16, shuffle=False)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    train_dl, model, optimizer = accelerator.prepare(train_dl, model, optimizer)
    for _ in range(3):
        for batch in train_dl:
            model.zero_grad()
            output = model(batch["x"])
            loss = torch.nn.functional.mse_loss(output, batch["y"])
            accelerator.backward(loss)
            optimizer.step()
    return model
def check_weights(operation, state_1, state_2):
    for weight_1, weight_2 in zip(state_1.values(), state_2.values()):
        if str(weight_1.device) != "cuda": weight_1 = weight_1.to("cuda")
        if str(weight_2.device) != "cuda": weight_2 = weight_2.to("cuda")
        if operation == "same": assert torch.allclose(weight_1, weight_2)
        else: assert not torch.allclose(weight_1, weight_2)
def check_safetensors_weights(path, model):
    safe_state_dict = load_file(path / "model.safetensors")
    safe_loaded_model = TinyModel()
    check_weights("diff", model.state_dict(), safe_loaded_model.state_dict())
    safe_loaded_model.load_state_dict(safe_state_dict)
    check_weights("same", model.state_dict(), safe_loaded_model.state_dict())
def check_pytorch_weights(path, model):
    nonsafe_state_dict = torch.load(path / "pytorch_model.bin")
    nonsafe_loaded_model = TinyModel()
    check_weights("diff", model.state_dict(), nonsafe_loaded_model.state_dict())
    nonsafe_loaded_model.load_state_dict(nonsafe_state_dict)
    check_weights("same", model.state_dict(), nonsafe_loaded_model.state_dict())
def test_merge_weights_safetensors(model, path):
    merge_fsdp_weights(path / "pytorch_model_fsdp_0", path, safe_serialization=True)
    check_safetensors_weights(path, model)
def test_merge_weights_command_safetensors(model, path):
    args = parser.parse_args([str(path / "pytorch_model_fsdp_0"), str(path)])
    merge_command(args)
    check_safetensors_weights(path, model)
def test_merge_weights_pytorch(model, path):
    merge_fsdp_weights(path / "pytorch_model_fsdp_0", path, safe_serialization=False)
    check_pytorch_weights(path, model)
def test_merge_weights_command_pytorch(model, path):
    args = parser.parse_args([str(path / "pytorch_model_fsdp_0"), str(path), "--unsafe_serialization"])
    merge_command(args)
    check_pytorch_weights(path, model)
if __name__ == "__main__":
    model, plugin, accelerator = setup()
    if accelerator.num_processes > 1:
        try:
            out_path = Path("test_merge_weights_fsdp_weights")
            if not out_path.exists(): out_path.mkdir(parents=True, exist_ok=True)
            model = mock_training(accelerator, model)
            accelerator.wait_for_everyone()
            gc.collect()
            save_fsdp_model(plugin, accelerator, model, out_path)
            accelerator.wait_for_everyone()
            test_merge_weights_safetensors(model, out_path)
            test_merge_weights_command_safetensors(model, out_path)
            test_merge_weights_pytorch(model, out_path)
            test_merge_weights_command_pytorch(model, out_path)
        except Exception: raise
        finally:
            if accelerator.is_main_process: shutil.rmtree(out_path)
            accelerator.wait_for_everyone()
            accelerator.end_training()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
