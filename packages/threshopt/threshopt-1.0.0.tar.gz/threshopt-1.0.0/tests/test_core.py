import pytest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from threshopt import optimize_threshold

def test_optimize_threshold_basic():
    # Crea un dataset bilanciato semplice
    X, y = make_classification(n_samples=200, n_features=5, random_state=42)

    # Modello semplice
    model = LogisticRegression()
    model.fit(X, y)

    # Ottimizza soglia usando F1
    best_thresh, best_val = optimize_threshold(model, X, y, metric=f1_score, plot=False, cm=False, report=False)

    assert 0.0 <= best_thresh <= 1.0, "Threshold should be between 0 and 1"
    assert 0.0 <= best_val <= 1.0, "Metric value should be between 0 and 1"
    assert isinstance(best_thresh, float), "Threshold should be a float"
    assert isinstance(best_val, float), "Metric value should be a float"
