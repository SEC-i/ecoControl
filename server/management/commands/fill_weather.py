from django.core.management.base import BaseCommand
from os import listdir
from os.path import isfile, join
from server.settings import BASE_DIR
from datetime import datetime
import json
from server.models import WeatherValue, RealWeatherValue
from django.utils.timezone import utc
from django.db import connection
import csv
import calendar
import string
from io import BytesIO

class Command(BaseCommand):
    help = 'fill weather from files into the database'

    def handle(self, *args, **options):
        directory  = join(BASE_DIR,"server","forecasting","demodata")
        
        with open(join(directory,'demo_weather.csv'), "rb") as file_obj:
            reader = csv.reader(file_obj, delimiter="\t")
            header = reader.next()
            print "Writing demo weather data into database"
               
            t_index = header.index('Timestamp')
            v_index = header.index('Value')
            values = []
            for row in reader:
                t = datetime.fromtimestamp(int(row[t_index])).replace(tzinfo=utc)   
                values.append([float(row[v_index]),t])                          
                #entry = RealWeatherValue(temperature=float(row[v_index]), timestamp=t)
                #entry.save()
            self.flush_data(values,False)
                
        with open(join(directory,'demo_weather_forecast.csv'), "rb") as file_obj:
            reader = csv.reader(file_obj, delimiter="\t")
            header = reader.next()
            print "Writing demo weather forecasts into database"
                            
            tc_index = header.index('Timestamp')
            tf_index = header.index('ForecastTimestamp')
            v_index = header.index('Value')
            values = []
            for row in reader:
                time_c = datetime.fromtimestamp(int(row[tc_index])).replace(tzinfo=utc)  
                time_fc = datetime.fromtimestamp(int(row[tf_index])).replace(tzinfo=utc)                                 
                values.append([float(row[v_index]),time_c,time_fc]) 
                #entry = WeatherValue(temperature=float(row[v_index]), timestamp=time_c, target_time=time_fc)
                #entry.save()
                
            self.flush_data(values,True)
                
    def flush_data(self,values, forecasts):
        cursor = connection.cursor()
        # Convert floating point numbers to text, write to COPY input

        cpy = BytesIO()
        for row in values:
            if forecasts:
                vals = [row[0], connection.ops.value_to_db_datetime(row[1]), connection.ops.value_to_db_datetime(row[2])]
            else:
                vals = [row[0], connection.ops.value_to_db_datetime(row[1])]
            cpy.write('\t'.join([str(val) for val in vals]) + '\n')

        # Insert forecast_data; database converts text back to floating point
        # numbers
        cpy.seek(0)
        if forecasts:
            cursor.copy_from(cpy, 'server_weathervalue',
                             columns=('temperature', 'timestamp', 'target_time'))
        else:
            cursor.copy_from(cpy, 'server_realweathervalue',
                             columns=('temperature', 'timestamp'))
            
        connection.commit()