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
        self.thread = None

    def simulation_start(self):
        self.thread = SimulationBackgroundRunner(self.main_simulation.env)
        self.thread.start()


    def forecast_for(self, seconds):

        t0 = time.time()
        new_sim = Simulation.copyconstruct(self.main_simulation)
        print "time for copying a new simulation: ", time.time() - t0, " seconds"


        measurements = MeasurementCache(new_sim.env, new_sim.cu, new_sim.plb, new_sim.heat_storage,
        new_sim.thermal_consumer, new_sim.electrical_consumer)

        thread = SimulationBackgroundRunner(new_sim.env)
        thread.start()
        
        new_sim.env.forward = seconds
        new_sim.env.stop_after_forward = True

        return (new_sim, measurements)

    def is_main_forwarding(self):
        return self.main_simulation.env.forward > 0.0

    def forward_main(self, seconds):
        if self.thread == None or not self.thread.isAlive():
            self.simulation_start()
        
        self.main_simulation.env.forward = seconds
