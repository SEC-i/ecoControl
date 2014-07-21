
from sys import exit
from math import sqrt
import numpy as np
from numpy import array
from collections import namedtuple
import csv
import string
from datetime import timedelta, date, datetime
import os
import cProfile as profile
import time
import timeit
#import pyximport
#pyximport.install(setup_args={'include_dirs':[np.get_include()]})
from _Choltwinters import Cdouble_seasonal


class DataLoader(object):
    cached_csv = {}
    
    @classmethod
    def load_from_file(cls,filepath, column_name, delim="\t",date_name="Datum", sampling_interval=600):
        if filepath not in cls.cached_csv:
            if filepath.endswith(".csv"):
                with open(filepath, "rb") as file_obj:
                    reader = csv.reader(file_obj)
                    header = reader.next()
                    if type(header)== list:
                        header = header[0]
                    
                    labels = [string.strip(label) for label in header.split(delim)]
                    columns = {}
                    for label in labels:
                        columns[label] = []
                    
                    for row in reader:
                        _row = row
                        if type(row) == list:
                            _row = row[0]
                        elements = [string.strip(label) for label in _row.split(delim)]
                        for index, element in enumerate(elements):
                            label = labels[index]
                            columns[label].append(element)
                              
                    cls.cached_csv[filepath] = cls.evenly_sampled(columns, date_name,sampling_interval)
        
        return cls.cached_csv[filepath][column_name]
    
    """ 
    @param data: dict with column names as keys
    @param date_name: name of date row
    @param sampling_interval: the number of seconds between each consecutive sample (if standard interval)
    """
    @classmethod
    def evenly_sampled(cls, data, date_name="Datum", sampling_interval=600):
        samples_per_hour = (60 * 60) / sampling_interval
        epsilon = 59  # maximal 59 seconds deviatiation from samplinginterval
        dates = data[date_name]
        
        #empty copy
        output_data = {key : [] for key in data.keys()}
        
        for index, date in enumerate(dates):
            for key in data.keys():
                output_data[key].append(data[key][index])
            
            if index < len(dates) - 1:
                diff = int(dates[index+1]) - int(dates[index])
                time_passed = timedelta(seconds= int(date) - int(dates[0]))         
                
                if abs(diff - sampling_interval) > epsilon:
                    #read from back one week ago, if existent
                    if time_passed >= timedelta(days = 7):
                        back = 7 * 24 * samples_per_hour
                    #else only take last day
                    elif time_passed >= timedelta(days = 1):
                        back = 24 * samples_per_hour
                    else:
                        back = 1
                    
                    history_index = index - back
                    #stop at 10 minutes before next sample
                    stop = diff - sampling_interval + 1
                    for j in range(sampling_interval, stop, sampling_interval):
                        #repeat samples, if time difference is bigger than available data
                        adjusted_index = history_index + j % back
                        for key in data.keys():
                            if key == date_name:
                                output_data[key].append(int(date) + j)
                            else:
                                output_data[key].append(data[key][adjusted_index])
        return output_data

"""Holt-Winters algorithms to forecasting
Original Gist: Andre Queiroz, modified and extended by MR
Description: This module contains three exponential smoothing algorithms. They are Holt's linear trend method and Holt-Winters seasonal methods (additive and multiplicative).
References:
 Hyndman, R. J.; Athanasopoulos, G. (2013) Forecasting: principles and practice. http://otexts.com/fpp/. Accessed on 07/03/2013.
 Byrd, R. H.; Lu, P.; Nocedal, J. A Limited Memory Algorithm for Bound Constrained Optimization, (1995), SIAM Journal on Scientific and Statistical Computing, 16, 5, pp. 1190-1208."""
 
#from scipy.optimize import fmin_l_bfgs_b


