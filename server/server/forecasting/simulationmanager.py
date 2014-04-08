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

    def simulation_start(self, blocking = False):
        self.thread = SimulationBackgroundRunner(self.main_simulation.env)
        self.thread.start()
        if blocking:
            #wait on forwarding to end
            #cant use thread.join() here, because sim will not stop after forward
            while self.is_main_forwarding(): 
                time.sleep(0.2) 


    """ create a new simulation instance, which copies the settings and timepoint of the main simulation and starts
    forwarding for specified seconds.
    required:
    @param seconds: seconds to forward
    optional:
    @param blocking: function blocks until forecast is done if True, otherwise will run threaded
    @param preStartCallback: pass a callback, which will receive the simulation  instance before it is started
    useful for passing settings before starting the simulation. f.e : 
    setStuff(sim):
        sim.stuff = 123

    forecast_for(1,preStartCallback=setStuff)
    @param copy_sim: a simulation to copy, use the main simulation if this is left out
    
    """
    def forecast_for(self, seconds,blocking=False,pre_start_callback=None, copy_sim=None):

        t0 = time.time()
        if copy_sim != None:
            new_sim = Simulation.copyconstruct(copy_sim)
        else:
            new_sim = Simulation.copyconstruct(self.main_simulation)
        print "time for copying a new simulation: ", time.time() - t0, " seconds"


        measurements = MeasurementCache(new_sim.env, new_sim.cu, new_sim.plb, new_sim.heat_storage,
        new_sim.thermal_consumer, new_sim.electrical_consumer)

        new_sim.env.forward = seconds
        new_sim.env.stop_after_forward = True

        if blocking == False:
            thread = SimulationBackgroundRunner(new_sim.env)
            thread.start()
        else:
            new_sim.env.run()

        return (new_sim, measurements)
    

    def is_main_forwarding(self):
        return self.main_simulation.env.forward > 0.0

    def forward_main(self, seconds, blocking=False):
        self.main_simulation.env.forward = seconds
        if self.thread == None or not self.thread.isAlive():
            self.simulation_start(blocking)
        
