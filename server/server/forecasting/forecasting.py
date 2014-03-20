from simulation import Simulation
from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values
import sys
import os
import time


class Forecasting:  

    def __init__(self):
        self.simulation = Simulation()
        #self.measure_cache = MeasurementCache()


    def forecast_until(self, seconds):
        new_simulation = Simulation.copyconstruct(self.simulation)
        new_simulation.env.forward = seconds





f = Forecasting()
f.forecast_until(60 * 60* 10)
