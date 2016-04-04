#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
from scipy.optimize.minpack import leastsq

"""Fit 1D-data to arbitrary specified objective function.
Copyright (C) 2008 Jochen K�pper
"""
__author__ = "Jochen K�pper"
__version__ = "1.0 (03.10.2008)"

# various functions
def single_exponential(A, t):
    """Calculate the values y[i] of a single exponential function 
        y = A[0] + A[1]*exp(-t/A[2]) 
    at all times t[i]"""
    return A[0] + A[1] * numpy.exp(t/A[2])

def single(A, t):
    """Calculate the values y[i] of a single exponential function 
        y = A[0] + A[1]*exp(-t/A[2]) 
    at all times t[i]"""
    return A[0] + A[1] * t/A[2]

def objective(A, t, y0, func):
    """Calculate residual deviation of simulated data and experimental data."""
    return y0 - func(A, t)

def aproximate(t_exp, y_exp, test=False):
    # define cost function - adapt to your usage
    #
    # single exponential
    function = single_exponential
    x0 = [0, y_exp[-1], t_exp.shape[0]]
    param = (t_exp, y_exp, function)

    # perform least squares fit
    A_final, cov_x, infodict, mesg, ier = leastsq(objective, x0, args=param, full_output=True)
    if ier != 1:
        print "No fit! %s " % mesg 
        return None
    y_final = function(A_final, t_exp)
    chi2 = sum((y_exp-y_final)**2 / y_final)
    if not test:
        return y_final
    else:
        return y_final,chi2

def aproximate_lineal(t_exp, y_exp, test=False):
    # define cost function - adapt to your usage
    #
    # single exponential
    function = single
    x0 = [0, y_exp[-1], t_exp.shape[0]]
    param = (t_exp, y_exp, function)

    # perform least squares fit
    A_final, cov_x, infodict, mesg, ier = leastsq(objective, x0, args=param, full_output=True)
    if ier != 1:
        print "No fit! %s " % mesg 
        return None
    y_final = function(A_final, t_exp)
    chi2 = sum((y_exp-y_final)**2 / y_final)
    if not test:
        return y_final
    else:
        return y_final,chi2