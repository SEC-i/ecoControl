from datetime import datetime
from scipy.optimize import fmin_l_bfgs_b, fmin, fmin_tnc, basinhopping
import calendar
import cProfile
import copy
from collections import namedtuple
import numpy as np
from numpy import array

from server.systems.base import BaseEnvironment
from server.models import DeviceConfiguration
from server.forecasting import get_initialized_scenario,\
    DEFAULT_FORECAST_INTERVAL, get_forecast
from server.forecasting.helpers import MeasurementStorage
from server.systems import get_user_function
from server.functions import get_configuration

DEFAULT_FORECAST_INTERVAL = 12 * 3600.0

def simulation_run(code=None):
    
    initial_time = calendar.timegm(datetime(year=2013,month=5,day=15).timetuple())
    env = BaseEnvironment(initial_time)
    configurations = DeviceConfiguration.objects.all()
    
    systems = get_initialized_scenario(env, configurations)
    [hs,pm,cu,plb,tc,ec] = systems
    measurements = MeasurementStorage(env, systems)
    
    user_function = get_user_function(systems, code)

    forward = 30 * 24 * 3600.0 #month
    next_auto_optim = 0.0
    while forward > 0:
        measurements.take_and_cache()

        user_function(*systems)

        # call step function for all systems
        for system in systems:
            system.step()
            
        if next_auto_optim <= 0.0:
            values = auto_optimize(env.now, systems, configurations)
            optimized_config = values["config"]
            
            #hs.target_temperature = optimized_config["target_temperature"]
            cu.overwrite_workload = float(optimized_config["cu_overwrite_workload"])
            
            print "optimization round: ", optimized_config
            
            next_auto_optim = 12 * 3600.0
        plb.overwrite_workload = 0
        #print hs.get_temperature()

        env.now += env.step_size
        forward -= env.step_size
        next_auto_optim -= env.step_size
        
    plot_dataset(measurements.get(), 0, False)
    
    values = get_forecast(forward=forward)
    
    plot_dataset(measurements.get(), 0, True)
        
    



def auto_optimize(initial_time, systems, configurations):
    prices = {}
    prices["gas_costs"] = get_configuration('gas_costs')
    prices["electrical_costs"] = get_configuration('electrical_costs')
    
    rewards  = {}
    rewards["thermal_revenues"] = get_configuration('thermal_revenues')
    rewards["warmwater_revenues"] = get_configuration('warmwater_revenues')
    rewards["electrical_revenues"] = get_configuration('electrical_revenues')
    rewards["feed_in_reward"] = get_configuration('feed_in_reward')

    #target_temperature, cu_overwrite_workload, plb_overwrite_workload
    boundaries = [(0.0,100.0),]
    arguments = (initial_time, systems, prices, rewards)
    
    #find initial approximation for parameters
    class bilance_result:
        def __init__(self, costs, params):
            self.costs = costs
            self.params = params
        def __repr__(self):
            return repr((self.costs, self.params))
    
    results = []
    for cu_load in range(0,100,10):
        #print "testing load ", cu_load
        config = [cu_load,]
        results.append( bilance_result(optim_function(config, *arguments), config))
    results = sorted(results,key=lambda result: result.costs)
        
   
    initial_values = array( results[0].params )
    
    parameters = fmin_l_bfgs_b(optim_function, x0 = initial_values, 
                               args = arguments, bounds = boundaries, 
                               approx_grad = True, factr=10**6, iprint=-1,
                               epsilon=5, maxfun =50)
    
    #parameters = fmin_tnc(optim_function, x0 = initial_values, args = arguments, bounds = boundaries,epsilon=5, approx_grad = True)
    

    named_parameters = {"cu_overwrite_workload":parameters[0][0]}
    
    return {"config": named_parameters}

def optim_function(params, *args):
    (initial_time, systems, prices, rewards) = args
    cost = auto_forecast(initial_time, params, systems, prices, rewards)
    return cost
    

def auto_forecast(initial_time, configurations, systems, prices, rewards, code=None):

    copied_system = copy.deepcopy(systems)
    [hs,pm,cu,plb,tc,ec] = copied_system
    #hs.input_energy = 1000
    ##configure 
    cu.overwrite_workload, = configurations
    
    weighted_temperature = simplified_forecast(initial_time,copied_system,code)
    #list: [SimulatedHeatStorage,SimulatedPowerMeter, SimulatedCogenerationUnit, SimulatedPeakLoadBoiler, SimulatedThermalConsumer, 
    #SimulatedElectricalConsumer
    #maintenance_costs = cu.power_on_count
    gas_costs = (cu.total_gas_consumption + plb.total_gas_consumption) * prices["gas_costs"]
    #thermal_production = cu.total_thermal_production +plb.total_thermal_production
    electric_rewards = pm.fed_in_electricity * rewards["feed_in_reward"] + ec.total_consumption * rewards["electrical_revenues"]
    electric_costs = pm.total_purchased  * prices["electrical_costs"]
    
    thermal_rewards = tc.total_consumed * rewards["thermal_revenues"]
    
    final_cost = electric_costs-electric_rewards + gas_costs - thermal_rewards 
    temp = weighted_temperature
    above_penalty = abs(min(hs.critical_temperature - temp, 0) * 1000)
    below_penalty = abs(max(hs.min_temperature - temp, 0) * 1000)
    
    small_penalties = (temp > hs.target_temperature+5) * 15 + (temp < hs.target_temperature-5) * 5
    
    return final_cost + above_penalty + below_penalty + small_penalties


def simplified_forecast(initial_time, systems, code = None):
    env = systems[0].env
    [hs,pm,cu,plb,tc,ec] = systems
    #print hs.get_temperature()
    #user_function = get_user_function(systems, code)

    forward = DEFAULT_FORECAST_INTERVAL
    steps = 0
    temperatures = []
    while forward > 0:
        # call step function for all systems
        for system in systems:
            system.step()

        env.now += env.step_size
        forward -= env.step_size
        steps += 1
        temperatures.append(hs.get_temperature())
    return np.average(temperatures, weights = range(steps))
        
 
        

def plot_dataset(sensordata,forecast_start=0,block=True):
    import matplotlib.pyplot as plt
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
