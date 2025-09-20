__version__ = "0.2.0"

from .utils.data_import import load_data
from .pipelines.run_pipeline import run_pipeline  

__all__ = [
    "load_data",
    "run_pipeline",   
]
