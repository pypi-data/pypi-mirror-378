# __init__.py

# Import evaluation functions
from .evaluation import evaluate_classifier, evaluate_regressor

# Import data preparation functions
from .dataprep import datacheck, dataeda, auto_convert_dates

# Import model fitting + evaluation functions
from .model_runner import fit_eval_classifier, fit_eval_regressor

# Import model preparation functions
from .modelprep import split_sets, save_sets_csv, load_sets_csv

# Define what is available when someone does `from your_package import *`
__all__ = [
    # Evaluation
    "evaluate_classifier",
    "evaluate_regressor",

    # Data prep
    "datacheck",
    "dataeda",
    "auto_convert_dates",

    # Model runner
    "fit_eval_classifier",
    "fit_eval_regressor",

    # Model prep
    "split_sets",
    "save_sets_csv",
    "load_sets_csv",
]
