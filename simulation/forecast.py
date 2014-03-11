import urllib2
import json
import systems.data
from systems.data import *
import time
import datetime


class Forecast:

    def __init__(self, env=None):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures = []

    def get_weather_forecast(self):
        if self.forecast_temperatures != [] and self.forecast_query_date - self.get_date() < 60 * 30 : #only permit forecast queries every 30min, to save some api requests
            return self.forecast_temperatures

        #3-hourly forecast for 14 days
        url = "http://openweathermap.org/data/2.3/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5&mode=json"
        forecast_temperatures = []
        self.forecast_query_date = self.get_date()
        try:
            result = urllib2.urlopen(url)
            jsondata = result.read()
            data = json.loads(jsondata)
            for data_set in data["list"]:
                try:
                    forecast_temperatures.append(data_set["main"]["temp"])
                except:
                    print "error reading temperatures from: \n", json.dumps(data_set, sort_keys=True, indent=4, separators=(',', ': '))

            print "read ", len(forecast_temperatures), "temperatures"


        except urllib2.URLError, e:
            handleError(e)

        return forecast_temperatures

    def get_temperature_estimate(self,date):
        history_data = self.get_average_outside_temperature(date)
        forecast_data = self.get_forecast_temperature(date)
        time_passed = datetime.timedelta(seconds=self.forecast_query_date - self.get_date()).days
        factor = 1.0/time_passed
        if time_passed < 14.0:
            weighted_temperature = history_data * (1-factor) + forecast_data * factor
        else:
            weighted_temperature = history_data

        return weighted_temperature

    def get_forecast_temperature(self,date):
        self.forecast_temperatures = self.get_weather_forecast()
        time_passed = (self.forecast_query_date - self.get_date()) / (60.0 * 60.0) # in hours
        weight = (time_passed % 3) / 3.0
        t0 = self.forecast_temperatures[int(time_passed / 3)]
        t1 = int(min((time_passed + 1),len(self.forecast_temperatures)-1) / 3)
        return self.linear_interpolation(t0,t1,weight)
               #values are measured 3 hourly



    def get_average_outside_temperature(self, date, offset_days=0):
        day = (time.gmtime(date).tm_yday + offset_days) % 365
        hour = time.gmtime(date).tm_hour
        d0 = outside_temperatures_2013[day * 24 + hour] 
        d1 = outside_temperatures_2012[day * 24 + hour] 
        return (d0 + d1) / 2.0

    def linear_interpolation(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        #return self.env.now
        return time.time() #for debugging, use self.env.noe otherwise<






f=Forecast() 
print f.get_temperature_estimate(1394549951000) # Tue, 11 Mar 2014 14:59:11 GMT