# -*- coding: utf-8 -*-
from numpy import array, ones, linalg, random

try:
    from scipy.stats import linregress
except ImportError:
    linregress = None

try:
    from scipy.optimize import fmin
except ImportError:
    fmin = None


def aproximate_lineal1(x_exp, y_exp):
    """
    Lineal regression tendency line obtained from X and Y values.

    Borrowed from http://glowingpython.blogspot.com/2012/03/linear-regression-with-numpy.html

    :param x_exp: X values
    :param y_exp: Y values
    :return: tendency line
    """

    a_matrix = array([x_exp, ones(x_exp.shape[0])])

    # Parameters
    w = linalg.lstsq(a_matrix.T, y_exp)[0]
    line = w[0]*x_exp + w[1]
    return line


def aproximate_lineal2(x_exp, y_exp):
    """
    Lineal regression tendency line obtained from X and Y values.

    Borrowed from http://glowingpython.blogspot.com/2012/03/linear-regression-with-numpy.html

    :param x_exp: X values
    :param y_exp: Y values
    :return: tendency line
    """
    if linregress is None:
        return aproximate_lineal1(x_exp, y_exp)

    slope, intercept, r_value, p_value, std_err = linregress(x_exp, y_exp)
    line = slope*x_exp + intercept
    return line


def aproximate_poly(x_exp, y_exp):
    """
    Curve fitting

    Borrowed from http://glowingpython.blogspot.it/2011/05/curve-fitting-using-fmin.html

    :param x_exp: X values
    :param y_exp: Y values
    :return: tendency line
    """
    if fmin is None:
        return

    fp = lambda c, x: c[0] + c[1]*x + c[2]*x*x + c[3]*x*x*x
    err = lambda p, x, y: (abs((fp(p, x) - y))).sum()
    p0 = random.rand(4)
    p = fmin(err, p0, args=(x_exp, y_exp))

    return fp(p, x_exp)

aproximate = aproximate_lineal2
aproximate_lineal = aproximate_lineal2