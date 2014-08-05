"""
This module contains the algorithm for optimizing the costs of energy systems.

"""
from datetime import datetime
from scipy.optimize import fmin_l_bfgs_b
import calendar
import cProfile
import copy
from collections import namedtuple
import numpy as np
from numpy import array

from server.devices.base import BaseEnvironment

from server.functions import get_configuration
import multiprocessing
from multiprocessing.process import Process
import os
from server.settings import BASE_DIR
from csv import writer
import dateutil


DEFAULT_FORECAST_INTERVAL = 1 * 3600.0
"""The interval for how long one auto_optimize will forecast and for how long one specific workload is set.
Note, that this constant also represents a compromise: Shorter intervals can adjust to quick changes,
f.e. electricity demands changes, while longer intervals can incorporate more forecasts, but wont be able
to adjust quickly. 
The interval of one hour lead to good results in our tests.
"""

def auto_optimize(forecast):
    """ Tries to optimize the cost and sets the ``cu.overwrite_workload``

    The method forecasts from ``env.now`` with different cu workloads and finds the one with the
    lowest cost. The length of the forecast is :attr:`DEFAULT_FORECAST_INTERVAL`.
    
    :param forecast: the forecast to be optimized

    """
    optimized_config = find_optimal_config(forecast)
    
    cu = forecast.getCU()
    cu.overwrite_workload = float(optimized_config["cu_overwrite_workload"])
    
    print "optimization round at time: ",datetime.fromtimestamp(forecast.env.now),":", optimized_config
    


def find_optimal_config(initial_time, forecast):
    """ ``Internal Method`` Main method, which optimizes the costs by running a global
    approximation for the best configuration and then running a local minimization
    method on this approximation"""
    prices = {}
    prices["gas_costs"] = get_configuration('gas_costs')
    prices["electrical_costs"] = get_configuration('electrical_costs')
    
    rewards  = {}
    rewards["thermal_revenues"] = get_configuration('thermal_revenues')
    rewards["warmwater_revenues"] = get_configuration('warmwater_revenues')
    rewards["electrical_revenues"] = get_configuration('electrical_revenues')
    rewards["feed_in_reward"] = get_configuration('feed_in_reward')

    arguments = (initial_time, forecast, prices, rewards)
    #find initial approximation for parameters
    results = []
    for cu_load in range(0,100,10):
            config = [cu_load,]
            cost = estimate_cost(config, *arguments)
            results.append(BilanceResult(cost, config))

    boundaries = [(0.0,100.0)]
    #take parameters with lowest cost
    initial_parameters = min(results,key=lambda result: result.cost).params
    
    parameters = fmin_l_bfgs_b(estimate_cost, x0 = array(initial_parameters), 
                               args = arguments, bounds = boundaries, 
                               approx_grad = True, factr=10**4, iprint=0,
                               epsilon=1, maxfun =50)
    cu_workload, = parameters[0]
    
    return {"cu_overwrite_workload":cu_workload}

def estimate_cost(params, *args):
    """``Internal Method`` copies the devices and environment, forwards it and returns the costs.

    :param list params: parameter to be optimized (CU.workload for now)
    :param args: (initial_time, forecast, prices, rewards)

    """
    (initial_time, forecast, prices, rewards) = args
    copied_devices = copy.deepcopy(forecast.devices)

    cu = copied_devices.cu
    cu.overwrite_workload = params[0]
        
    simplified_forecast(cu.env, initial_time, copied_devices)
    
    return total_costs(copied_devices, prices, rewards)

def simplified_forecast(env, initial_time, devices):
    """runs the forward loop only executing the step function"""
    forward = DEFAULT_FORECAST_INTERVAL
    while forward > 0:
        for device in devices:
            device.step()
            
        env.now += env.step_size
        forward -= env.step_size


def total_costs(devices, prices, rewards):
    """``Internal Method`` Returns the cost of a forecast run. The function uses the prices which are stored
    in the db deviceconfiguration. It is also constrained by boundaries, f.e. the heatstorage should
    never go below min temperature.

    :param devices: The devices after the forecast
    :param dict prices, rewards: Cached prices and rewards 
    """
    d = devices
    cu,plb,ec,pm,tc,hs = d.cu,d.plb,d.ec,d.pm,d.tc,d.hs
    #maintenance_costs = cu.power_on_count
    gas_costs = (cu.total_gas_consumption + plb.total_gas_consumption) * prices["gas_costs"]
    own_el_consumption = ec.total_consumption -  pm.fed_in_electricity - pm.total_purchased
    electric_rewards = pm.fed_in_electricity * rewards["feed_in_reward"] + own_el_consumption * rewards["electrical_revenues"]
    electric_costs = pm.total_purchased  * prices["electrical_costs"]
    
    thermal_rewards = tc.total_consumed * rewards["thermal_revenues"]
    
    final_cost = electric_costs-electric_rewards + gas_costs - thermal_rewards 
    temp = hs.get_temperature()
    above_penalty = abs(min(hs.config["critical_temperature"] - temp, 0) * 1000)
    below_penalty = abs(max(hs.config["min_temperature"] - temp, 0) * 1000)
    
    small_penalties = (temp > hs.config["target_temperature"]+5) * 15 + (temp < hs.config["target_temperature"]-5) * 5 
    
    return final_cost + above_penalty + below_penalty + small_penalties


class BilanceResult(object):
    """ wrapper for storing a optimization result"""
    def __init__(self, cost, params):
        self.params = params
        self.cost = cost

####################################
######### multiprocess map #########
####################################


def multiprocess_map(target,params, *args):
    mgr = multiprocessing.Manager()
    dict_threadsafe = mgr.dict()

    jobs = [Process(target=target_wrapper, args=(target,param,index,dict_threadsafe,args)) for index, param in enumerate(params)]
    for job in jobs: job.start()
    for job in jobs: job.join()

    return dict_threadsafe.values()
    
def target_wrapper(target, params, index, dict_threadsafe, args):
    dict_threadsafe[index] = BilanceResult(target(params, *args),params)
    
