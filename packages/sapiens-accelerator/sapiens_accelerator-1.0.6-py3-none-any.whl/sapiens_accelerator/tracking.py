"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import json
import os
import time
from functools import wraps
from typing import Any, Dict, List, Optional, Union
import yaml
from .logging import get_logger
from .state import PartialState
from .utils import (LoggerType, is_aim_available, is_clearml_available, is_comet_ml_available, is_dvclive_available, is_mlflow_available,
is_tensorboard_available, is_wandb_available, listify)
_available_trackers = []
if is_tensorboard_available(): _available_trackers.append(LoggerType.TENSORBOARD)
if is_wandb_available(): _available_trackers.append(LoggerType.WANDB)
if is_comet_ml_available(): _available_trackers.append(LoggerType.COMETML)
if is_aim_available(): _available_trackers.append(LoggerType.AIM)
if is_mlflow_available(): _available_trackers.append(LoggerType.MLFLOW)
if is_clearml_available(): _available_trackers.append(LoggerType.CLEARML)
if is_dvclive_available(): _available_trackers.append(LoggerType.DVCLIVE)
logger = get_logger(__name__)
def on_main_process(function):
    @wraps(function)
    def execute_on_main_process(self, *args, **kwargs):
        if getattr(self, "main_process_only", False): return PartialState().on_main_process(function)(self, *args, **kwargs)
        else: return function(self, *args, **kwargs)
    return execute_on_main_process
def get_available_trackers(): return _available_trackers
class GeneralTracker:
    main_process_only = True
    def __init__(self, _blank=False):
        if not _blank:
            err = ""
            if not hasattr(self, "name"): err += "`name`"
            if not hasattr(self, "requires_logging_directory"):
                if len(err) > 0: err += ", "
                err += "`requires_logging_directory`"
            if "tracker" not in dir(self):
                if len(err) > 0: err += ", "
                err += "`tracker`"
            if len(err) > 0: raise NotImplementedError(f"The implementation for this tracker class is missing the following required attributes. Please define them in the class definition: {err}")
    def store_init_configuration(self, values: dict): pass
    def log(self, values: dict, step: Optional[int], **kwargs): pass
    def finish(self): pass
class TensorBoardTracker(GeneralTracker):
    name = "tensorboard"
    requires_logging_directory = True
    @on_main_process
    def __init__(self, run_name: str, logging_dir: Union[str, os.PathLike], **kwargs):
        try: from torch.utils import tensorboard
        except ModuleNotFoundError: import tensorboardX as tensorboard
        super().__init__()
        self.run_name = run_name
        self.logging_dir = os.path.join(logging_dir, run_name)
        self.writer = tensorboard.SummaryWriter(self.logging_dir, **kwargs)
    @property
    def tracker(self): return self.writer
    @on_main_process
    def store_init_configuration(self, values: dict):
        self.writer.add_hparams(values, metric_dict={})
        self.writer.flush()
        project_run_name = time.time()
        dir_name = os.path.join(self.logging_dir, str(project_run_name))
        os.makedirs(dir_name, exist_ok=True)
        with open(os.path.join(dir_name, "hparams.yml"), "w") as outfile:
            try: yaml.dump(values, outfile)
            except yaml.representer.RepresenterError: raise
    @on_main_process
    def log(self, values: dict, step: Optional[int] = None, **kwargs):
        values = listify(values)
        for k, v in values.items():
            if isinstance(v, (int, float)): self.writer.add_scalar(k, v, global_step=step, **kwargs)
            elif isinstance(v, str): self.writer.add_text(k, v, global_step=step, **kwargs)
            elif isinstance(v, dict): self.writer.add_scalars(k, v, global_step=step, **kwargs)
        self.writer.flush()
    @on_main_process
    def log_images(self, values: dict, step: Optional[int], **kwargs):
        for k, v in values.items(): self.writer.add_images(k, v, global_step=step, **kwargs)
    @on_main_process
    def finish(self): self.writer.close()
