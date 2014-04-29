import os
import pickle
import time

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