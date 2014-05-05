import urllib2
import json
import time
from datetime import date
import datetime
from django.utils import timezone

from server.forecasting.systems.data import outside_temperatures_2013, outside_temperatures_2012
from server.models import WeatherSource, WeatherValue


class WeatherForecast:

    def __init__(self, env=None):
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.three_hourly_url = "http://openweathermap.org/data/2.5/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5&mode=json"


    def get_weather_forecast(self, url, hourly=True):
        if not hourly:
            url = "http://openweathermap.org/data/2.3/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5?mode=daily_compact"       
        try:
            result = urllib2.urlopen(url)
            jsondata = result.read()
            data = json.loads(jsondata)
            results = self.set_up_records_out_of_json(data)
        except urllib2.URLError, e:
            print e
            # Use history data
            result = []
            for i in range(0, 40):
                result.append(
                    self.get_average_outside_temperature(self.get_date(), i))
            return result
        return results
        
    def set_up_records_out_of_json(self, data):
        results = []
        for data_set in data["list"]:
            try:
                temperature = data_set["main"]["temp"]
                stamp_naive = datetime.datetime.fromtimestamp(self.get_date())
                timestamp = stamp_naive.replace(tzinfo=timezone.utc)
                new_record = WeatherValue(temperature=temperature, 
                    timestamp=timestamp)
                results.append(new_record)
            except KeyError as k:
                # last value of data seams always to be gdps
                if "gdps" not in data_set:
                    raise k 
        return results
    
    def get_weather_forecast_three_hourly(self):
        results = self.get_weather_forecast(self.three_hourly_url)
        i = 0
        for record in results:
            record.target_time = datetime.datetime.fromtimestamp(
                self.get_date()+i*10800).replace(tzinfo=timezone.utc) # every 3-hours: 3*60*60 
            record.save()
            i = i+1

    def get_temperature_estimate(self, date):
        """get most accurate forecast for given date
        that can be derived from 5 days forecast, 14 days forecast or from history data"""
        history_data = self.get_average_outside_temperature(date)
        time_passed = (date - self.get_date()) / (60.0 * 60.0 * 24)  # in days
        if time_passed < 0.0 or time_passed > 13.0:
            return history_data

        forecast_data_hourly = self.get_forecast_temperature_hourly(date)
        forecast_data_daily = self.get_forecast_temperature_daily(date)
        if time_passed < 5.0:
            return forecast_data_hourly
        else:
            return forecast_data_daily

    def get_forecast_temperature_hourly(self, date):
        self.forecast_temperatures_3hourly = self.get_weather_forecast(
            hourly=True)
        time_passed = int((date - self.get_date()) / (60.0 * 60.0))  # in hours
        weight = (time_passed % 3) / 3.0
        t0 = min(int(time_passed / 3), len(
            self.forecast_temperatures_3hourly) - 1)
        t1 = min(t0 + 1, len(self.forecast_temperatures_3hourly) - 1)
        a0 = self.forecast_temperatures_3hourly[t0]
        a1 = self.forecast_temperatures_3hourly[t1]
        return self.mix(a0, a1, weight)

    def get_forecast_temperature_daily(self, date):
        self.forecast_temperatures_daily = self.get_weather_forecast(
            hourly=False)
        time_passed = int((date - self.get_date()) / (60.0 * 60.0))  # in days
        weight = (time_passed % 24) / 24.0
        t0 = min(int(time_passed / 24), len(
            self.forecast_temperatures_daily) - 1)
        t1 = min(t0 + 1, len(self.forecast_temperatures_daily) - 1)
        a0 = self.forecast_temperatures_daily[t0]
        a1 = self.forecast_temperatures_daily[t1]
        return self.mix(a0, a1, weight)

    def get_average_outside_temperature(self, date, offset_days=0):
        day = (time.gmtime(date).tm_yday + offset_days) % 365
        hour = time.gmtime(date).tm_hour
        d0 = outside_temperatures_2013[day * 24 + hour]
        d1 = outside_temperatures_2012[day * 24 + hour]
        return (d0 + d1) / 2.0
        
    def update_weather_estimates(self):
    # only permit forecast queries every 30min, to save some api requests
        values = WeatherValue.objects.order_by('-timestamp')
    
        last_time = self.get_latest_valid_time(values)
        if last_time:
            time_naive = datetime.datetime.fromtimestamp(self.get_date())
            current_time = time_naive.replace(tzinfo=timezone.utc)
            seconds_passed = (current_time - last_time).total_seconds()
            if seconds_passed < 1800: # 30 minutes 
                return
        self.get_weather_forecast_three_hourly()
        
    def get_latest_valid_time(self, values):
        for value in values:
            if float(value.temperature) > -273.15:
                return value.timestamp
            
    def mix(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        return time.time()
