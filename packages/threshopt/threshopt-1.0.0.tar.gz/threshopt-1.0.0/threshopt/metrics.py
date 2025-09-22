from sklearn.metrics import confusion_matrix, balanced_accuracy_score

def gmean_score(y_true, y_pred):
    """
    Geometric Mean of sensitivity and specificity.
    """
    cm = confusion_matrix(y_true, y_pred)
    # Evitiamo divisione per zero
    sensitivity = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
    specificity = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
    return (sensitivity * specificity) ** 0.5

def youden_j_stat(y_true, y_pred):
    """
    Youden's J statistic = sensitivity + specificity - 1
    """
    cm = confusion_matrix(y_true, y_pred)
    sensitivity = cm[1,1] / (cm[1,1] + cm[1,0]) if (cm[1,1] + cm[1,0]) > 0 else 0
    specificity = cm[0,0] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
    return sensitivity + specificity - 1

def balanced_acc_score(y_true, y_pred):
    """
    Balanced accuracy (wrapper sklearn for convenience)
    """
    return balanced_accuracy_score(y_true, y_pred)