class WandBTracker(GeneralTracker):
    name = "wandb"
    requires_logging_directory = False
    main_process_only = False
    @on_main_process
    def __init__(self, run_name: str, **kwargs):
        super().__init__()
        self.run_name = run_name
        import wandb
        self.run = wandb.init(project=self.run_name, **kwargs)
    @property
    def tracker(self): return self.run
    @on_main_process
    def store_init_configuration(self, values: dict):
        import wandb
        wandb.config.update(values, allow_val_change=True)
    @on_main_process
    def log(self, values: dict, step: Optional[int] = None, **kwargs): self.run.log(values, step=step, **kwargs)
    @on_main_process
    def log_images(self, values: dict, step: Optional[int] = None, **kwargs):
        import wandb
        for k, v in values.items(): self.log({k: [wandb.Image(image) for image in v]}, step=step, **kwargs)
    @on_main_process
    def log_table(self, table_name: str, columns: List[str] = None, data: List[List[Any]] = None, dataframe: Any = None, step: Optional[int] = None, **kwargs):
        import wandb
        values = {table_name: wandb.Table(columns=columns, data=data, dataframe=dataframe)}
        self.log(values, step=step, **kwargs)
    @on_main_process
    def finish(self): self.run.finish()
class CometMLTracker(GeneralTracker):
    name = "comet_ml"
    requires_logging_directory = False
    @on_main_process
    def __init__(self, run_name: str, **kwargs):
        super().__init__()
        self.run_name = run_name
        from comet_ml import Experiment
        self.writer = Experiment(project_name=run_name, **kwargs)
    @property
    def tracker(self): return self.writer
    @on_main_process
    def store_init_configuration(self, values: dict): self.writer.log_parameters(values)
    @on_main_process
    def log(self, values: dict, step: Optional[int] = None, **kwargs):
        if step is not None: self.writer.set_step(step)
        for k, v in values.items():
            if isinstance(v, (int, float)): self.writer.log_metric(k, v, step=step, **kwargs)
            elif isinstance(v, str): self.writer.log_other(k, v, **kwargs)
            elif isinstance(v, dict): self.writer.log_metrics(v, step=step, **kwargs)
    @on_main_process
    def finish(self): self.writer.end()
class AimTracker(GeneralTracker):
    name = "aim"
    requires_logging_directory = True
    @on_main_process
    def __init__(self, run_name: str, logging_dir: Optional[Union[str, os.PathLike]] = ".", **kwargs):
        self.run_name = run_name
        from aim import Run
        self.writer = Run(repo=logging_dir, **kwargs)
        self.writer.name = self.run_name
    @property
    def tracker(self): return self.writer
    @on_main_process
    def store_init_configuration(self, values: dict): self.writer["hparams"] = values
    @on_main_process
    def log(self, values: dict, step: Optional[int], **kwargs):
        for key, value in values.items(): self.writer.track(value, name=key, step=step, **kwargs)
    @on_main_process
    def log_images(self, values: dict, step: Optional[int] = None, kwargs: Optional[Dict[str, dict]] = None):
        import aim
        aim_image_kw = {}
        track_kw = {}
        if kwargs is not None:
            aim_image_kw = kwargs.get("aim_image", {})
            track_kw = kwargs.get("track", {})
        for key, value in values.items():
            if isinstance(value, tuple): img, caption = value
            else: img, caption = value, ""
            aim_image = aim.Image(img, caption=caption, **aim_image_kw)
            self.writer.track(aim_image, name=key, step=step, **track_kw)
    @on_main_process
    def finish(self): self.writer.close()
class MLflowTracker(GeneralTracker):
    name = "mlflow"
    requires_logging_directory = False
    @on_main_process
    def __init__(self, experiment_name: str = None, logging_dir: Optional[Union[str, os.PathLike]] = None, run_id: Optional[str] = None, tags: Optional[Union[Dict[str, Any], str]] = None,
    nested_run: Optional[bool] = False, run_name: Optional[str] = None, description: Optional[str] = None):
        experiment_name = os.environ.get("MLFLOW_EXPERIMENT_NAME", experiment_name)
        run_id = os.environ.get("MLFLOW_RUN_ID", run_id)
        tags = os.environ.get("MLFLOW_TAGS", tags)
        if isinstance(tags, str): tags = json.loads(tags)
        nested_run = os.environ.get("MLFLOW_NESTED_RUN", nested_run)
        import mlflow
        exps = mlflow.search_experiments(filter_string=f"name = '{experiment_name}'")
        if len(exps) > 0: experiment_id = exps[0].experiment_id
        else: experiment_id = mlflow.create_experiment(name=experiment_name, artifact_location=logging_dir, tags=tags)
        self.active_run = mlflow.start_run(run_id=run_id, experiment_id=experiment_id, run_name=run_name, nested=nested_run, tags=tags, description=description)
    @property
    def tracker(self): return self.active_run
    @on_main_process
    def store_init_configuration(self, values: dict):
        import mlflow
        for name, value in list(values.items()):
            if len(str(value)) > mlflow.utils.validation.MAX_PARAM_VAL_LENGTH: del values[name]
        values_list = list(values.items())
        for i in range(0, len(values_list), mlflow.utils.validation.MAX_PARAMS_TAGS_PER_BATCH): mlflow.log_params(dict(values_list[i : i + mlflow.utils.validation.MAX_PARAMS_TAGS_PER_BATCH]))
    @on_main_process
    def log(self, values: dict, step: Optional[int]):
        metrics = {}
        for k, v in values.items():
            if isinstance(v, (int, float)): metrics[k] = v
        import mlflow
        mlflow.log_metrics(metrics, step=step)
    @on_main_process
    def finish(self):
        import mlflow
        mlflow.end_run()
