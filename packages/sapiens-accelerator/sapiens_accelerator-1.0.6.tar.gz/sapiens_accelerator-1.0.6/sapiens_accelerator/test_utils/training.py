"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import numpy as np
import torch
from torch.utils.data import DataLoader
from sapiens_accelerator.utils.dataclasses import DistributedType
class RegressionDataset:
    def __init__(self, a=2, b=3, length=64, seed=None):
        rng = np.random.default_rng(seed)
        self.length = length
        self.x = rng.normal(size=(length,)).astype(np.float32)
        self.y = a * self.x + b + rng.normal(scale=0.1, size=(length,)).astype(np.float32)
    def __len__(self): return self.length
    def __getitem__(self, i): return {"x": self.x[i], "y": self.y[i]}
class RegressionModel4XPU(torch.nn.Module):
    def __init__(self, a=0, b=0, double_output=False):
        super().__init__()
        self.a = torch.nn.Parameter(torch.tensor([2, 3]).float())
        self.b = torch.nn.Parameter(torch.tensor([2, 3]).float())
        self.first_batch = True
    def forward(self, x=None):
        if self.first_batch: self.first_batch = False
        return x * self.a[0] + self.b[0]
class RegressionModel(torch.nn.Module):
    def __init__(self, a=0, b=0, double_output=False):
        super().__init__()
        self.a = torch.nn.Parameter(torch.tensor(a).float())
        self.b = torch.nn.Parameter(torch.tensor(b).float())
        self.first_batch = True
    def forward(self, x=None):
        if self.first_batch: self.first_batch = False
        return x * self.a + self.b
def mocked_dataloaders(accelerator, batch_size: int = 16):
    from datasets import load_dataset
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    data_files = {"train": "tests/test_samples/MRPC/train.csv", "validation": "tests/test_samples/MRPC/dev.csv"}
    datasets = load_dataset("csv", data_files=data_files)
    label_list = datasets["train"].unique("label")
    label_to_id = {v: i for i, v in enumerate(label_list)}
    def tokenize_function(examples):
        outputs = tokenizer(examples["sentence1"], examples["sentence2"], truncation=True, max_length=None, padding="max_length")
        if "label" in examples: outputs["labels"] = [label_to_id[l] for l in examples["label"]]
        return outputs
    tokenized_datasets = datasets.map(tokenize_function, batched=True, remove_columns=["sentence1", "sentence2", "label"])
    def collate_fn(examples):
        if accelerator.distributed_type == DistributedType.XLA: return tokenizer.pad(examples, padding="max_length", max_length=128, return_tensors="pt")
        return tokenizer.pad(examples, padding="longest", return_tensors="pt")
    train_dataloader = DataLoader(tokenized_datasets["train"], shuffle=True, collate_fn=collate_fn, batch_size=2)
    eval_dataloader = DataLoader(tokenized_datasets["validation"], shuffle=False, collate_fn=collate_fn, batch_size=1)
    return train_dataloader, eval_dataloader
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
