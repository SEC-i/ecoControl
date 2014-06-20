
from sys import exit
from math import sqrt
import numpy as np
from numpy import array

"""Holt-Winters algorithms to forecasting
Original Gist: Andre Queiroz, modified and extended by MR
Description: This module contains three exponential smoothing algorithms. They are Holt's linear trend method and Holt-Winters seasonal methods (additive and multiplicative).
References:
 Hyndman, R. J.; Athanasopoulos, G. (2013) Forecasting: principles and practice. http://otexts.com/fpp/. Accessed on 07/03/2013.
 Byrd, R. H.; Lu, P.; Nocedal, J. A Limited Memory Algorithm for Bound Constrained Optimization, (1995), SIAM Journal on Scientific and Statistical Computing, 16, 5, pp. 1190-1208."""
 
from scipy.optimize import fmin_l_bfgs_b


def exponential_smoothing_step(input, index, (alpha, beta, gamma), (level, trend, seasonal,forecast), type):
    # 0 = linear, 1 = addditive, 2 = multiplicative
    i = index
    Y = input
    
    a = level
    b = trend
    s = seasonal
    y = forecast
    if type == 0:
        a.append(alpha * Y[i] + (1 - alpha) * (a[i] + b[i]))
        b.append(beta * (a[i + 1] - a[i]) + (1 - beta) * b[i])
        y.append(a[i + 1] + b[i + 1])
    
    elif type == 1:
        a.append(alpha * (Y[i] - s[i]) + (1 - alpha) * (a[i] + b[i]))
        b.append(beta * (a[i + 1] - a[i]) + (1 - beta) * b[i])
        s.append(gamma * (Y[i] - a[i] - b[i]) + (1 - gamma) * s[i])
        y.append(a[i + 1] + b[i + 1] + s[i + 1])
    
    elif type == 2:
        a.append(alpha * (Y[i] / s[i]) + (1 - alpha) * (a[i] + b[i]))
        b.append(beta * (a[i + 1] - a[i]) + (1 - beta) * b[i])
        s.append(gamma * (Y[i] / (a[i] + b[i])) + (1 - gamma) * s[i])
        y.append((a[i + 1] + b[i + 1]) * s[i + 1])
        
        
def onestep_forecasts(params, *args):
    Y = args[0]
    type = args[1]
    test_data = args[3]
 
    if type == 0:
 
        alpha, beta = params
        a = [Y[0]]
        b = [Y[1] - Y[0]]
        y = [a[0] + b[0]]
 
        for i in range(len(Y)):
            
            exponential_smoothing_step(Y, i, (alpha, beta, None), (a, b, None, y), 0)
 
    else:
 
        alpha, beta, gamma = params
        m = args[2]        
        a = [sum(Y[0:m]) / float(m)]
        b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]
 
        if type == 1:
 
            s = [Y[i] - a[0] for i in range(m)]
            y = [a[0] + b[0] + s[0]]
 
            for i in range(len(Y)):
                
                exponential_smoothing_step(Y, i, (alpha, beta, gamma), (a, b, s, y), 1)
 
        elif type == 2:
 
            s = [Y[i] / a[0] for i in range(m)]
            y = [(a[0] + b[0]) * s[0]]
 
            for i in range(len(Y) + len(test_data)):
         
                if i >= len(Y):
                    Y.append((a[-1] + b[-1]) * s[-m])
                    
                exponential_smoothing_step(Y, i, (alpha, beta, gamma), (a, b, s, y), 2)
 
        else:
 
            exit('Type must be either linear, additive or multiplicative')
            
        return (Y[:-len(test_data)],Y[-len(test_data):])
        

def RMSE(params, *args):
    (input, forecast) = onestep_forecasts(params,*args)
    test_data = args[3]
    rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(test_data, forecast)]) / len(test_data))
    #penalty = mean_below_penalty(input,24,params,7*24*2)
    
    return rmse #+ penalty

def MASE(params, *args): 
    (input, forecast) = onestep_forecasts(params,*args)
    
    training_series = np.array(input)
    testing_series = np.array(args[3])
    prediction_series = np.array(forecast)
    n = training_series.shape[0]
    d = np.abs(  np.diff(training_series) ).sum()/(n-1)
    
    errors = np.abs(testing_series - prediction_series )
    #penalty = mean_below_penalty(input,24,params,7*24*2)
    return errors.mean()/d #+ penalty

