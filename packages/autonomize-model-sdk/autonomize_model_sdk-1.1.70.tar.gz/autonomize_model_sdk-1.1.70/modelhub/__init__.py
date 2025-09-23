"""
This module provides the following functionalities:

- `MLflowClient`: A class for interacting with MLflow.
- `PipelineManager`: A class for managing pipelines.
- `Stage`: A class representing a stage in a pipeline.
- `PipelineCreateRequest`: A class representing a request to create a pipeline.
- `Pipeline`: A class representing a pipeline.
- `setup_logger`: A function for setting up the logger.

These functionalities can be imported using the `from modelhub import *` statement.
"""

from .clients import DatasetClient, MLflowClient, PipelineManager
from .datasets import list_datasets, load_dataset
from .models import Pipeline, PipelineCreateRequest, Stage
from .utils import setup_logger

# Optional evaluation module (requires evidently)
try:
    from .evaluation import EvaluationConfig, EvaluationReport, PromptEvaluator

    _EVALUATION_AVAILABLE = True
except ImportError:
    _EVALUATION_AVAILABLE = False

__all__ = [
    "MLflowClient",
    "PipelineManager",
    "Stage",
    "PipelineCreateRequest",
    "Pipeline",
    "setup_logger",
    "DatasetClient",
    "load_dataset",
    "list_datasets",
]

# Add evaluation classes to __all__ if available
if _EVALUATION_AVAILABLE:
    __all__.extend(["PromptEvaluator", "EvaluationConfig", "EvaluationReport"])
