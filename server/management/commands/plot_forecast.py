from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import get_forecast
from server.functions import get_past_time
import calendar
from server.models import SensorValue
from time import time
import cProfile


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        try:
            latest_timestamp = get_past_time()
            initial_time = calendar.timegm(latest_timestamp.timetuple())
        except SensorValue.DoesNotExist:
            initial_time = time()
        
        output = get_forecast(initial_time)
        self.plot_simulation(output, 0, plot_series=["Thermal Consumerget_outside_temperature"], block=True)
        
        #cProfile.runctx("get_forecast(initial_time)",globals(),locals(),filename="profile.profile")
    def plot_simulation(self, sensordata,forecast_start=0, plot_series="all", block=True):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        #from pylab import *
        fig, ax = plt.subplots()
        for index, dataset in enumerate(sensordata):
            if plot_series == "all" or dataset["device"] + dataset["key"] in plot_series:
                data = [data_tuple[1] for data_tuple in dataset["data"]]
                sim_plot, = ax.plot(range(len(data)), data, label=dataset["device"] + dataset["key"])
            
        self.show_plotting(plt, ax)
        
    def show_plotting(self, plt, ax):
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
        #plt.xlabel('Simulated time in seconds')
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.show()

        
