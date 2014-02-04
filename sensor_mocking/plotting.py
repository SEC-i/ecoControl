import matplotlib.pyplot as plt
import numpy as np

from HeatStorage import HeatStorage
from Simulation import Simulation
from Heating import Heating

SIMULATION_DURATION = 5
STEP_SIZE = 200

simulation = Simulation(step_size=STEP_SIZE,plotting=True,duration=SIMULATION_DURATION)
simulation.start()
simulation.join()



# evenly sampled time at 200ms intervals
t = np.arange(0., SIMULATION_DURATION, 0.5)

data = simulation.plotting_data

print data
plt.plot(data[2]["temperature heatStorage"])
plt.xlabel('Simulated time in seconds')
plt.ylabel('Celsius')
plt.title('Temperatures')
plt.axis([0, SIMULATION_DURATION * STEP_SIZE, 0,100])
plt.grid(True)
plt.show()