import matplotlib.pyplot as plt
import numpy as np
import time
from simulationmanager import SimulationManager

from helpers import SimulationBackgroundRunner, MeasurementCache

SIMULATED_TIME_MAIN =  60 * 60 * 24 * 5
SIMULATED_TIME_FORECAST = 60 * 60 * 24 * 5


class Plotting(object):
    def __init__(self):
        self.measure_values = ['time', 'cu_workload', 'plb_workload', 'hs_temperature',
               'thermal_consumption', 'outside_temperature', 'electrical_consumption']
        
        self.simulation_manager = SimulationManager()
        self.simulation_manager.simulation_start()
        self.env  = self.simulation_manager.main_simulation.env

        #self.env.stop_after_forward = True
        #self.env.forward = SIMULATED_TIME_MAIN # 5days


        self.plot_new_simulation(SIMULATED_TIME_FORECAST, 60, "Forecast1")


        


    def plot_new_simulation(self, simulated_time, measurement_interval, title,  datasheet = None):
        data = {}
        for name in self.measure_values:
            data[name] = []

        (simulation, measurements) = self.simulation_manager.forecast_for(simulated_time)
        env = simulation.env 
        

        while env.forward > 0 :
            if env.now % measurement_interval == 0: 
                for value in self.measure_values:
                    data[value].append(measurements.get_mapped_value(value))

        print env.forward       
        print data
        # evenly sampled time at xxx intervals
        t = np.arange(0.0,simulated_time,simulated_time/len(data["time"]))

        #cut to the actual length of simulation data
        print len(t),len(data["time"])
        t = t[0:len(data["time"])]
        
        self.plot_dataset("Energy Conversion")
        plt.show(block=True)

    
    def get_line_name(self,concat_name):
        parts = concat_name.split(".")
        dev_id = int(parts[1])
        device = self.simulation.devices[dev_id]
        sensor = self.simulation.get_sensor(dev_id,sensor_name=parts[0])
        return sensor.name + " of " + device.name +  " in " +  sensor.unit


    def plot_dataset(self, timedata, sensordata, title):

        
        fig, ax = plt.subplots()
        
        for name,sensorvals in sensordata.items():
            ax.plot(timedata,sensorvals,label=name)
        
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
        plt.axis([0,SIMULATED_TIME, 0,100])
        plt.grid(True)
        

if __name__ == "__main__":
    Plotting()