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

DEFAULT_FORECAST_INTERVAL = 1 * 24 * 3600.0

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
    measurements = MeasurementStorage(env, systems)
    
    ecosystem = (systems,measurements)
    
    Configurations = namedtuple("configuration", ["target_temperature", "cu_overwrite_workload", "plb_overwrite_workload"])
    config = Configurations(target_temperature=60, cu_overwrite_workload=100.0, plb_overwrite_workload=0.0)
    
    price = auto_forecast(initial_time, config, systems, prices=prices,rewards=rewards)
    #cProfile.runctx("price = auto_forecast(initial_time, configurations, ecosystem, prices=prices,rewards=rewards)", globals(), locals())
    return {"price" : locals()["price"]}

def auto_forecast(initial_time, configurations, ecosystem, prices, rewards, code=None):

    copied_system = copy.deepcopy(ecosystem[0])
    [hs,pm,cu,plb,tc,ec] = copied_system
    ##configure 
    hs.target_temperature =  configurations.target_temperature
    cu.overwrite_workload = configurations.cu_overwrite_workload
    plb.overwrite_workload = configurations.plb_overwrite_workload
    
    
    measurements = get_forecast(initial_time,(copied_system,ecosystem[1]),code)
    #list: [SimulatedHeatStorage,SimulatedPowerMeter, SimulatedCogenerationUnit, SimulatedPeakLoadBoiler, SimulatedThermalConsumer, 
    #SimulatedElectricalConsumer
    #maintenance_costs = cu.power_on_count
    gas_costs = (cu.total_gas_consumption + plb.total_gas_consumption) * prices["gas_costs"]
    #thermal_production = cu.total_thermal_production +plb.total_thermal_production
    electric_rewards = pm.fed_in_electricity * rewards["feed_in_reward"] + ec.total_consumption * rewards["electrical_revenues"]
    electric_costs = pm.total_purchased  * prices["electrical_costs"]
    
    thermal_rewards = tc.total_consumed * rewards["thermal_revenues"]
    
    final_price = electric_rewards - electric_costs + thermal_rewards - gas_costs

    return final_price



def get_forecast(initial_time, ecosystem, code = None):
    systems = ecosystem[0]
    measurements = ecosystem[1]
    env = systems[0].env
    
    user_function = get_user_function(systems, code)

    forward = DEFAULT_FORECAST_INTERVAL
    while forward > 0:
        measurements.take_and_cache()

        user_function(*systems)

        # call step function for all systems
        for system in systems:
            system.step()

        env.now += env.step_size
        forward -= env.step_size
    return measurements.get(delete_after=True)