def exponential_smoothing_step(input, index, params,
                               (forecast, level, trend, seasonal, seasonal2),
                               hw_type ):
    # 0 = linear, 1 = addditive, 2 = multiplicative, 3 = double seasonal
    i = index
    Y = input
    
    a = level
    b = trend
    s = seasonal
    s2 = seasonal2
    y = forecast
    if hw_type == 0:
        a.append(params.alpha * Y[i] + (1 - params.alpha) * (a[i] + b[i]))
        b.append(params.beta * (a[i + 1] - a[i]) + (1 - params.beta) * b[i])
        y.append(a[i + 1] + b[i + 1])
    
    elif hw_type == 1:
        a.append(params.alpha * (Y[i] - s[i]) + (1 - params.alpha) * (a[i] + b[i]))
        b.append(params.beta * (a[i + 1] - a[i]) + (1 - params.beta) * b[i])
        s.append(params.gamma * (Y[i] - a[i] - b[i]) + (1 - params.gamma) * s[i])
        y.append(a[i + 1] + b[i + 1] + s[i + 1])
    
    elif hw_type == 2:
        a.append(params.alpha * (Y[i] / s[i]) + (1 - params.alpha) * (a[i] + b[i]))
        b.append(params.beta * (a[i + 1] - a[i]) + (1 - params.beta) * b[i])
        s.append(params.gamma * (Y[i] / (a[i] + b[i])) + (1 - params.gamma) * s[i])
        y.append((a[i + 1] + b[i + 1]) * s[i + 1])
        
    elif hw_type == 3:
        #see Short-term electricity demand forecasting using 
        #double seasonal exponential smoothing (Tayler 2003)
        a.append( params.alpha * (Y[i] - s2[i] - s[i]) + (1 - params.alpha) * (a[i]))
        s.append(params.delta *  (Y[i] - a[i] - s2[i]) + (1 - params.delta) * s[i])
        s2.append(params.gamma * (Y[i] - a[i] - s[i]) + (1 - params.gamma) * s2[i])
        autocorr = params.autocorrelation * (Y[i] - (a[i] + s[i] + s2[i]))
        y.append(a[i + 1] + s[i + 1] + s2[i + 1] + autocorr)

        
def _holt_winters(params, *args):
    train = args[0][:]
    hw_type = args[1]
    m = args[2]
    test_data = args[3]
 
    if hw_type == 0:

        alpha, beta = params
        linear(train, len(test_data), alpha, beta)

    if hw_type == 1:
        alpha, beta, gamma = params
        forecast, params, onestepfcs = additive(train, m, len(test_data), alpha=alpha,beta=beta,gamma=gamma)
    elif hw_type == 2:
        alpha, beta, gamma = params
        forecast, params, onestepfcs = multiplicative(train, m, len(test_data), alpha=alpha,beta=beta,gamma=gamma)

    elif hw_type == 3:
            alpha, beta, gamma, delta, autocorrelation = params
            forecast, params, onestepfcs = double_seasonal(train, m[0],m[1], len(test_data), 
                                                             alpha=alpha,beta=beta,gamma=gamma,delta=delta, 
                                                             autocorrelation=autocorrelation)
    else:
    
        exit('type must be either linear, additive, multiplicative or double seasonal')
    
    return forecast, onestepfcs
        

def MSE(params, *args):
    forecast, onestepfcs = _holt_winters(params,*args)
    test_data = args[3]
    train = args[0]
    mse_outofsample = sum([(m - n) ** 2 for m, n in zip(test_data, forecast)]) / len(test_data)
    mse_insample = sum([(m - n) ** 2 for m, n in zip(train, onestepfcs)]) / len(train)
    
    return mse_insample + mse_outofsample

def MASE(params, *args): 
    input = args[0]
    forecast = _holt_winters(params,*args)
    
    training_series = np.array(input)
    testing_series = np.array(args[3])
    prediction_series = np.array(forecast)
    n = training_series.shape[0]
    d = np.abs(  np.diff(training_series) ).sum()/(n-1)
    
    errors = np.abs(testing_series - prediction_series )
    return errors.mean()/d
     
 
def linear(x, forecast, alpha = None, beta = None):
 
    Y = x[:]
 
    if (alpha == None or beta == None):
 
        initial_values = array([0.3, 0.1])
        boundaries = [(0, 1), (0, 1)]
        hw_type = 0#'linear'
 
        parameters = fmin_l_bfgs_b(MSE, x0 = initial_values, args = (Y, hw_type), bounds = boundaries, approx_grad = True)
        alpha, beta = parameters[0]
 
    a = [Y[0]]
    b = [Y[1] - Y[0]]
    y = [a[0] + b[0]]
    
    named_parameters = namedtuple("Linear", ["alpha", "beta"], False)(alpha,beta)

    for i in range(len(Y) + forecast):
 
        if i == len(Y):
            Y.append(a[-1] + b[-1])
            
        exponential_smoothing_step(Y, i, named_parameters, (a, b, None, y), 0)
 
    return Y[-forecast:], alpha, beta, y[:-forecast]
 
