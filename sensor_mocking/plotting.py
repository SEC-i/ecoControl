import matplotlib.pyplot as plt
import numpy as np

from HeatStorage import HeatStorage
from Simulation import Simulation
from Heating import Heating


SIMULATED_TIME = 5 * 3600
SIMULATION_DURATION = 10

STEP_SIZE = SIMULATED_TIME / SIMULATION_DURATION
TIME_STEP = 0.005


class Plotting(object):
    def __init__(self):
        simulation = Simulation(step_size=STEP_SIZE,time_step=TIME_STEP,plotting=True,duration=SIMULATION_DURATION)
        simulation.start()
        simulation.join()
        

        self.data = simulation.plotting_data
        # evenly sampled time at xxx intervals
        self.t = np.arange(0.0, SIMULATED_TIME, TIME_STEP*STEP_SIZE)        
        #cut to the actual length of simulation data
        self.t = self.t[0:len(self.data[1]["workload0"])]
        
        self.plot_dataset(1, "Energy Conversion")
        plt.show(block=False)
        self.plot_dataset(2, "Temperatures")
        plt.show(block=True)    
        


    def plot_dataset(self,data_id,title):

        
        fig, ax = plt.subplots()
        
        for name,sensorvals in self.data[data_id].items():
            if name != "unit":
                line_label = name + " in " +  self.data[data_id]["unit"]
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