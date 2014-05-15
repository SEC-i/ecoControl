import os
import pickle
import time
from datetime import date,datetime,timedelta


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)


def approximate_index(dataset, findvalue):
    length = len(dataset)
    #aproximate index
    i = min(int(findvalue - dataset[0]), length -1)
    while i < length and i >= 0:
        if i == length -1:
            return i if dataset[i] == findvalue else -1
        
        if dataset[i] < findvalue and dataset[i+1] > findvalue:
            return i
        elif dataset[i] > findvalue:
            i-=1
        else:
            i+=1
    return -1




def cached_data(name, data_function=None, max_age=60):
    cache_path = cachefile('%s.cache' % name)
    age = cached_data_age(name)
    if (age < max_age or max_age == 0) and os.path.exists(cache_path):
        with open(cache_path, 'rb') as file:
            return pickle.load(file)
    if not data_function:
        return None
    data = data_function()
    cache_data(name, data)
    return data


def cache_data(name, data):
    cache_path = cachefile('%s.cache' % name)
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def cachefile(filename):
        return os.path.join('cache', filename)

def cached_data_age(name):
    cache_path = cachefile('%s.cache' % name)
    if not os.path.exists(cache_path):
        return 0
    return time.time() - os.stat(cache_path).st_mtime