class ClearMLTracker(GeneralTracker):
    name = "clearml"
    requires_logging_directory = False
    @on_main_process
    def __init__(self, run_name: str = None, **kwargs):
        from clearml import Task
        current_task = Task.current_task()
        self._initialized_externally = False
        if current_task:
            self._initialized_externally = True
            self.task = current_task
            return
        kwargs.setdefault("project_name", os.environ.get("CLEARML_PROJECT", run_name))
        kwargs.setdefault("task_name", os.environ.get("CLEARML_TASK", run_name))
        self.task = Task.init(**kwargs)
    @property
    def tracker(self): return self.task
    @on_main_process
    def store_init_configuration(self, values: dict): return self.task.connect_configuration(values)
    @on_main_process
    def log(self, values: Dict[str, Union[int, float]], step: Optional[int] = None, **kwargs):
        clearml_logger = self.task.get_logger()
        for k, v in values.items():
            if not isinstance(v, (int, float)): continue
            if step is None:
                clearml_logger.report_single_value(name=k, value=v, **kwargs)
                continue
            title, series = ClearMLTracker._get_title_series(k)
            clearml_logger.report_scalar(title=title, series=series, value=v, iteration=step, **kwargs)
    @on_main_process
    def log_images(self, values: dict, step: Optional[int] = None, **kwargs):
        clearml_logger = self.task.get_logger()
        for k, v in values.items():
            title, series = ClearMLTracker._get_title_series(k)
            clearml_logger.report_image(title=title, series=series, iteration=step, image=v, **kwargs)
    @on_main_process
    def log_table(self, table_name: str, columns: List[str] = None, data: List[List[Any]] = None, dataframe: Any = None, step: Optional[int] = None, **kwargs):
        to_report = dataframe
        if dataframe is None:
            if data is None: raise ValueError("`ClearMLTracker.log_table` requires that `data` to be supplied if `dataframe` is `None`")
            to_report = [columns] + data if columns else data
        title, series = ClearMLTracker._get_title_series(table_name)
        self.task.get_logger().report_table(title=title, series=series, table_plot=to_report, iteration=step, **kwargs)
    @on_main_process
    def finish(self):
        if self.task and not self._initialized_externally: self.task.close()
    @staticmethod
    def _get_title_series(name):
        for prefix in ["eval", "test", "train"]:
            if name.startswith(prefix + "_"): return name[len(prefix) + 1 :], prefix
        return name, "train"
class DVCLiveTracker(GeneralTracker):
    name = "dvclive"
    requires_logging_directory = False
    @on_main_process
    def __init__(self, run_name: Optional[str] = None, live: Optional[Any] = None, **kwargs):
        from dvclive import Live
        super().__init__()
        self.live = live if live is not None else Live(**kwargs)
    @property
    def tracker(self): return self.live
    @on_main_process
    def store_init_configuration(self, values: dict): self.live.log_params(values)
    @on_main_process
    def log(self, values: dict, step: Optional[int] = None, **kwargs):
        from dvclive.plots import Metric
        if step is not None: self.live.step = step
        for k, v in values.items():
            if Metric.could_log(v): self.live.log_metric(k, v, **kwargs)
        self.live.next_step()
    @on_main_process
    def finish(self): self.live.end()
LOGGER_TYPE_TO_CLASS = {"aim": AimTracker, "comet_ml": CometMLTracker, "mlflow": MLflowTracker, "tensorboard": TensorBoardTracker, "wandb": WandBTracker, "clearml": ClearMLTracker, "dvclive": DVCLiveTracker}
def filter_trackers(log_with: List[Union[str, LoggerType, GeneralTracker]], logging_dir: Union[str, os.PathLike] = None): return []
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
