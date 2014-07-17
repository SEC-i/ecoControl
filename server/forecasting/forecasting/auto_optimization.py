from datetime import datetime
from scipy.optimize import fmin_l_bfgs_b
import calendar
import cProfile
import copy
from collections import namedtuple
import numpy as np
from numpy import array

from server.systems.base import BaseEnvironment

from server.functions import get_configuration
import multiprocessing
from multiprocessing.process import Process
import os
from server.settings import BASE_DIR
from csv import writer
import dateutil


DEFAULT_FORECAST_INTERVAL = 1 * 3600.0

def simulation_run(start=None,code=None):
    from server.forecasting import get_initialized_scenario
    from server.forecasting.helpers import MeasurementStorage
    from server.models import DeviceConfiguration
    from server.systems import get_user_function
    from server.forecasting import get_forecast
    
    if start==None:
        initial_time = calendar.timegm(datetime(year=2014,month=4,day=20).timetuple())
    else:
        initial_time = start
    

    
    env = BaseEnvironment(initial_time)
    configurations = DeviceConfiguration.objects.all()
    
    systems = get_initialized_scenario(env, configurations)
    [hs,pm,cu,plb,tc,ec] = systems
    measurements = MeasurementStorage(env, systems)
    

    days = 30
    forward = days * 24 * 3600.0 #month
    next_auto_optim = 0.0
    
    #values = get_forecast(initial_time, forward=forward, forecast=False)
    #plot_dataset(values, 0, True)
    
    
    while forward > 0:
        measurements.take_and_cache()

        # call step function for all systems
        for system in systems:
            system.step()
            
        if next_auto_optim <= 0.0:
            auto_optimize(env, systems)
            next_auto_optim = DEFAULT_FORECAST_INTERVAL

        env.now += env.step_size
        forward -= env.step_size
        next_auto_optim -= env.step_size
    
    values_norm = get_forecast(initial_time, forward=days * 24 * 3600.0, forecast=False)


    values_optim = measurements.get()
    return (values_norm, values_optim)



def auto_optimize(env, systems):
    optimized_config = find_optimal_config(env.now, systems)
    [hs,pm,cu,plb,tc,ec] = systems
    
    cu.overwrite_workload = float(optimized_config["cu_overwrite_workload"])
    
    print "optimization round at time: ",datetime.fromtimestamp(env.now),":", optimized_config
    


def find_optimal_config(initial_time, systems):
    prices = {}
    prices["gas_costs"] = get_configuration('gas_costs')
    prices["electrical_costs"] = get_configuration('electrical_costs')
    
    rewards  = {}
    rewards["thermal_revenues"] = get_configuration('thermal_revenues')
    rewards["warmwater_revenues"] = get_configuration('warmwater_revenues')
    rewards["electrical_revenues"] = get_configuration('electrical_revenues')
    rewards["feed_in_reward"] = get_configuration('feed_in_reward')

    arguments = (initial_time, systems, prices, rewards)
    #find initial approximation for parameters
    results = []
    for cu_load in range(0,100,10):
            config = [cu_load,]
            results.append(BilanceResult(estimate_cost(config, *arguments), config))
#     configs = [[v,] for v in range(0,100,10)]
#     results = multiprocess_map(estimate_cost, configs, *arguments)
    boundaries = [(0.0,100.0)]
    initial_parameters = min(results,key=lambda result: result.cost).params
    
    parameters = fmin_l_bfgs_b(estimate_cost, x0 = array(initial_parameters), 
                               args = arguments, bounds = boundaries, 
                               approx_grad = True, factr=10**4, iprint=0,
                               epsilon=1, maxfun =50)
    cu_workload, = parameters[0]
    
    return {"cu_overwrite_workload":cu_workload}

def estimate_cost(params, *args):
    (initial_time, systems, prices, rewards) = args
    copied_system = copy.deepcopy(systems)
    [hs,pm,cu,plb,tc,ec] = copied_system
    
    cu.overwrite_workload = params[0]
        
    simplified_forecast(hs.env, initial_time,copied_system)
    
    return total_costs(copied_system, prices, rewards)

def simplified_forecast(env, initial_time, systems):
    forward = DEFAULT_FORECAST_INTERVAL
    while forward > 0:
        for system in systems:
            system.step()
            
        env.now += env.step_size
        forward -= env.step_size


def total_costs(systems, prices, rewards):
    [hs,pm,cu,plb,tc,ec] = systems
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



def multiprocess_map(target,params, *args):
        mgr = multiprocessing.Manager()
        dict_threadsafe = mgr.dict()

        jobs = [Process(target=target_wrapper, args=(target,param,index,dict_threadsafe,args)) for index, param in enumerate(params)]
        for job in jobs: job.start()
        for job in jobs: job.join()
        
        result = []
        for cost, param in dict_threadsafe.values():
            result.append(BilanceResult(cost, param))
            

        return result
    
def target_wrapper(target, params, index, dict_threadsafe, args):
    cost = target(params, *args)
    dict_threadsafe[index] = [cost,params]
    
class BilanceResult(object):
    def __init__(self, cost, params):
        self.params = params
        self.cost = cost


def plot_dataset(sensordata,forecast_start=0,block=True):
    try:
        import matplotlib.pyplot as plt
    except:
        pass
    #from pylab import *
    fig, ax = plt.subplots()
    for index, dataset in enumerate(sensordata):
        data = [data_tuple[1] for data_tuple in dataset["data"]]
        sim_plot, = ax.plot(range(len(data)), data, label=dataset["device"] + dataset["key"])
    
    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper center', shadow=True)
    
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('medium')
    
    for label in legend.get_lines():
        label.set_linewidth(1.5)
    
    plt.subplots_adjust(bottom=0.2)
    plt.xlabel('Simulated time in seconds')
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.show()