def additive(x, m, forecast, alpha = None, beta = None, gamma = None):
 
    Y = x[:]
 
    if (alpha == None or beta == None or gamma == None):
 
        initial_values = array([0.3, 0.1, 0.1])
        boundaries = [(0, 1), (0, 1), (0, 1)]
        hw_type = 1#'additive'
 
        parameters = fmin_l_bfgs_b(MSE, x0 = initial_values, args = (Y, hw_type, m), bounds = boundaries, approx_grad = True,factr=10**6)
        alpha, beta, gamma = parameters[0]
 
    a = [sum(Y[0:m]) / float(m)]
    b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]
    s = [Y[i] - a[0] for i in range(m)]
    y = [a[0] + b[0] + s[0]]
    named_parameters = namedtuple("Additive", ["alpha", "beta","gamma"], False)(alpha,beta,gamma)
    
    for i in range(len(Y) + forecast):
 
        if i == len(Y):
            Y.append(a[-1] + b[-1] + s[-m])
            
        exponential_smoothing_step(Y, i, named_parameters, (y, a, b, s, None), 1)
 
    return Y[-forecast:], (alpha, beta, gamma), y[:-forecast]
 
def multiplicative(x, m, forecast, alpha=None, beta=None, gamma=None, initial_values_optimization=[0.002, 0.0, 0.0002], optimization_type="MSE"):
 
    Y = x[:]
    test_series = []
    if (alpha == None or beta == None or gamma == None):
 
        initial_values = array(initial_values_optimization)
        boundaries = [(0, 1), (0, 0.05), (0, 1)]
        hw_type = 2 #'multiplicative'
        optimization_criterion = MSE if optimization_type == "MSE" else MASE
        
        train_series = Y[:-m*2]
        test_series = Y[-m*2:]
        
        Y = train_series

        parameters = fmin_l_bfgs_b(optimization_criterion, x0 = initial_values, args = (train_series, hw_type, m, test_series), 
                                   bounds = boundaries, approx_grad = True,factr=10**3)
        alpha, beta, gamma = parameters[0]
    

    a = [sum(Y[0:m]) / float(m)]
    b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]
    s = [Y[i] / a[0] for i in range(m)]
    y = [(a[0] + b[0]) * s[0]]
    
    named_parameters = namedtuple("Multiplicative", ["alpha", "beta","gamma"], False)(alpha,beta,gamma)

    for i in range(len(Y) + forecast+len(test_series)):
 
        if i >= len(Y):
            Y.append((a[-1] + b[-1]) * s[-m])
            
        exponential_smoothing_step(Y, i, named_parameters, (y, a, b, s, None), 2)
        
    return Y[-forecast:], (alpha, beta, gamma), y[:-forecast]


