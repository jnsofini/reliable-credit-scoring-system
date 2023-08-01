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
    Returns:
        float: Summy count stats
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
    """Compute the Kolmogorov-Smirnov (KS).
    Parameters
    ----------
    y : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    Returns:
        float: Summy count stats
    """
    return kolmogorov_smirnov(y, y_pred)


def gini(y, y_pred):
    """Compute the Gini using the roc_auc_score
    Parameters
    ----------
    y : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    
    Returns:
        float: Summy count stats
    """
    auroc = roc_auc_score(y, y_pred)
    return auroc * 2 - 1


def auc(y, y_pred):
    """Compute the AUC.
    Parameters
    ----------
    y : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    """
    return roc_auc_score(y, y_pred)


def formatted_metrics(y, y_pred):
    """Gets the fit stats used in the model building.

    These statistics includes:
        - auc
        - gini
        - ks

    Parameters
    ----------
    y : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.

    Returns:
        dict: Summy count stats
    """
    auc_ = auc(y, y_pred)
    gini_ = gini(y, y_pred)
    ks_ = ks(y, y_pred)

    return {
        "auc": f"{float(auc_):.2%}",
        "gini": f"{float(gini_):.2%}",
        "KS": f"{float(ks_):.2%}",
    }


def get_population_dist(y):
    """Takes an array and return stats.

    The stats include
     - number of observations
     - number of events
     - number of non events
     - ratio of events to non-events

    Args:
        y (array | list): Events and non events

    Returns:
        dict: Summy count stats
    """
    pop_count = len(y)
    default_count = sum(y)
    return {
        "Num of observations": int(pop_count),
        "Num of non-events": int(pop_count - default_count),
        "Num of events": int(default_count),
        "Default Rate": f"{float(default_count/pop_count):.2%}",
    }
