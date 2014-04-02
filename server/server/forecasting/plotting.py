import matplotlib.pyplot as plt
import numpy as np
import time
from simulationmanager import SimulationManager

from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values

SIMULATED_TIME =  60 * 60 * 24 * 365


class Plotting(object):
    def __init__(self):
        self.values = ['time', 'cu_workload', 'plb_workload', 'hs_temperature',
               'thermal_consumption', 'outside_temperature', 'electrical_consumption']
        
        self.simulation_manager = SimulationManager()
        self.simulation_manager.simulation_start()
        self.env  = self.simulation_manager.main_simulation.env

        self.env.stop_after_forward = True
        self.env.forward = SIMULATED_TIME

        
        
        self.data = {}
        for name in self.values:
            self.data[name] = []

        while self.env.now < self.env.now + self.env.forward:
            if self.env.now % self.env.measurement_interval == 0:
                for value in self.values:
                    self.data[value].append(self.simulation_manager.measurements.get_mapped_value(value))



        
        # evenly sampled time at xxx intervals
        self.t = np.arange(0.0,SIMULATED_TIME,SIMULATED_TIME/len(self.data["cu_workload"]))

        
        #cut to the actual length of simulation data
        print len(self.t),len(self.data["cu_workload"])
        self.t = self.t[0:len(self.data["cu_workload"])]
        
        self.plot_dataset("Energy Conversion")
        plt.show(block=True)
    
    def get_line_name(self,concat_name):
        parts = concat_name.split(".")
        dev_id = int(parts[1])
        device = self.simulation.devices[dev_id]
        sensor = self.simulation.get_sensor(dev_id,sensor_name=parts[0])
        return sensor.name + " of " + device.name +  " in " +  sensor.unit

    
    def get_mapped_value(self, value):
        if value == 'time':
            return self.env.now
        if value == 'cu_workload':
            return self.cu.workload
        if value == 'plb_workload':
            return self.plb.workload
        if value == 'hs_temperature':
            return self.heat_storage.get_temperature()
        if value == 'thermal_consumption':
            return self.thermal_consumer.get_consumption_power()
        if value == 'outside_temperature':
            return self.thermal_consumer.get_outside_temperature()
        if value == 'electrical_consumption':
            return self.electrical_consumer.get_consumption_power()
        return 0


    def plot_dataset(self,title):

        
        fig, ax = plt.subplots()
        
        for name,sensorvals in self.data.items():
            ax.plot(self.t,sensorvals,label=name)
        
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