import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split

def split_sets(features, target, test_val_ratio=0.3, stratify=False):
    """
    Split features and target into training, validation, and test sets.
    
    Parameters
    ----------
    features : pd.DataFrame or np.ndarray
        Feature set.
    target : pd.Series or np.ndarray
        Target variable.
    test_val_ratio : float, default=0.3
        Proportion of data to allocate to test + validation sets.
    stratify : bool or array-like, default=False
        - If True, stratify splits using the target (for classification).
        - If array-like, stratify using that array.
        - If False, no stratification (for regression).
    
    Returns
    -------
    X_train, y_train, X_val, y_val, X_test, y_test
    """
    # Ensure test_val_ratio is between 0 and 1
    if not (0 < test_val_ratio < 1):
        raise ValueError("test_val_ratio must be between 0 and 1.")

    # Determine stratify option for first split
    if stratify is True:
        stratify_option = target
    else:
        stratify_option = None  # for regression or stratify=False

    # First split: Train vs (Validation + Test)
    X_train, X_test_val, y_train, y_test_val = train_test_split(
        features, target,
        test_size=test_val_ratio,
        random_state=8,
        stratify=stratify_option
    )

    # Stratify option for second split
    if stratify is True:
        stratify_option_2 = y_test_val
    else:
        stratify_option_2 = None


    # Second split: Validation vs Test
    X_val, X_test, y_val, y_test = train_test_split(
        X_test_val, y_test_val,
        test_size=0.5,
        random_state=8,
        stratify=stratify_option_2
    )

    return X_train, y_train, X_val, y_val, X_test, y_test


def save_sets_csv(X_train=None, y_train=None, 
                  X_val=None, y_val=None, 
                  X_test=None, y_test=None, 
                  path='../data/processed/'):
    """
    Save the different sets as CSV files (works for both NumPy arrays and pandas DataFrames/Series).

    Parameters
    ----------
    X_train, y_train, X_val, y_val, X_test, y_test: array-like or DataFrame
        Features/targets for train, validation, and test sets.
    path : str
        Path to the folder where the sets will be saved (default: '../data/processed/')
    """

    os.makedirs(path, exist_ok=True)  # ensure directory exists

    def save_data(data, name):
        if data is None:
            return
        # If it's a numpy array, convert to DataFrame first
        if isinstance(data, np.ndarray):
            df = pd.DataFrame(data)
        elif isinstance(data, (pd.DataFrame, pd.Series)):
            df = data
        else:
            raise TypeError(f"{name} must be a numpy array, pandas DataFrame, or pandas Series.")
        df.to_csv(os.path.join(path, f"{name}.csv"), index=False)

    save_data(X_train, "X_train")
    save_data(y_train, "y_train")
    save_data(X_val,   "X_val")
    save_data(y_val,   "y_val")
    save_data(X_test,  "X_test")
    save_data(y_test,  "y_test")


def load_sets_csv(path='../data/processed/'):
    """
    Load the saved train/val/test sets from CSV files.

    Parameters
    ----------
    path : str
        Path to the folder where the sets are saved (default: '../data/processed/')

    Returns
    -------
    X_train, y_train, X_val, y_val, X_test, y_test : pd.DataFrame or pd.Series
        The datasets loaded from CSV files.
    """

    def load_data(name):
        file_path = os.path.join(path, f"{name}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # If it's a single column (like y), return as Series
            if df.shape[1] == 1:
                return df.iloc[:, 0]
            return df
        else:
            print(f"Warning: {file_path} not found.")
            return None

    X_train = load_data("X_train")
    y_train = load_data("y_train")
    X_val   = load_data("X_val")
    y_val   = load_data("y_val")
    X_test  = load_data("X_test")
    y_test  = load_data("y_test")

    return X_train, y_train, X_val, y_val, X_test, y_test