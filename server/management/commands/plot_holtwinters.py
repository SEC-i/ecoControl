import calendar
from time import time
import cProfile
import dateutil
import os
from csv import writer
from django.core.management.base import BaseCommand
from datetime import datetime
import sys

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
from server.systems.base import BaseEnvironment



class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        #self.strom_real()
        #self.handle_single_data()
        self.error_arrays()

        
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
            
    def export_csv(self, datasets=[], dataset=None,name='evaluation_full.csv', plot_series="all"):
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

          
     
    def rmse(self, forecast, testdata):
        return sqrt(sum([(m - n) ** 2 for m, n in zip(forecast, testdata)]) / len(testdata))
                
    def one_forecast(self, trainingdata, testdata, start_forecast, end_forecast, day_errors, hour_errors, period_errors):
        
        electrical_forecast = Forecast(BaseEnvironment(start_forecast, False, False), trainingdata, samples_per_hour=1)
        forecast  = [electrical_forecast.get_forecast_at(timestamp) for timestamp in range(start_forecast,end_forecast,3600)]
        
        
        for day, length in enumerate(range(24,14*24,24)):
            period_errors[day][0] += self.rmse(forecast[:length], testdata[:length])
            period_errors[day][1] += Forecast.MASE(trainingdata, testdata[:length], forecast[:length])
        
        
        for day, day_data in enumerate(electrical_forecast.forecasted_demands):
            split_testdata = Forecast.split_weekdata(testdata,samples_per_hour=1,start_date=datetime.fromtimestamp(start_forecast))
            day_errors[day][0] += self.rmse(day_data, split_testdata[day])
            day_errors[day][1] += Forecast.MASE(electrical_forecast.demands[day], split_testdata[day], electrical_forecast.forecasted_demands[day])
            
            
        hour_maker = lambda data,hour: [val for i, val in enumerate(data) if i % 24  == hour]
        for hour in range(24):
            hour_values_train = hour_maker(trainingdata, hour)
            hour_values_test = hour_maker(testdata, hour)
            hour_values_forecast = hour_maker(forecast, hour)
            
            hour_errors[hour][0] += self.rmse(hour_values_forecast, hour_values_test)
            hour_errors[hour][1] += Forecast.MASE(hour_values_train, hour_values_test, hour_values_forecast)
            
    def strom_real(self):
        sep = os.path.sep
        path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_2013.csv")
        raw_dataset = DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates = DataLoader.load_from_file(path, "Datum", "\t")

        path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_1.1-12.6.2014.csv")
        raw_dataset += DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates += DataLoader.load_from_file(path, "Datum", "\t")
        
        dates = Forecast.make_hourly([int(d) for d in dates],6)
        demand = Forecast.make_hourly([float(val) / 1000.0 for val in raw_dataset], 6)  
        
        
        hourly_weekday = [[0,0] for i in range(24)]
        hourly_weekend = [[0,0] for i in range(24)]
        
        start = calendar.timegm(datetime(year=2013,month=1,day=1).timetuple())
        end = calendar.timegm(datetime(year=2014,month=1,day=1).timetuple())
        
        day = datetime(year=2013,month=1,day=1).weekday()
        for i,h in enumerate(demand):
            if day in [5,6]:
                hourly_weekend[i%24][0] += h
                hourly_weekend[i%24][1] += 1
            else:
                hourly_weekday[i%24][0] += h
                hourly_weekday[i%24][1] += 1
                
            if i %24 == 0:
                day = (day+1) % 7
        hourly_weekend = [r/l for r,l in hourly_weekend]
        hourly_weekday = [r/l for r,l in hourly_weekday]
        
        self.export_csv(datasets=[("weekday",hourly_weekday),("weekend", hourly_weekend)],name="avg.csv")
                
    def error_arrays(self):
        sep = os.path.sep
        path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_2013-6.2014Reger.csv")
        raw_dataset1 = DataLoader.load_from_file(
            path, "Energie DG Leistung", "\t")
        raw_dataset2 = DataLoader.load_from_file(
            path, "Energie EG Leistung", "\t")
        
        dates = DataLoader.load_from_file(path, "Datum", "\t")

