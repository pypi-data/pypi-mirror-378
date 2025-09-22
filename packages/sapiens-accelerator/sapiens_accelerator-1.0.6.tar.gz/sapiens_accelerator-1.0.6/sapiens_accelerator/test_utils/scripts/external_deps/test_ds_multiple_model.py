"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
from pathlib import Path
import evaluate
import torch
from datasets import load_dataset
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
from sapiens_accelerator import Accelerator, DeepSpeedPlugin, DistributedType
from sapiens_accelerator.state import AcceleratorState
from sapiens_accelerator.utils.deepspeed import get_active_deepspeed_plugin
MAX_GPU_BATCH_SIZE = 16
EVAL_BATCH_SIZE = 32
class NoiseModel(torch.nn.Module):
    def __init__(self, noise_factor=0.1):
        super().__init__()
        self.noise_factor = torch.nn.Parameter(torch.tensor(noise_factor, dtype=torch.float32))
    def forward(self, loss): return loss * self.noise_factor
def get_dataloaders(accelerator: Accelerator, batch_size: int = 16, model_name: str = "bert-base-cased"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    datasets = load_dataset("glue", "mrpc")
    def tokenize_function(examples):
        outputs = tokenizer(examples["sentence1"], examples["sentence2"], truncation=True, max_length=None)
        return outputs
    tokenized_datasets = datasets.map(tokenize_function, batched=True, remove_columns=["idx", "sentence1", "sentence2"], load_from_cache_file=False)
    tokenized_datasets = tokenized_datasets.rename_column("label", "labels")
    def collate_fn(examples):
        if accelerator.distributed_type == DistributedType.XLA: return tokenizer.pad(examples, padding="max_length", max_length=128, return_tensors="pt")
        return tokenizer.pad(examples, padding="longest", return_tensors="pt")
    train_dataloader = DataLoader(tokenized_datasets["train"], shuffle=True, collate_fn=collate_fn, batch_size=batch_size)
    eval_dataloader = DataLoader(tokenized_datasets["validation"], shuffle=False, collate_fn=collate_fn, batch_size=EVAL_BATCH_SIZE)
    return train_dataloader, eval_dataloader
test_file_path = __file__
path = Path(test_file_path).resolve()
test_file_dir_str = str(path.parent.parent.parent.parent.parent.parent)
ds_config_file = dict(zero2=f"{test_file_dir_str}/tests/deepspeed/ds_config_zero2_model_only.json", zero3=f"{test_file_dir_str}/tests/deepspeed/ds_config_zero3_model_only.json")
def single_model_training(config, args):
    num_epochs = config["num_epochs"]
    zero2_plugin = DeepSpeedPlugin(hf_ds_config=ds_config_file["zero2"])
    zero3_plugin = DeepSpeedPlugin(hf_ds_config=ds_config_file["zero3"])
    deepspeed_plugins = {"training": zero2_plugin, "inference": zero3_plugin}
    accelerator = Accelerator(deepspeed_plugins=deepspeed_plugins, mixed_precision="bf16")
    assert get_active_deepspeed_plugin(accelerator.state) is zero2_plugin
    train_model = AutoModelForSequenceClassification.from_pretrained(args.model_name_or_path)
    train_dataloader, eval_dataloader = get_dataloaders(accelerator, batch_size=config["batch_size"], model_name=args.model_name_or_path)
    max_training_steps = len(train_dataloader) * config["num_epochs"]
    optimizer = AdamW(train_model.parameters(), lr=config["lr"])
    lr_scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=max_training_steps)
    train_dataloader, eval_dataloader, train_model, optimizer, lr_scheduler = accelerator.prepare(train_dataloader, eval_dataloader, train_model, optimizer, lr_scheduler)
    accelerator.state.select_deepspeed_plugin("inference")
    assert get_active_deepspeed_plugin(accelerator.state) is zero3_plugin
    inference_model = NoiseModel()
    inference_model = accelerator.prepare(inference_model)
    inference_model.eval()
    accelerator.state.select_deepspeed_plugin("training")
    starting_epoch = 0
    best_performance = 0
    metric = evaluate.load("glue", "mrpc")
    performance_metric = {}
    for epoch in range(starting_epoch, num_epochs):
        train_model.train()
        inference_model.train()
        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(train_model):
                outputs_1 = train_model(**batch)
                with torch.no_grad(): outputs_2 = inference_model(outputs_1.loss)
                loss = outputs_1.loss + outputs_2
                accelerator.backward(loss)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
        train_model.eval()
        for step, batch in enumerate(eval_dataloader):
            with torch.no_grad(): outputs = train_model(**batch)
            predictions = outputs.logits.argmax(dim=-1)
            predictions, references = accelerator.gather_for_metrics((predictions, batch["labels"]))
            metric.add_batch(predictions=predictions, references=references)
        eval_metric = metric.compute()
        accelerator.print(f"epoch {epoch}:", eval_metric)
        performance_metric[f"epoch-{epoch}"] = eval_metric["accuracy"]
        if best_performance < eval_metric["accuracy"]: best_performance = eval_metric["accuracy"]
    assert best_performance > performance_metric["epoch-0"]