#m = intraday, m2 = intraweek seasonality
def double_seasonal(x, m, m2, forecast, alpha = None, beta = None, gamma = None,delta=None,
                    autocorrelation=None, initial_values_optimization=[0.1, 0.0, 0.2, 0.2, 0.9],
                     optimization_type="MSE", beta_bound=0.0):
 
    Y = x[:]
    test_series = []
    if (alpha == None or beta == None or gamma == None):
 
        initial_values = array(initial_values_optimization)
        boundaries = [(0, 1), (0, beta_bound), (0, 1), (0,1), (0,1)]
        hw_type = 3 #'double seasonal
        optimization_criterion = MSE if optimization_type == "MSE" else MASE
        
        train_series = Y[:-m2*1]
        test_series = Y[-m2*1:]
        Y = train_series

        parameters = fmin_l_bfgs_b(optimization_criterion, x0 = initial_values, args = (train_series, hw_type, (m,m2), test_series), 
                                   bounds = boundaries, approx_grad = True,factr=10**3)
        alpha, beta, gamma, delta, autocorrelation = parameters[0]
    
    all_length = [0 for i in range(len(Y) + forecast+len(test_series))]
    a = [sum(Y[0:m]) / float(m)]
    #b = [(sum(Y[m2:2 * m2]) - sum(Y[0:m2])) / (m2) ** 2] + all_length
    s = [Y[i] / a[0] for i in range(m)]
    s2 = [Y[i] / a[0] for i in range(0,m2,m)] 
    y = [a[0]+ s[0] + s2[0]] 
    #named_parameters = namedtuple("Multiplicative", ["alpha", "beta","gamma","delta","autocorrelation"], False)(alpha,beta,gamma,delta,autocorrelation)
    for i in range(len(Y) + forecast+len(test_series)):

        if i >= len(Y):
            Y.append(a[-1]+ s[-m] + s2[-m2])
            
        a.append( alpha * (Y[i] - s2[i] - s[i]) + (1 - alpha) * (a[i]))
        s.append(delta *  (Y[i] - a[i] - s2[i]) + (1 - delta) * s[i])
        s2.append(gamma * (Y[i] - a[i] - s[i]) + (1 - gamma) * s2[i])
        autocorr = autocorrelation * (Y[i] - (a[i] + s[i] + s2[i]))
        y.append(a[i + 1] + s[i + 1] + s2[i + 1] + autocorr)
        
    return Y[-forecast:], (alpha, beta, gamma, delta, autocorrelation), y[:-forecast]

def make_hourly(data, samples_per_hour):
        """ aggregates data series to 1hourly data.

        :param list data: the series
        :param int samples_per_hour: number of samples per hour contained in `data`

        :returns: list of 1hourly data
        """
        def avg(hour):
            sum = 0
            for i in range(samples_per_hour):
                sum += data[hour * samples_per_hour + i]
            return sum / samples_per_hour

        hours = len(data) / samples_per_hour
        return [avg(i) for i in range(hours)]

def timing(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr):
    for i in range(1000):
        forecast_values, p,insample = double_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)
def timing2(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr):
    for i in range(1000):
        forecast_values, p,insample = Cdouble_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)


def init_all():
    path = "Electricity_1.1-12.6.2014.csv"
    raw_data = DataLoader.load_from_file(path, "Strom - Verbrauchertotal (Aktuell)",delim="\t")
    ind = len(raw_data) / 2
    kW_data = make_hourly([float(val) / 1000.0 for val in raw_data],6) #cast to float and convert to kW
    dates = [int(d) for d in DataLoader.load_from_file(path, "Datum", "\t")]
    start_index = 0
    train_len= 24*7*8
    global trainingdata
    trainingdata = kW_data[start_index:start_index+train_len]
    test_start = start_index+train_len 
    testdata = kW_data[test_start:test_start+7*24*2]
    start_forecast = test_start*3600
    end_forecast = start_forecast + len(testdata) * 3600

    global alpha,beta,gamma,delta,autocorr,m,m2,fc
    alpha = 0.0000001
    beta = 0.0
    gamma = 0.05
    delta = 0.01
    autocorr = 0.5
    #plot_dataset(values)
    m = 24
    m2 = 24 * 7
    #forecast length
    fc = 1000

if __name__ == "__main__":
    init_all()
    #forecast_values0, p,insample = double_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)
    #forecast_values1, p,insample = Cdouble_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)
    #hw = CHoltWinters(trainingdata, m,m2,fc)
    #forecast_values1, p,insample = hw.double_seasonal(alpha,beta,gamma,delta,autocorr)
    #print forecast_values0
    #print forecast_values1
    #print sum([(m - n) ** 2 for m, n in zip(forecast_values0, forecast_values1)]) / len(forecast_values0)
    #profile.runctx("timing(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)",globals(),locals())
    #profile.runctx("timing2(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)",globals(),locals())
    setup = """import autooptim_otherversion as o;o.init_all()"""

    t =  timeit.Timer("o.Cdouble_seasonal(o.trainingdata, o.m,o.m2,o.fc, o.alpha,o.beta,o.gamma,o.delta,o.autocorr)", setup=setup)
    print t.timeit(number=10000)
    #print forecast_values
    #import numpy.distutils.system_info as sysinfo
    #sysinfo.show_all()