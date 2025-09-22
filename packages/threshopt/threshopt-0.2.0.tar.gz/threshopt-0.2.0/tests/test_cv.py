import pytest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from threshopt import optimize_threshold_cv

def test_optimize_threshold_cv_basic():
    # Crea un dataset bilanciato semplice
    X, y = make_classification(n_samples=200, n_features=5, random_state=42)

    # Modello semplice
    model = LogisticRegression()

    # Esegui ottimizzazione soglia con CV
    best_thresh, best_metric = optimize_threshold_cv(model, X, y, metric=f1_score, cv=3)

    assert 0.0 <= best_thresh <= 1.0, "La soglia deve essere tra 0 e 1"
    assert 0.0 <= best_metric <= 1.0, "La metrica deve essere tra 0 e 1"
    assert isinstance(best_thresh, float), "La soglia deve essere float"
    assert isinstance(best_metric, float), "La metrica deve essere float"
