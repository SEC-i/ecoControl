from simulation import get_new_simulation
from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values
import sys
import os
import time


class Forecasting:  
    def __init__(self):
       (self.env, self.heat_storage, self.power_meter, self.cu, self.plb, self.thermal_consumer,
        self.electrical_consumer, self.code_executer) = get_new_simulation()

       