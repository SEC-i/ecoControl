import time
from simulationmanager import SimulationManager

FORECAST_TIME = 60 * 60 * 24 * 7
SIMULATED_TIME_MAIN =  60 * 60 * 24 * 10

class RuleStrategy(object):
    """docstring for RuleStrategy"""
    def __init__(self, env, simulation_manager):
        self.env = env
        self.simulation_manager = simulation_manager


    #priorities:
    #1 ensure heatstorage 

    def validate_heatstorage_fill(self):
        #prerequisites: None --> use last settings
        #forecast for one week
        (sim,measurements) = self.simulation_manager.forecast_for(FORECAST_TIME, blocking=True)

        def sim_settings(sim):
            sim.cu.overwrite_workload=100.0

        (sim1,measurements1) = self.simulation_manager.forecast_for(FORECAST_TIME, blocking=True, pre_start_callback=sim_settings )
        #can cu run on this settings for next week?
        if measurements.get_last("hs_temperature") < sim.heatstorage.min_temp:
            #step1: set up full power run
            print "under temp"




    def full_power_run(self):
        pass
