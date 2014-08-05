""" helper methods for forecasting"""
import os
import pickle
import time
from datetime import date,datetime,timedelta
from server.settings import BASE_DIR
from math import cos, pi


def interpolate_year(day):
    """
    input: int between 0,365
    output: float between 0,1
    interpolates a year day to 1=winter, 0=summer
    """
    # shift summer days at 180-365
    # 1'April = 90th day
    day_shift = day + 90
    day_shift %= 365
    day_float = float(day) / 365.0
    interpolation = cos(day_float * pi * 2)
    # shift to 0-1
    return (interpolation / 2) + 0.5

def linear_interpolation(a, b, x):
    return a * (1 - x) + b * x

def perdelta(start, end, delta):
    """ generator function, which outputs dates.
    works like `range(start, stop, step)` for dates

    :param datetime start,end: dates between which to iterate
    :param timedelta delta: the stepwidth
    """
    curr = start
    while curr < end:
        yield curr
        curr += delta

def approximate_index(dataset, findvalue):
    """ Return index  value in dataset, with optimized find procedure.
    This assumes a `dataset` with continuous, increasing values. Typically, these are timestamps.

    :param list dataset: a continuous list of values (f.e. timestamps)
    :param int findvalue: the value, of which to find the index.
    """
    length = len(dataset)
    #aproximate index
    diff = (dataset[1] - dataset[0])
    i = min(int((findvalue - dataset[0])/diff), length -1)
    while i < length and i >= 0:
        if i == length -1:
            return i if dataset[i] == findvalue else -1
        if  dataset[i] == findvalue or (dataset[i] < findvalue and dataset[i+1] > findvalue):
            return i
        elif dataset[i] > findvalue:
            i-=1
        else:
            i+=1
    return -1

def cached_data(name, data_function=None, max_age=0):
    """ store and retrieve data from a cache on the filesystem.
    The function will try to retrieve the cached data. If there is None or
    the data is too old, `data_function` will be called and the result is stored in the cache. 


    :param string name: name of cache file
    :param function data_function: A function, which outputs the data to be stored. 
        If the function is ``None`` and the cache is invalid, the funtion will return ``None``.
    :param int max_age: The maximum age (real time) in seconds, the cache is allowed to have before turning invalid.
    :returns: data or ``None``
    """
    cache_path = cachefile('%s.cache' % name)
    age = cached_data_age(name)
    if age != None and (age < max_age or max_age == 0):
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    if not data_function:
        return None
    data = data_function()
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)
    return data

def cachefile(filename):
        return os.path.join(BASE_DIR,'cache', filename)

def cached_data_age(name):
    cache_path = cachefile('%s.cache' % name)
    if not os.path.exists(cache_path):
        return None
    return time.time() - os.stat(cache_path).st_mtime 

def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)

def values_comparison(actual_value, expected_value):
    return "expected: {0}. got: {1}".format(expected_value, actual_value)