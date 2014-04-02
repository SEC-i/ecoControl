from simulation import Simulation
from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values
import sys
import os
import time


class SimulationManager:  

    def __init__(self):
        self.main_simulation = Simulation()

        sim = self.main_simulation
        self.measurements = MeasurementCache(sim.env, sim.cu, sim.plb, sim.heat_storage,
        sim.thermal_consumer, sim.electrical_consumer)

    def simulation_start(self):
        thread = SimulationBackgroundRunner(self.main_simulation.env)
        thread.start()


    def forecast_for(self, seconds):

        new_simulation = Simulation.copyconstruct(self.main_simulation)
        new_simulation.env.forward = seconds
        new_simulation.env.stop_after_forward = True

        thread = SimulationBackgroundRunner(new_simulation.env)
        thread.start()

        return new_simulation


# f = SimulationManager()
# f.forecast_for(60 * 60* 10)
