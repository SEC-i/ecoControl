import cProfile
import re

from heat_storage import HeatStorage
from simulation import Simulation
from heating import Heating



SIMULATED_TIME = 3 * 3600
SIMULATION_DURATION = 30

STEP_SIZE = SIMULATED_TIME / SIMULATION_DURATION
TIME_STEP = 0.005



simulation = Simulation(step_size=STEP_SIZE,time_step=TIME_STEP,plotting=True,duration=SIMULATION_DURATION)

cProfile.run('simulation.run()')

        # evenly sampled time at xxx intervals

