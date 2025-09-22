from sklearn.metrics import precision_recall_curve, confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
import numpy as np
import warnings

def optimize_threshold(model, X, y_true, metric, multiclass=False, use_predict_if_no_proba=False,
                       plot=True, cm=True, report=True):
    """
    Find the optimal threshold(s) for a classifier by maximizing the specified metric.
    
    Args:
        model: trained classifier with predict_proba, decision_function, or predict
        X: array-like test features
        y_true: array-like true labels
        metric: metric function with signature metric(y_true, y_pred) -> float
        multiclass: if True, optimize thresholds in a One-vs-Rest fashion
        use_predict_if_no_proba: if True, use predict() as proxy if no predict_proba or decision_function
        plot: if True, plots probability distributions
        cm: if True, displays confusion matrix
        report: if True, prints classification report
    
    Returns:
        thresholds: optimal threshold(s), scalar for binary, array for multiclass
        best_metric_values: corresponding metric value(s)
    """

    y_true = np.asarray(y_true)
    classes = np.unique(y_true)
    
    # --- Get probabilistic scores ---
    def get_scores(model, X):
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)
        elif hasattr(model, "decision_function"):
            df = model.decision_function(X)
            df = np.asarray(df)
            if df.ndim == 1:
                # binary: sigmoid
                return np.vstack([1 - 1/(1+np.exp(-df)), 1/(1+np.exp(-df))]).T
            else:
                # multiclass: softmax
                e = np.exp(df - np.max(df, axis=1, keepdims=True))
                return e / (np.sum(e, axis=1, keepdims=True)+1e-12)
        elif hasattr(model, "predict") and use_predict_if_no_proba:
            preds = np.asarray(model.predict(X))
            if preds.ndim == 1:
                # normalize 0-1
                mn, mx = preds.min(), preds.max()
                if mx - mn < 1e-12:
                    p = np.clip(preds, 0, 1)
                else:
                    p = (preds - mn) / (mx - mn)
                return np.vstack([1 - p, p]).T
            else:
                row_sum = preds.sum(axis=1, keepdims=True)
                row_sum[row_sum==0] = 1.0
                return preds / row_sum
        else:
            raise ValueError("Model has neither predict_proba nor decision_function. "
                             "Set use_predict_if_no_proba=True to allow predict() fallback.")
    
    y_scores = get_scores(model, X)

    # --- Function to find best threshold for binary ---
    def best_threshold_binary(y_true_bin, y_prob):
        thresholds = np.linspace(0,1,200)
        best_score = -np.inf
        best_t = 0.5
        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)
            score = metric(y_true_bin, y_pred)
            if score > best_score:
                best_score = score
                best_t = t
        return best_t, best_score

    # --- Optimize ---
    if multiclass:
        if y_scores.ndim == 1:
            raise ValueError("Multiclass requested but model outputs 1D probabilities")
        n_classes = y_scores.shape[1]
        thresholds = np.zeros(n_classes)
        best_scores = np.zeros(n_classes)
        for k in range(n_classes):
            y_bin = (y_true == classes[k]).astype(int)
            t, s = best_threshold_binary(y_bin, y_scores[:,k])
            thresholds[k] = t
            best_scores[k] = s
    else:
        # binary
        if y_scores.ndim == 2 and y_scores.shape[1]==2:
            pos_prob = y_scores[:,1]
        else:
            pos_prob = y_scores.ravel()
        # binarize labels if necessary
        if len(classes)==2:
            pos_label = classes[1]
            y_bin = (y_true == pos_label).astype(int)
        else:
            y_bin = (y_true != 0).astype(int)
        t, s = best_threshold_binary(y_bin, pos_prob)
        thresholds = t
        best_scores = s

    # --- Display ---
    if report or cm or plot:
        if multiclass:
            for k, cls in enumerate(classes):
                print(f"Class {cls} - Best {metric.__name__}: {best_scores[k]:.4f} at threshold {thresholds[k]:.2f}")
                y_pred_k = (y_scores[:,k] >= thresholds[k]).astype(int)
                if report:
                    print(classification_report((y_true==cls).astype(int), y_pred_k))
                if cm:
                    cmatrix = confusion_matrix((y_true==cls).astype(int), y_pred_k)
                    disp = ConfusionMatrixDisplay(cmatrix)
                    disp.plot(cmap=plt.cm.Greens)
                    plt.title(f"Confusion Matrix - Class {cls}")
                    plt.show()
        else:
            print(f"Best {metric.__name__}: {best_scores:.4f} at threshold: {thresholds:.2f}")
            y_pred_best = (pos_prob >= thresholds).astype(int)
            if report:
                print(classification_report(y_bin, y_pred_best))
            if cm:
                cmatrix = confusion_matrix(y_bin, y_pred_best)
                disp = ConfusionMatrixDisplay(cmatrix)
                disp.plot(cmap=plt.cm.Greens)
                plt.title(f"Confusion Matrix at threshold={thresholds:.2f}")
                plt.show()
            if plot:
                plt.figure(figsize=(8,4))
                plt.hist(pos_prob[y_bin==0], bins=30, alpha=0.5, label='Class 0')
                plt.hist(pos_prob[y_bin==1], bins=30, alpha=0.5, label='Class 1')
                plt.axvline(thresholds, color='red', linestyle='--', label='Optimal Threshold')
                plt.xlabel('Predicted probability for positive class')
                plt.ylabel('Frequency')
                plt.title('Predicted Score Distribution')
                plt.legend()
                plt.show()

    return thresholds, best_scores
