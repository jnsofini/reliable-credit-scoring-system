import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def kolmogorov_smirnov(y, y_pred):
    """Compute the Kolmogorov-Smirnov (KS).
    Parameters
    ----------
    y : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    """

    n_samples = y.shape[0]
    n_event = np.sum(y)
    n_nonevent = n_samples - n_event

    idx = y_pred.argsort()
    yy = y[idx]
    pp = y_pred[idx]

    cum_event = np.cumsum(yy)
    cum_population = np.arange(0, n_samples)
    cum_nonevent = cum_population - cum_event

    p_event = cum_event / n_event
    p_nonevent = cum_nonevent / n_nonevent

    p_diff = p_nonevent - p_event
    ks_score = np.max(p_diff)

    return ks_score


def ks(y, y_pred):
    return kolmogorov_smirnov(y, y_pred)


def gini(y, y_pred):
    auroc = roc_auc_score(y, y_pred)
    return auroc * 2 - 1


def auc(y, y_pred):
    return roc_auc_score(y, y_pred)


def formatted_metrics(y, y_pred):
    """Gets the fit stats used in out model building"""
    auc_ = auc(y, y_pred)
    gini_ = gini(y, y_pred)
    ks_ = ks(y, y_pred)

    return {"auc": f"{float(auc_):.2%}", "gini": f"{float(gini_):.2%}", "KS": f"{float(ks_):.2%}"}


def get_population_dist(y):
    pop_count = len(y)
    default_count = sum(y)
    return {
        "Num of observations": int(pop_count),
        "Num of non-events": int(pop_count - default_count),
        "Num of events": int(default_count),
        "Default Rate": f"{float(default_count/pop_count):.2%}",
    }