def multiple_model_training(config, args):
    num_epochs = config["num_epochs"]
    zero2_plugin = DeepSpeedPlugin(hf_ds_config=ds_config_file["zero2"])
    zero3_plugin = DeepSpeedPlugin(hf_ds_config=ds_config_file["zero3"])
    deepspeed_plugins = {"zero2": zero2_plugin, "zero3": zero3_plugin}
    zero2_accelerator = Accelerator(deepspeed_plugins=deepspeed_plugins, mixed_precision="bf16")
    zero3_accelerator = Accelerator()
    assert get_active_deepspeed_plugin(zero2_accelerator.state) is zero2_plugin
    zero2_model = AutoModelForSequenceClassification.from_pretrained(args.model_name_or_path)
    train_dataloader, eval_dataloader = get_dataloaders(zero2_accelerator, batch_size=config["batch_size"], model_name=args.model_name_or_path)
    max_training_steps = len(train_dataloader) * config["num_epochs"]
    zero2_optimizer = AdamW(zero2_model.parameters(), lr=config["lr"])
    zero2_lr_scheduler = get_linear_schedule_with_warmup(zero2_optimizer, num_warmup_steps=0, num_training_steps=max_training_steps)
    train_dataloader, eval_dataloader, zero2_model, zero2_optimizer, zero2_lr_scheduler = zero2_accelerator.prepare(train_dataloader, eval_dataloader, zero2_model, zero2_optimizer, zero2_lr_scheduler)
    assert zero2_accelerator.deepspeed_engine_wrapped.engine is zero2_model
    zero3_accelerator.state.select_deepspeed_plugin("zero3")
    zero3_plugin.deepspeed_config["train_micro_batch_size_per_gpu"] = zero2_plugin.deepspeed_config["train_micro_batch_size_per_gpu"]
    assert get_active_deepspeed_plugin(zero3_accelerator.state) is zero3_plugin
    zero3_model = AutoModelForSequenceClassification.from_pretrained(args.model_name_or_path)
    zero3_optimizer = AdamW(zero3_model.parameters(), lr=config["lr"])
    zero3_lr_scheduler = get_linear_schedule_with_warmup(zero3_optimizer, num_warmup_steps=0, num_training_steps=max_training_steps)
    zero3_model, zero3_optimizer, zero3_lr_scheduler = zero3_accelerator.prepare(zero3_model, zero3_optimizer, zero3_lr_scheduler)
    assert zero3_accelerator.deepspeed_engine_wrapped.engine is zero3_model
    starting_epoch = 0
    best_performance_a = 0
    best_performance_b = 0
    metric_a = evaluate.load("glue", "mrpc")
    metric_b = evaluate.load("glue", "mrpc")
    performance_metric_a = {}
    performance_metric_b = {}
    for epoch in range(starting_epoch, num_epochs):
        zero2_model.train()
        zero3_model.train()
        for step, batch in enumerate(train_dataloader):
            with zero2_accelerator.accumulate(zero2_model, zero3_model):
                outputs_1 = zero2_model(**batch)
                zero2_accelerator.backward(outputs_1.loss)
                zero2_optimizer.step()
                zero2_lr_scheduler.step()
                zero2_optimizer.zero_grad()
                outputs_2 = zero3_model(**batch)
                zero3_accelerator.backward(outputs_2.loss)
                zero3_optimizer.step()
                zero3_lr_scheduler.step()
                zero3_optimizer.zero_grad()
        zero2_model.eval()
        zero3_model.eval()
        for step, batch in enumerate(eval_dataloader):
            with torch.no_grad():
                logits_a = zero2_model(**batch).logits
                logits_b = zero3_model(**batch).logits
            predictions_a = logits_a.argmax(dim=-1)
            predictions_b = logits_b.argmax(dim=-1)
            predictions_a, predictions_b, references = zero2_accelerator.gather_for_metrics((predictions_a, predictions_b, batch["labels"]))
            metric_a.add_batch(predictions=predictions_a, references=references)
            metric_b.add_batch(predictions=predictions_b, references=references)
        eval_metric_a = metric_a.compute()
        eval_metric_b = metric_b.compute()
        zero2_accelerator.print(f"epoch {epoch}:", eval_metric_a, eval_metric_b)
        performance_metric_a[f"epoch-{epoch}"] = eval_metric_a["accuracy"]
        performance_metric_b[f"epoch-{epoch}"] = eval_metric_b["accuracy"]
        if best_performance_a < eval_metric_a["accuracy"]: best_performance_a = eval_metric_a["accuracy"]
        if best_performance_b < eval_metric_b["accuracy"]: best_performance_b = eval_metric_b["accuracy"]
    assert best_performance_a > performance_metric_a["epoch-0"]
    assert best_performance_b > performance_metric_b["epoch-0"]
def main():
    parser = argparse.ArgumentParser(description="Simple example of training script tracking peak GPU memory usage.")
    parser.add_argument("--model_name_or_path", type=str, default="bert-base-cased", help="", required=False)
    parser.add_argument("--performance_lower_bound", type=float, default=None, help="Optional lower bound for the performance metric. If set, the training will throw error when the performance metric drops below this value.")
    parser.add_argument("--num_epochs", type=int, default=2, help="Number of train epochs.")
    args = parser.parse_args()
    config = {"lr": 2e-5, "num_epochs": args.num_epochs, "seed": 42, "batch_size": 16}
    single_model_training(config, args)
    AcceleratorState._reset_state(True)
    multiple_model_training(config, args)
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