#         path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_1.1-12.6.2014.csv")
#         raw_dataset += DataLoader.load_from_file(
#             path, "Strom - Verbrauchertotal (Aktuell)", "\t")
#         dates += DataLoader.load_from_file(path, "Datum", "\t")
        transf = lambda v: min(float(v) / 1000.0,500)
        demand = [transf(v1) + transf(v2) for v1,v2 in zip(raw_dataset1,raw_dataset2)]
        
        dates = Forecast.make_hourly([int(d) for d in dates],6)
        demand = Forecast.make_hourly(demand,6)#[float(val) / 1000.0 for val in raw_dataset], 6)
        
        start = calendar.timegm(datetime(year=2013,month=2,day=15).timetuple())
        end = calendar.timegm(datetime(year=2014,month=1,day=1).timetuple())
        fc_length = 7*24*2
        
        day_errors = [[0,0] for i in range(7)] #rmse, mase
        hour_errors = [[0,0] for i in range(24)]
        period_errors = [[0,0] for i in range(14)]
        for timestamp in range(start, end, 24*3600):
            print "day:", datetime.fromtimestamp(timestamp)
            
            start_index = approximate_index(dates, timestamp)
            trainingdata = demand[:start_index]
            testdata = demand[start_index:start_index+fc_length]
            try:
                self.one_forecast(trainingdata, testdata, timestamp, timestamp+fc_length*3600,
                                  day_errors=day_errors,hour_errors=hour_errors,period_errors=period_errors)
            except:
                print "error, really now", sys.exc_info()[0]
                break
            print day_errors, hour_errors
        
        l = len(range(start, end, 24*3600))    
        day_errors = [[r/l,m/l] for r,m in day_errors]
        hour_errors = [[r/l,m/l] for r,m in hour_errors]
        period_errors = [[r/l,m/l] for r,m in period_errors]
            

        #(forecast_values_auto, alpha, beta, gamma) = multiplicative(trainingdata, 7*24, 7*24*2, optimization_type="MASE")
        #print alpha, beta, gamma, rmse_auto, sqrt(sum([(m - n) ** 2 for m, n in zip(forecast_values_auto, testdata)]) / len(testdata))
        #print "normal", sqrt(sum([(m - n) ** 2 for m, n in zip(forecast_values_auto, testdata)]) / len(testdata))
        #print "split", sqrt(sum([(m - n) ** 2 for m, n in zip(forecast, testdata)]) / len(testdata))
        #split_testdata = Forecast.split_weekdata(testdata,samples_per_hour=1,start_date=datetime.fromtimestamp(start_forecast))
        #plot_dataset({"measured": split_testdata[5], "forecasted": electrical_forecast.forecasted_demands[5]}, 0, True)
        #self.export_rows({"measured": testdata, "forecasted": forecast_values_auto,  "forecasted_split": forecast})
        
#         self.export_csv({"day_errors_rmse": zip(*day_errors)[0], "day_errors_mase": zip(*day_errors)[1],
#                           "hour_errors_rmse": zip(*hour_errors)[0], "hour_errors_mase": zip(*hour_errors)[1], 
#                           "period_errors_rmse": zip(*period_errors)[0], "hour_errors_mase": zip(*period_errors)[1]})
        
        self.export_csv(datasets=[("day_errors_rmse", zip(*day_errors)[0]), ("day_errors_mase", zip(*day_errors)[1]),
                          ("hour_errors_rmse", zip(*hour_errors)[0]), ("hour_errors_mase", zip(*hour_errors)[1]), 
                          ("period_errors_rmse", zip(*period_errors)[0]), ("hour_errors_mase", zip(*period_errors)[1])],
                        name="eval_reger.csv")
                
    def handle_single_data(self):
        sep = os.path.sep
        path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "systems" + sep + "data" + sep + "Electricity_1.1-12.6.2014.csv")
        raw_dataset = DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates = Forecast.make_hourly([int(d) for d in DataLoader.load_from_file(path, "Datum", "\t")],6)
        demand = Forecast.make_hourly([float(val) / 1000.0 for val in raw_dataset], 6)
        
        start = calendar.timegm(datetime(year=2014,month=3,day=15).timetuple())
        start_index = approximate_index(dates, start)
        trainingdata = demand[start_index:-7*24*2]
        testdata = demand[-7*24*2:]
        start_forecast = start+len(trainingdata)*3600
        end_forecast = start_forecast + len(testdata) * 3600
        
        electrical_forecast = Forecast(BaseEnvironment(start_forecast, False, False), trainingdata, samples_per_hour=1)
        forecast  = [electrical_forecast.get_forecast_at(timestamp) for timestamp in range(start_forecast,end_forecast,3600)]
        
        #(forecast_values_auto, alpha, beta, gamma) = multiplicative(trainingdata, 7*24, 7*24*2, optimization_type="RMSE")
        #print alpha, beta, gamma, rmse_auto, sqrt(sum([(m - n) ** 2 for m, n in zip(forecast_values_auto, testdata)]) / len(testdata))
        #print "normal", sqrt(sum([(m - n) ** 2 for m, n in zip(forecast_values_auto, testdata)]) / len(testdata))
        #print "split", sqrt(sum([(m - n) ** 2 for m, n in zip(forecast, testdata)]) / len(testdata))
        #split_testdata = Forecast.split_weekdata(testdata,samples_per_hour=1,start_date=datetime.fromtimestamp(start_forecast))
        #plot_dataset({"measured": split_testdata[5], "forecasted": electrical_forecast.forecasted_demands[5]}, 0, True)
        plot_dataset({"measured":testdata, "forecasted":forecast})
        #self.export_rows({"measured": testdata, "forecasted": forecast_values_auto,  "forecasted_split": forecast})
        #self.export_csv(testdata)
           
        
        