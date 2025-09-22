from .evaluation import evaluate_classifier, evaluate_regressor  

# ---------------- FIT + EVAL WRAPPERS ----------------
def fit_eval_classifier(model, X_train, y_train, X_val=None, y_val=None, X_test=None, y_test=None):
    """
    Fit a classifier and evaluate it on Train, Validation, and Test sets.
    """
    model.fit(X_train, y_train)

    def get_proba(m, X):
        if hasattr(m, "predict_proba"):
            try:
                proba = m.predict_proba(X)
                if proba.shape[1] == 2:  # binary
                    proba = proba[:, 1]
                return proba
            except Exception:
                return None
        return None

    # Train set
    y_train_pred = model.predict(X_train)
    y_train_proba = get_proba(model, X_train)
    evaluate_classifier(y_train, y_train_pred, y_train_proba, dataset_name="Train")

    # Validation set
    if X_val is not None and y_val is not None:
        y_val_pred = model.predict(X_val)
        y_val_proba = get_proba(model, X_val)
        evaluate_classifier(y_val, y_val_pred, y_val_proba, dataset_name="Validation")

    # Test set
    if X_test is not None and y_test is not None:
        y_test_pred = model.predict(X_test)
        y_test_proba = get_proba(model, X_test)
        evaluate_classifier(y_test, y_test_pred, y_test_proba, dataset_name="Test")

    return model


def fit_eval_regressor(model, X_train, y_train, X_val=None, y_val=None, X_test=None, y_test=None):
    """
    Fit a regressor and evaluate it on Train, Validation, and Test sets.
    """
    model.fit(X_train, y_train)

    # Train set
    y_train_pred = model.predict(X_train)
    evaluate_regressor(y_train, y_train_pred, dataset_name="Train")

    # Validation set
    if X_val is not None and y_val is not None:
        y_val_pred = model.predict(X_val)
        evaluate_regressor(y_val, y_val_pred, dataset_name="Validation")

    # Test set
    if X_test is not None and y_test is not None:
        y_test_pred = model.predict(X_test)
        evaluate_regressor(y_test, y_test_pred, dataset_name="Test")

    return model