def mean_below_penalty(input, m, params,fc,value=0):
    outp = multiplicative(input, m, fc, alpha=params[0], beta=params[1], gamma=params[2])
    forecast = np.array(outp[0])
    mean = forecast[len(forecast)/2:].mean()
    inp_mean = np.array(input).mean()
    if abs(inp_mean - mean) > inp_mean or mean < value:
        return 0
    else:
        return abs(mean) - value 
    

     
 
def linear(x, forecast, alpha = None, beta = None):
 
    Y = x[:]
 
    if (alpha == None or beta == None):
 
        initial_values = array([0.3, 0.1])
        boundaries = [(0, 1), (0, 1)]
        type = 0#'linear'
 
        parameters = fmin_l_bfgs_b(RMSE, x0 = initial_values, args = (Y, type), bounds = boundaries, approx_grad = True)
        alpha, beta = parameters[0]
 
    a = [Y[0]]
    b = [Y[1] - Y[0]]
    y = [a[0] + b[0]]
    rmse = 0
 
    for i in range(len(Y) + forecast):
 
        if i == len(Y):
            Y.append(a[-1] + b[-1])
            
        exponential_smoothing_step(Y, i, (alpha, beta, None), (a, b, None, y), 0)
 
    rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(Y[:-forecast], y[:-forecast - 1])]) / len(Y[:-forecast]))

 
    return Y[-forecast:], alpha, beta, rmse
 
def additive(x, m, forecast, alpha = None, beta = None, gamma = None,alpha_bound=0.01):
 
    Y = x[:]
 
    if (alpha == None or beta == None or gamma == None):
 
        initial_values = array([0.3, 0.1, 0.1])
        boundaries = [(0, alpha_bound), (0, 1), (0, 1)]
        type = 1#'additive'
 
        parameters = fmin_l_bfgs_b(RMSE, x0 = initial_values, args = (Y, type, m), bounds = boundaries, approx_grad = True,factr=10**6)
        alpha, beta, gamma = parameters[0]
 
    a = [sum(Y[0:m]) / float(m)]
    b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]
    s = [Y[i] - a[0] for i in range(m)]
    y = [a[0] + b[0] + s[0]]
    rmse = 0
 
    for i in range(len(Y) + forecast):
 
        if i == len(Y):
            Y.append(a[-1] + b[-1] + s[-m])
            
        exponential_smoothing_step(Y, i, (alpha, beta, gamma), (a, b, s, y), 1)
 
    rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(Y[:-forecast], y[:-forecast - 1])]) / len(Y[:-forecast]))
 
    return Y[-forecast:], alpha, beta, gamma, rmse
 
def multiplicative(x, m, forecast, alpha = None, beta = None, gamma = None, initial_values_optimization=[0.002, 0.0, 0.0002], optimization_type="RMSE"):
 
    Y = x[:]
 
    if (alpha == None or beta == None or gamma == None):
 
        initial_values = array(initial_values_optimization)
        boundaries = [(0, 1), (0, 0), (0, 1)]
        type = 2 #'multiplicative'
        optimization_criterion = RMSE if optimization_type == "RMSE" else MASE
        
        train = Y[:-m*2]
        test = Y[-m*2:]
        
        parameters = fmin_l_bfgs_b(optimization_criterion, x0 = initial_values, args = (train, type, m, test), bounds = boundaries, approx_grad = True,factr=10**3)
        alpha, beta, gamma = parameters[0]
    
    Y = train
 
    a = [sum(Y[0:m]) / float(m)]
    b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]
    s = [Y[i] / a[0] for i in range(m)]
    y = [(a[0] + b[0]) * s[0]]
    
    rmse = 0
    
    for i in range(len(Y) + forecast):
 
        if i >= len(x):
            Y.append((a[-1] + b[-1]) * s[-m])
            
        exponential_smoothing_step(Y, i, (alpha, beta, gamma), (a, b, s, y), 2)
        
 
    rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(Y[:-forecast], y[:-forecast - 1])]) / len(Y[:-forecast]))
 
    return Y[-forecast:], alpha, beta, gamma, rmse


