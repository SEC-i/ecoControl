import calendar
from time import time
import cProfile
import dateutil
import os
from csv import writer
from django.core.management.base import BaseCommand

from server.models import SensorValue
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import get_forecast
from server.functions import get_past_time
from server.forecasting.tools.plotting import show_plotting
from server.settings import BASE_DIR
from server.forecasting.forecasting.holt_winters import multiplicative


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
        #self.plot_simulations([measured, forecasted], 0, plot_series=["Thermal Consumerget_outside_temperature", "Heat Storageget_temperature"], block=True)
        
        
        
        
        self.export_rows([measured, forecasted], plot_series=["Thermal Consumerget_outside_temperature", "Heat Storageget_temperature"])
        
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
        
    def export_csv(self, sensordata_sets, plot_series="all"):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        with open(os.path.join(BASE_DIR,'evaluation.csv'), 'w') as csv:
            w = writer(csv, delimiter='\t')
            labels = ["date"]
            for sensordata in sensordata_sets:
                for index, dataset in enumerate(sensordata):
                    if plot_series == "all" or dataset["device"] + dataset["key"] in plot_series:
                        labels.append(dataset["dataset_name"] + " " + dataset["key"])
            w.writerow(labels)
                       
            dates = [dateutil.parser.parse(data_tuple[0]) for data_tuple in sensordata_sets[0][0]["data"]]
            for i,_date in enumerate(dates):
                row = []
                row.append(_date)
                for sensordata in sensordata_sets:
                    for dataset in sensordata:
                        if plot_series == "all" or dataset["device"] + dataset["key"] in plot_series:
                            try:
                                row.append(dataset["data"][i][1])
                            except:
                                print "error in row", i, "with dataset ", dataset["key"]
                w.writerow(row)
    
    def export_rows(self, sensordata_sets, plot_series="all"):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        with open(os.path.join(BASE_DIR,'evaluation.txt'), 'w') as _file:                       
            dates = [dateutil.parser.parse(data_tuple[0]) for data_tuple in sensordata_sets[0][0]["data"]]
            output = "dates: "
            for d in dates:
                output += str(d) + ","
            
            for sensordata in sensordata_sets:
                for dataset in sensordata:
                    if plot_series == "all" or dataset["device"] + dataset["key"] in plot_series:
                        output += dataset["dataset_name"] + " " + dataset["key"] + ": "
                        for t,v in dataset["data"]:
                            output += str(v) + ","
                        output += "\n\n\n"
            _file.write(output)
            print "finito"
        
                    
            

        
