"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import argparse
import json
import os
import evaluate
import torch
from datasets import load_dataset
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup, set_seed
from sapiens_accelerator import Accelerator, DistributedType
from sapiens_accelerator.utils.deepspeed import DummyOptim, DummyScheduler
MAX_GPU_BATCH_SIZE = 16
EVAL_BATCH_SIZE = 32
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
def training_function(config, args):
    accelerator = Accelerator()
    lr = config["lr"]
    num_epochs = int(config["num_epochs"])
    seed = int(config["seed"])
    batch_size = int(config["batch_size"])
    model_name = args.model_name_or_path
    set_seed(seed)
    train_dataloader, eval_dataloader = get_dataloaders(accelerator, batch_size, model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, return_dict=True)
    optimizer_cls = (AdamW if accelerator.state.deepspeed_plugin is None or "optimizer" not in accelerator.state.deepspeed_plugin.deepspeed_config else DummyOptim)
    optimizer = optimizer_cls(params=model.parameters(), lr=lr)
    max_training_steps = len(train_dataloader) * num_epochs
    linear_decay_scheduler = False
    if (accelerator.state.deepspeed_plugin is None or "scheduler" not in accelerator.state.deepspeed_plugin.deepspeed_config):
        lr_scheduler = get_linear_schedule_with_warmup(optimizer=optimizer, num_warmup_steps=0, num_training_steps=max_training_steps)
        linear_decay_scheduler = True
    else: lr_scheduler = DummyScheduler(optimizer, total_num_steps=max_training_steps, warmup_num_steps=0)
    model, optimizer, train_dataloader, eval_dataloader, lr_scheduler = accelerator.prepare(model, optimizer, train_dataloader, eval_dataloader, lr_scheduler)
    starting_epoch = 0
    metric = evaluate.load("glue", "mrpc")
    best_performance = 0
    performance_metric = {}
    expected_lr_after_first_optim_step = lr * (1 - 1 / (max_training_steps / accelerator.num_processes / accelerator.gradient_accumulation_steps))
    lr_scheduler_check_completed = False
    for epoch in range(starting_epoch, num_epochs):
        model.train()
        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(model):
                outputs = model(**batch)
                loss = outputs.loss
                accelerator.backward(loss)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
                if (accelerator.sync_gradients and not lr_scheduler_check_completed and linear_decay_scheduler and accelerator.state.mixed_precision == "no"):
                    assert (lr_scheduler.get_last_lr()[0] == expected_lr_after_first_optim_step), f"Wrong lr found at second step, expected {expected_lr_after_first_optim_step}, got {lr_scheduler.get_last_lr()[0]}"
                    lr_scheduler_check_completed = True
        model.eval()
        samples_seen = 0
        for step, batch in enumerate(eval_dataloader):
            batch.to(accelerator.device)
            with torch.no_grad(): outputs = model(**batch)
            predictions = outputs.logits.argmax(dim=-1)
            predictions, references = accelerator.gather((predictions, batch["labels"]))
            if accelerator.use_distributed:
                if step == len(eval_dataloader) - 1:
                    predictions = predictions[: len(eval_dataloader.dataset) - samples_seen]
                    references = references[: len(eval_dataloader.dataset) - samples_seen]
                else: samples_seen += references.shape[0]
            metric.add_batch(predictions=predictions, references=references)
        eval_metric = metric.compute()
        accelerator.print(f"epoch {epoch}:", eval_metric)
        performance_metric[f"epoch-{epoch}"] = eval_metric["accuracy"]
        if best_performance < eval_metric["accuracy"]: best_performance = eval_metric["accuracy"]
    if linear_decay_scheduler and accelerator.state.mixed_precision == "no": assert (lr_scheduler.get_last_lr()[0] == 0), f"Wrong lr found at last step, expected 0, got {lr_scheduler.get_last_lr()[0]}"
    if args.performance_lower_bound is not None: assert (args.performance_lower_bound <= best_performance), f"Best performance metric {best_performance} is lower than the lower bound {args.performance_lower_bound}"
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        with open(os.path.join(args.output_dir, "all_results.json"), "w") as f: json.dump(performance_metric, f)
    accelerator.end_training()
def main():
    parser = argparse.ArgumentParser(description="Simple example of training script tracking peak GPU memory usage.")
    parser.add_argument("--model_name_or_path", type=str, default="bert-base-cased", help="Path to pretrained model or model identifier from huggingface.co/models.", required=False)
    parser.add_argument("--output_dir", type=str, default=".", help="Optional save directory where all checkpoint folders will be stored. Default is the current working directory.")
    parser.add_argument("--performance_lower_bound", type=float, default=None, help="Optional lower bound for the performance metric. If set, the training will throw error when the performance metric drops below this value.")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of train epochs.")
    args = parser.parse_args()
    config = {"lr": 2e-5, "num_epochs": args.num_epochs, "seed": 42, "batch_size": 16}
    training_function(config, args)
if __name__ == "__main__": main()
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
