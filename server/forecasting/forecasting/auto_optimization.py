from datetime import datetime
from scipy.optimize import fmin_l_bfgs_b

from server.systems.base import BaseEnvironment
from server.models import DeviceConfiguration
from server.forecasting import get_initialized_scenario,\
    DEFAULT_FORECAST_INTERVAL
from server.forecasting.helpers import MeasurementStorage
from server.systems import get_user_function
from server.functions import get_configuration
import calendar
import cProfile
import copy
from collections import namedtuple
from numpy import array

DEFAULT_FORECAST_INTERVAL = 2 * 24 * 3600.0

def auto_optimize(configurations):
    prices = {}
    prices["gas_costs"] = get_configuration('gas_costs')
    prices["electrical_costs"] = get_configuration('electrical_costs')
    
    rewards  = {}
    rewards["thermal_revenues"] = get_configuration('thermal_revenues')
    rewards["warmwater_revenues"] = get_configuration('warmwater_revenues')
    rewards["electrical_revenues"] = get_configuration('electrical_revenues')
    rewards["feed_in_reward"] = get_configuration('feed_in_reward')
    
    initial_time = calendar.timegm(datetime(year=2013,month=5,day=15).timetuple())
    
    env = BaseEnvironment(initial_time)
    systems = get_initialized_scenario(env, configurations)

    #target_temperature, cu_overwrite_workload, plb_overwrite_workload
    config = [60, 100.0,0.0]
    boundaries = [(50.0,80.0), (0.0,100.0), (0.0,100.0)]
    initial_values = array(config)

    arguments = (initial_time, systems, prices, rewards)
    
    parameters = fmin_l_bfgs_b(optim_function, x0 = initial_values, args = arguments, bounds = boundaries, approx_grad = True)
    
    
    named_parameters = {"target_temperature": parameters[0][0], 
                        "cu_overwrite_workload":parameters[0][1], 
                        "plb_overwrite_workload":parameters[0][2]}
    return {"final_bilance" : -parameters[1], "config": named_parameters}

def optim_function(params, *args):
    (initial_time, systems, prices, rewards) = args
    price = auto_forecast(initial_time, params, systems, prices, rewards)
    return price
    

def auto_forecast(initial_time, configurations, systems, prices, rewards, code=None):

    copied_system = copy.deepcopy(systems)
    [hs,pm,cu,plb,tc,ec] = copied_system
    ##configure 
    (hs.target_temperature, cu.overwrite_workload,plb.overwrite_workload) = configurations
    
    get_forecast(initial_time,copied_system,code)
    #list: [SimulatedHeatStorage,SimulatedPowerMeter, SimulatedCogenerationUnit, SimulatedPeakLoadBoiler, SimulatedThermalConsumer, 
    #SimulatedElectricalConsumer
    #maintenance_costs = cu.power_on_count
    gas_costs = (cu.total_gas_consumption + plb.total_gas_consumption) * prices["gas_costs"]
    #thermal_production = cu.total_thermal_production +plb.total_thermal_production
    electric_rewards = pm.fed_in_electricity * rewards["feed_in_reward"] + ec.total_consumption * rewards["electrical_revenues"]
    electric_costs = pm.total_purchased  * prices["electrical_costs"]
    
    thermal_rewards = tc.total_consumed * rewards["thermal_revenues"]
    
    final_cost = electric_costs-electric_rewards + gas_costs - thermal_rewards 
    penalties = hs.undersupplied() * 10000 #big penalty for undersupplied

    return final_cost + penalties



def get_forecast(initial_time, systems, code = None):
    env = systems[0].env
    
    user_function = get_user_function(systems, code)

    forward = DEFAULT_FORECAST_INTERVAL
    while forward > 0:
        #measurements.take_and_cache()

        user_function(*systems)

        # call step function for all systems
        for system in systems:
            system.step()

        env.now += env.step_size
        forward -= env.step_size