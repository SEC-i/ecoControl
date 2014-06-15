from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import get_forecast
from server.functions import get_past_time
import calendar
from server.models import SensorValue
from time import time
import cProfile
import dateutil
from server.forecasting.tools.plotting import show_plotting


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        try:
            latest_timestamp = get_past_time()
            initial_time = calendar.timegm(latest_timestamp.timetuple())
        except SensorValue.DoesNotExist:
            initial_time = time()
        
        forecasted = get_forecast(initial_time)
        for dataset in forecasted:
            dataset["dataset_name"] = "forecasted"
        measured = get_forecast(initial_time, forecast=False)
        for dataset in measured:
            dataset["dataset_name"] = "measured"
        self.plot_simulations([measured, forecasted], 0, plot_series=["Thermal Consumerget_outside_temperature"], block=True)
        
        #cProfile.runctx("get_forecast(initial_time)",globals(),locals(),filename="profile.profile")
    def plot_simulations(self, sensordata_sets,forecast_start=0, plot_series="all", block=True):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        #from pylab import *
        fig, ax = plt.subplots()
        for sensordata in sensordata_sets:
            for index, dataset in enumerate(sensordata):
                if plot_series == "all" or dataset["device"] + dataset["key"] in plot_series:
                    data = [data_tuple[1] for data_tuple in dataset["data"]]
                    dates = [dateutil.parser.parse(data_tuple[0]) for data_tuple in dataset["data"]]
                    sim_plot, = ax.plot(dates, data, label=dataset["dataset_name"] + " " + dataset["key"])
            
        show_plotting(plt, ax, block)

        
