from simulation import Simulation
from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values
import sys
import os
import time
from copy import deepcopy


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

        t0 = time.time()
        new_simulation = copy.deepcopy(self.main_simulation) #Simulation.copyconstruct(self.main_simulation)
        print "time for copying a new simulation: ", time.time() - t0, " seconds"


        measurements = MeasurementCache(new_simulation.env, new_simulation.cu, new_simulation.plb, new_simulation.heat_storage,
        new_simulation.thermal_consumer, new_simulation.electrical_consumer)

        thread = SimulationBackgroundRunner(new_simulation.env)
        thread.start()
        
        new_simulation.env.forward = seconds
        new_simulation.env.stop_after_forward = True

        return (new_simulation, measurements)