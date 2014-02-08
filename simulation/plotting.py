import matplotlib.pyplot as plt
import numpy as np

from heat_storage import HeatStorage
from simulation import Simulation
from heating import Heating


SIMULATED_TIME = 12 * 3600
SIMULATION_DURATION = 10

STEP_SIZE = SIMULATED_TIME / SIMULATION_DURATION
#timestep now denotes, how often values are written for plotting, internal shorter timesteos are used
TIME_STEP = 0.005


class Plotting(object):
    def __init__(self):
        self.simulation = Simulation(step_size=STEP_SIZE,time_step=TIME_STEP,plotting=True,duration=SIMULATION_DURATION)
        self.simulation.start()
        self.simulation.join()
        

        self.data = self.simulation.plotting_data
        # evenly sampled time at xxx intervals
        self.t = np.arange(0.0, SIMULATED_TIME,STEP_SIZE * TIME_STEP)        
        #cut to the actual length of simulation data
        self.t = self.t[0:len(self.data[1]["workload.0"])]
        
        self.plot_dataset(1, "Energy Conversion")
        plt.show(block=False)
        self.plot_dataset(2, "Temperatures")
        plt.show(block=True)    
    
    def get_line_name(self,concat_name):
        parts = concat_name.split(".")
        dev_id = int(parts[1])
        device = self.simulation.devices[dev_id]
        sensor = self.simulation.get_sensor(dev_id,sensor_name=parts[0])
        return sensor.name + " of " + device.name +  " in " +  sensor.unit


    def plot_dataset(self,data_id,title):

        
        fig, ax = plt.subplots()
        
        for name,sensorvals in self.data[data_id].items():
            if name != "unit":
                line_label = self.get_line_name(name)
                ax.plot(self.t,sensorvals,label=line_label)
        
        # Now add the legend with some customizations.
        legend = ax.legend(loc='upper center', shadow=True)
        
        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
        
        # Set the fontsize
        for label in legend.get_texts():
            label.set_fontsize('medium')
        
        for label in legend.get_lines():
            label.set_linewidth(1.5)  # the legend line widt
        #plt.plot(t,data[1]["workload BHKW"])
        
        
        plt.xlabel('Simulated time in seconds')
        #plt.ylabel('Celsius')
        plt.title(title)
        plt.axis([0, SIMULATED_TIME, 0,100])
        plt.grid(True)
        

if __name__ == "__main__":
    Plotting()