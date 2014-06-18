import calendar
from time import time
import cProfile
import dateutil
import os
from csv import writer
from django.core.management.base import BaseCommand
from datetime import datetime

from server.models import SensorValue
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import get_forecast
from server.functions import get_past_time
from server.forecasting.tools.plotting import show_plotting, plot_dataset
from server.settings import BASE_DIR
from server.forecasting.forecasting.holt_winters import multiplicative
from server.forecasting.forecasting.helpers import approximate_index
from server.forecasting.forecasting.dataloader import DataLoader
from server.forecasting.forecasting import Forecast
from math import sqrt


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        sep = os.path.sep
        path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_1.1-12.6.2014.csv")
        raw_dataset = DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates = Forecast.make_hourly([int(d) for d in DataLoader.load_from_file(path, "Datum", "\t")],6)
        demand = Forecast.make_hourly([float(val) / 1000.0 for val in raw_dataset], 6)
        
        start = calendar.timegm(datetime(year=2014,month=2,day=1).timetuple())
        start_index = approximate_index(dates, start)
        trainingdata = demand[start_index:-7*24*2]
        testdata = demand[-7*24*2:]
        
        (forecast_values_auto, alpha, beta, gamma, rmse_auto) = multiplicative(trainingdata, 7*24, 7*24*2, optimization_type="RMSE")
        print alpha, beta, gamma, rmse_auto, sqrt(sum([(m - n) ** 2 for m, n in zip(forecast_values_auto, testdata)]) / len(testdata))
        #plot_dataset({"measured": testdata, "forecasted": forecast_values_auto}, 0, True)
        self.export_rows({"measured": testdata, "forecasted": forecast_values_auto})
        
    def export_rows(self, sensordata, plot_series="all"):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        with open(os.path.join(BASE_DIR,'evaluation_hw.txt'), 'w') as _file:   
            output  = ""                    
            for key,dataset in sensordata.iteritems():
                output += key + ": "
                for v in dataset:
                    output += str(v) + ","
                output += "\n\n\n"
            _file.write(output)
            print "finito"
        
        