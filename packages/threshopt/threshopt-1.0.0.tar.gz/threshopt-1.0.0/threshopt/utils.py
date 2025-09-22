import numpy as np

def normalize_scores(scores):
    """
    Normalize an array-like of scores to [0,1].
    """
    min_score = np.min(scores)
    max_score = np.max(scores)
    if max_score == min_score:
        return np.zeros_like(scores)
    return (scores - min_score) / (max_score - min_score)
