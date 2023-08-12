"""
Metrics to measure performance of model.
"""
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def kolmogorov_smirnov(y_true, y_pred):
    # pylint: disable=invalid-name
    """Compute the Kolmogorov-Smirnov (KS).
    Parameters
    ----------
    y_true : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    Returns:
        float: Summy count stats
    """

    n_samples = y_true.shape[0]
    n_event = np.sum(y_true)
    n_nonevent = n_samples - n_event

    idx = y_pred.argsort()
    yy = y_true[idx]  # pylint: disable=invalid-name
    # pp = y_pred[idx]

    cum_event = np.cumsum(yy)
    cum_population = np.arange(0, n_samples)
    cum_nonevent = cum_population - cum_event

    p_event = cum_event / n_event
    p_nonevent = cum_nonevent / n_nonevent

    p_diff = p_nonevent - p_event
    ks_score = np.max(p_diff)

    return ks_score


def ks(y_true, y_pred):  # pylint: disable=invalid-name
    """Compute the Kolmogorov-Smirnov (KS).
    Parameters
    ----------
    y_true : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    Returns:
        float: Summy count stats
    """
    return kolmogorov_smirnov(y_true, y_pred)


def gini(y_true, y_pred):
    """Compute the Gini using the roc_auc_score
    Parameters
    ----------
    y_true : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.

    Returns:
        float: Summy count stats
    """
    auroc = roc_auc_score(y_true, y_pred)
    return auroc * 2 - 1


def auc(y_true, y_pred):
    """Compute the AUC.
    Parameters
    ----------
    y_true : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.
    """
    return roc_auc_score(y_true, y_pred)


def formatted_metrics(y_true, y_pred):
    """Gets the fit stats used in the model building.

    These statistics includes:
        - auc
        - gini
        - ks

    Parameters
    ----------
    y_true : array-like, shape = (n_samples,)
        Array with the target labels.
    y_pred : array-like, shape = (n_samples,)
        Array with predicted probabilities.

    Returns:
        dict: Summy count stats
    """
    auc_ = auc(y_true, y_pred)
    gini_ = gini(y_true, y_pred)
    ks_ = ks(y_true, y_pred)

    # return {
    #     "auc": f"{float(auc_):.2%}",
    #     "gini": f"{float(gini_):.2%}",
    #     "KS": f"{float(ks_):.2%}",
    # }
    return {
        "auc": f"{float(auc_):.2}",
        "gini": f"{float(gini_):.2}",
        "KS": f"{float(ks_):.2}",
    }


def get_population_dist(y_true):
    """Takes an array and return stats.

    The stats include
     - number of observations
     - number of events
     - number of non events
     - ratio of events to non-events

    Args:
        y_true (array | list): Events and non events

    Returns:
        dict: Summy count stats
    """
    pop_count = len(y_true)
    default_count = sum(y_true)
    return {
        "Num of observations": int(pop_count),
        "Num of non-events": int(pop_count - default_count),
        "Num of events": int(default_count),
        "Default Rate": f"{float(default_count/pop_count):.2%}",
    }


def sensivity_specifity_cutoff(y_true, y_score):
    '''Find data-driven cut-off for classification

    Cut-off is determied using Youden's index defined as sensitivity + specificity - 1.

    Parameters
    ----------

    y_true : array, shape = [n_samples]
        True binary labels.

    y_score : array, shape = [n_samples]
        Target scores, can either be probability estimates of the positive class,
        confidence values, or non-thresholded measure of decisions (as returned by
        “decision_function” on some classifiers).

    References
    ----------

    Ewald, B. (2006). Post hoc choice of cut points introduced bias to diagnostic research.
    Journal of clinical epidemiology, 59(8), 798-801.

    Steyerberg, E.W., Van Calster, B., & Pencina, M.J. (2011). Performance measures for
    prediction models and markers: evaluation of predictions and classifications.
    Revista Espanola de Cardiologia (English Edition), 64(9), 788-794.

    Jiménez-Valverde, A., & Lobo, J.M. (2007). Threshold criteria for conversion of probability
    of species presence to either–or presence–absence. Acta oecologica, 31(3), 361-369.
    '''
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    idx = np.argmax(tpr - fpr)
    return thresholds[idx]
