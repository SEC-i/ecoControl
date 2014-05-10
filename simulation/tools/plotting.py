import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import time
import datetime

from simulation.core.helpers import SimulationBackgroundRunner, MeasurementCache

SIMULATED_TIME_MAIN = 60 * 60 * 24 * 10
SIMULATED_TIME_FORECAST = 60 * 60 * 24 * 100


class Plotting(object):

    def __init__(self):
        self.measure_values = [
            'time', 'cu_workload', 'plb_workload', 'hs_temperature',
            'thermal_consumption', 'outside_temperature', 'electrical_consumption']

#         self.simulation_manager = SimulationManager(
#             initial_time=1396915200)  # 8.4.2014
        self.plot_new_simulation(SIMULATED_TIME_FORECAST, 60, "Forecast1")

    def plot_new_simulation(self, simulated_time, measurement_interval, title,  datasheet=None):
        data = {}
        for name in self.measure_values:
            data[name] = []

        (simulation, measurements) = self.simulation_manager.forecast_for(
            simulated_time, blocking=False)
        env = simulation.env

        rule_strategy = RuleStrategy(env, self.simulation_manager)

        # supply environment with measurement function
        env.register_step_function(self.step_function, {
                                   "env": env, "measurement_cache": measurements, "data": data, "rule_strategy": rule_strategy})

        while env.forward > 0:
            time.sleep(0.2)

        t = []
        for value in data["time"]:
            t.append(datetime.datetime.fromtimestamp(value))

        Plotting.plot_dataset(t, data, "Energy Conversion")
        plt.show(block=True)

    def step_function(self, kwargs):
        self.measure_function(kwargs)
        if "rule_strategy" in kwargs:
            rule_strategy = kwargs["rule_strategy"]
            rule_strategy.step_function()

    def measure_function(self, kwargs):
        env = kwargs["env"]

        if env.now % 3600 == 0.0:
            measurements = kwargs["measurement_cache"]
            data = kwargs["data"]
            for value in self.measure_values:
                data[value].append(measurements.get_mapped_value(value))
    
    @classmethod
    def plot_dataset(cls,sensordata):
        fig, ax = plt.subplots()
        for name, sensorvals in sensordata.items():
            if name != "time":
                ax.plot(range(len(sensorvals)), sensorvals, label=name)
        
        # Now add the legend with some customizations.
        legend = ax.legend(loc='upper center', shadow=True)
        
        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
        
        # Set the fontsize
        for label in legend.get_texts():
            label.set_fontsize('medium')
        
        for label in legend.get_lines():
            label.set_linewidth(1.5)
        
        plt.subplots_adjust(bottom=0.2)
        plt.xlabel('Simulated time in seconds')
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.show(block=True)
        


if __name__ == "__main__":
    Plotting()
