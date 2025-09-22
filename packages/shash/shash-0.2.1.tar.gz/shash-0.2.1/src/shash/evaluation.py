import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                            roc_auc_score, classification_report, confusion_matrix,
                            ConfusionMatrixDisplay)
from sklearn.metrics import (mean_absolute_error, mean_squared_error, root_mean_squared_error,
                             r2_score, mean_absolute_percentage_error)

def evaluate_classifier(y_true, y_pred_labels, y_pred_proba=None, dataset_name="Dataset"):
    """
    Evaluate a classification model and print metrics, confusion matrix, and classification report.
    
    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred_labels : array-like
        Predicted labels (binary or multiclass).
    y_pred_proba : array-like, optional
        Predicted probabilities (used for ROC AUC).
    dataset_name : str, default="Dataset"
        Name of dataset for display.
    """
    print("----------------------------"*5)
    print(f"\n--- {dataset_name} Evaluation ---")

    # Determine if binary or multi-class
    n_classes = pd.Series(y_true).nunique()
    average = "binary" if n_classes == 2 else "weighted"

    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred_labels)
    precision = precision_score(y_true, y_pred_labels, average=average, zero_division=0)
    recall = recall_score(y_true, y_pred_labels, average=average, zero_division=0)
    f1 = f1_score(y_true, y_pred_labels, average=average, zero_division=0)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    # ROC AUC
    if y_pred_proba is not None:
        if n_classes == 2:
            roc_auc = roc_auc_score(y_true, y_pred_proba)
        else:
            roc_auc = roc_auc_score(y_true, y_pred_proba, multi_class="ovr", average="weighted")
        print(f"ROC AUC  : {roc_auc:.4f}")

    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred_labels, zero_division=0))

    # Confusion matrix
    print("Confusion Matrix (Raw Counts):")
    cm = confusion_matrix(y_true, y_pred_labels)
    print(cm)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues")
    plt.title(f"Confusion Matrix - {dataset_name}")
    plt.show()


def evaluate_regressor(y_true, y_pred, dataset_name="Dataset"):
    """
    Evaluate a regression model and print metrics and residual plot.
    
    Parameters
    ----------
    y_true : array-like
        True values.
    y_pred : array-like
        Predicted values.
    dataset_name : str, default="Dataset"
        Name of dataset for display.
    """
    print("----------------------------"*5)
    print(f"\n--- {dataset_name} Evaluation ---")

    # Metrics
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    print(f"MAE  (Mean Absolute Error)      : {mae:.4f}")
    print(f"MSE  (Mean Squared Error)       : {mse:.4f}")
    print(f"RMSE (Root Mean Squared Error)  : {rmse:.4f}")
    print(f"MAPE (Mean Absolute % Error)    : {mape:.4f}")
    print(f"R²   (Coefficient of Determination): {r2:.4f}")

    # Residual plot
    residuals = y_true - y_pred
    plt.figure(figsize=(6, 4))
    plt.scatter(y_pred, residuals, alpha=0.6, color="blue")
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Predicted Values")
    plt.ylabel("Residuals")
    plt.title(f"Residual Plot - {dataset_name}")
    plt.show()

    # True vs Predicted plot
    plt.figure(figsize=(6, 4))
    plt.scatter(y_true, y_pred, alpha=0.6, color="green")
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], "r--")
    plt.xlabel("True Values")
    plt.ylabel("Predicted Values")
    plt.title(f"True vs Predicted - {dataset_name}")
    plt.show()