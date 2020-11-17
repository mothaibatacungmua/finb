import numpy as np
from sklearn.linear_model import LinearRegression
from cvxopt import matrix, solvers


def mean_var_opt(f:np.ndarray, specific_risk_mat: np.ndarray, factor_mat: np.ndarray, risk_aversion=1) -> np.ndarray:
    """ Solve the quaratic optimization problem

    Maximize f'w - 1/2 risk_aversion * (w'*specific_risk_mat*w)
    or Minimize 1/2 risk_aversion * (w'*specific_risk_mat*w) - f'w
    subject to: w'. i = 0, and w'.factor_mat = 0

    :param f: Forecast return, (num_stocks,)
    :param specific_risk_mat: Diagonal matrix (num_stocks, num_stocks)
    :param factor_mat: Factor matrix (num_stocks, num_factors)
    :param risk_aversion: Risk Aversion parameter
    :return: optimization weights, (adjusted forecast)
    """

    P = matrix(risk_aversion * specific_risk_mat)
    q = matrix(-f)

    i = matrix(np.ones([factor_mat.shape[0], 1]))
    b = matrix(np.zeros([factor_mat.shape[1]+1]))

    A = matrix(np.concatenate([factor_mat, i], axis=1).transpose([1,0]))

    G = None
    h = None

    sol = solvers.qp(P, q, G, h, A, b)

    return np.array(sol['x'])


def adjusted_return(returns:np.ndarray, specific_risk_mat: np.ndarray, factor_mat: np.ndarray):
    """Compute adjusted return

    :param returns:
    :param specific_risk_mat:
    :param factor_mat: Factor matrix (num_stocks, num_factors)
    :return:
    """
    result = LinearRegression().fit(factor_mat, returns)
    pred = result.predict(factor_mat)
    d = np.diagonal(specific_risk_mat)
    ret = (returns - pred)/d

    return ret


