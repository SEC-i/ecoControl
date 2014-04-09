import time
from simulationmanager import SimulationManager

FORECAST_TIME = 60 * 60 * 24 * 7
SIMULATED_TIME_MAIN =  60 * 60 * 24 * 10

class RuleStrategy(object):
    """A Strategy for chosing the right settings for a simulation by forecasting for a certain amount of time 
    and validating the effects
    required:
    @param env: environment
    @param simulation_manager: the manager with the main simulation"""
    def __init__(self, env, simulation_manager):
        self.env = env
        self.simulation_manager = simulation_manager
        #try not to use plb
        self.simulation_manager.main_simulation.plb.overwrite_workload = 0.0


    def validate_heatstorage_fill(self):
        #forecast for one week
        (sim,measurements) = self.simulation_manager.forecast_for(FORECAST_TIME, blocking=True)
        last_temp = measurements.get_last("hs_temperature")
        
        if last_temp < sim.heat_storage.min_temperature:
            print "under temp"

            def sim_settings(sim):
                sim.cu.overwrite_workload=100.0
    
            (sim1,measurements1) = self.simulation_manager.forecast_for(FORECAST_TIME, blocking=True, pre_start_callback=sim_settings)
            
            
            
            
            
    def step_function(self):
        if self.env.now % (60 * 60 * 24 * 3) == 0.0:
            self.validate_heatstorage_fill()




    def full_power_run(self):
        pass
