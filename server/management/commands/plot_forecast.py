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
from datetime import datetime, timedelta
from math import sqrt
from server.forecasting.forecasting.helpers import approximate_index


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        try:
            latest_timestamp = get_past_time()
            initial_time = calendar.timegm(latest_timestamp.timetuple())
        except SensorValue.DoesNotExist:
            initial_time = time()
            
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        
        
#         forecasted = get_forecast(initial_time)
#         for dataset in forecasted:
#             dataset["dataset_name"] = "forecasted"
#         measured = get_forecast(initial_time, forecast=False)
#         for dataset in measured:
#             dataset["dataset_name"] = "measured"
        #self.plot_simulations([measured, forecasted], 0, plot_series=["Thermal Consumerget_outside_temperature", "Heat Storageget_temperature"], block=True)
        
        
        
        self.day_errors()
        #self.export_csv([measured, forecasted], plot_series=["Thermal Consumerget_outside_temperature", "Heat Storageget_temperature"])
        #self.export_csv_dataset(datasets=[("day_errors_rmse",  day_errors)])
    
    def day_errors(self):
        try:
            latest_timestamp = get_past_time()
            initial_time = calendar.timegm(latest_timestamp.timetuple())
        except SensorValue.DoesNotExist:
            initial_time = time()
        start = int(initial_time)
        end = int(initial_time + timedelta(days=20).total_seconds())
        fc_length = 7*24*2
        
        day_errors = [0 for i in range(10)] #rmse
        
        for timestamp in range(start, end, 24*3600):
            forecasted = get_forecast(timestamp)
            measured = get_forecast(timestamp, forecast=False)

            get_dataset =  lambda data, k: next((x["data"] for x in data if x["key"] == k), None)
            convert_dataset = lambda data: [(v,calendar.timegm(dateutil.parser.parse(date).timetuple())) for date,v in data]
            temp_m = convert_dataset( get_dataset(measured,"get_outside_temperature"))
            temp_f = convert_dataset( get_dataset(forecasted,"get_outside_temperature"))
            
            temp_m = convert_dataset( get_dataset(measured,"get_outside_temperature"))
            temp_f = convert_dataset( get_dataset(forecasted,"get_outside_temperature"))
            
            horizon = int(timedelta(days=10).total_seconds())    
            for i, current_time in enumerate(range(timestamp, timestamp+horizon, 24*3600)):
                
                slice = lambda data: [(val,date) for val, date in data if date >= current_time and date < current_time + 24*3600]
                measured_slice = slice(temp_m)
                forecast_sclice = [self.approximate_value(temp_f,date) for val, date in measured_slice]
                day_errors[i] += self.rmse(forecast_sclice, zip(*measured_slice)[0])
                
        l = 30    
        day_errors = [r/l for r in day_errors]
        #self.plot_simulations([measured, forecasted], 0, plot_series=["Thermal Consumerget_outside_temperature", "Heat Storageget_temperature"], block=True)
        
        
        
        self.export_csv_dataset(datasets=[("day_errors_rmse",  day_errors)])
        #self.export_rows([measured, forecasted], plot_series=["Thermal Consumerget_outside_temperature"])
        
    def rmse(self, forecast, testdata):
        return sqrt(sum([(m - n) ** 2 for m, n in zip(forecast, testdata)]) / len(testdata))
    
    def approximate_value(self, dataset_tuples, findvalue):
        values, dates = zip(*dataset_tuples)
        length = len(dates)
        #aproximate index
        diff = (dates[1] - dates[0])
        i = min(int((findvalue - dates[0])/diff), length -1)
        while i < length and i >= 0:
            if i == length -1:
                return values[i] if dates[i] == findvalue else None
            if  dates[i] == findvalue or (dates[i] < findvalue and dates[i+1] > findvalue):
                return values[i]
            elif dates[i] > findvalue:
                i-=1
            else:
                i+=1
        return None   
        
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
                if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
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
                    if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
                        labels.append(dataset["dataset_name"] + " " + dataset["key"])
            w.writerow(labels)
                       
            dates = [dateutil.parser.parse(data_tuple[0]) for data_tuple in sensordata_sets[0][0]["data"]]
            for i,_date in enumerate(dates):
                row = []
                row.append(_date)
                for sensordata in sensordata_sets:
                    for dataset in sensordata:
                        if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
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
                    if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
                        output += dataset["dataset_name"] + " " + dataset["key"] + ": "
                        for t,v in dataset["data"]:
                            output += str(v) + ","
                        output += "\n\n\n"
            _file.write(output)
            print "finito"
    
    def export_csv_dataset(self, datasets=[], dataset=None,name='evaluation_weather.csv', plot_series="all"):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        with open(os.path.join("D:\Dropbox\BachelorArbeit\Bachelorarbeiten\Max",name), 'w') as csv:
            w = writer(csv, delimiter='\t')
            if dataset != None:
                for v in dataset:
                    w.writerow([v])
            if datasets != []:
                labels = zip(*datasets)[0]
                w.writerow(labels)
                
                for index in range(24):
                    row = []
                    for label,dataset in datasets:
                        if len(dataset) > index:
                            row.append(dataset[index])
                        else:
                            row.append("")

                    w.writerow(row)
        
                    
            

        
