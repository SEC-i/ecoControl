import urllib2
import json
import time
from datetime import date
import datetime
from django.utils import timezone
import logging

from server.models import WeatherValue

logger = logging.getLogger('simulation')


from server.forecasting.systems.data import outside_temperatures_2013, outside_temperatures_2012
from server.forecasting.forecasting.helpers import cached_data

class WeatherForecast:

    def __init__(self, env=None):
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.three_hourly_url = "http://api.openweathermap.org/data/2.5/forecast?q=berlin&mode=json&units=metric"
        self.daily_url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=berlin&cnt=14&mode=json&units=metric"
        
    def update_weather_estimates(self):
    # only permit forecast queries every 30min, to save some api requests
        try:
            value = WeatherValue.objects.latest('timestamp')
            if float(value.temperature) < -273.15:
                raise WeatherValue.DoesNotExist
            last_time = value.timestamp
            
            time_naive = datetime.datetime.fromtimestamp(self.get_date())
            current_time = time_naive.replace(tzinfo=timezone.utc)
            seconds_passed = (current_time - last_time).total_seconds()
            if seconds_passed < 1800: # 30 minutes 
                return
        except WeatherValue.DoesNotExist:
            pass
        
        self.save_weather_forecast_three_hourly()
        self.save_weather_forecast_daily_from_day_six()
        
    def get_weather_forecast(self, daily = True):
        if daily:
            url = self.daily_url
        else:
            url = self.three_hourly_url
            
        try:
            #jsondata = cached_data('openweathermap', data_function=self.get_openweathermapdata, max_age=0)
            result = urllib2.urlopen(url)
            jsondata = result.read()
            data = json.loads(jsondata)
            results = self.set_up_records_out_of_json(data, daily)
        except urllib2.URLError, e:
            logger.warning("{0}: Couln't reach {1}".format(e, url))
            results = []
            stamp_naive = datetime.datetime.fromtimestamp(self.get_date())
            timestamp = stamp_naive.replace(tzinfo=timezone.utc)
            for i in range(0, 40):
                results.append(
                    WeatherValue(temperature=-300, timestamp=timestamp))
        return results        
        
    def set_up_records_out_of_json(self, data, daily=True):
        # logger.warning("WeatherForecast: Problems while json parsing.")
        # logger.error("WeatherForecast: Fetched %d temperature values") % len(forecast_temperatures))
        # logger.error("WeatherForecast: URLError during API call")
        results = []
        for data_set in data["list"]:
            try:
                target_sec = data_set['dt']
                target_naive = datetime.datetime.fromtimestamp(target_sec)
                target_time = target_naive.replace(tzinfo=timezone.utc)
                
                if(daily):
                    target_time = target_time.replace(hour = 0, 
                                        minute=0, second=0, microsecond=0)
                    temperature = data_set['temp']['day']
                else:
                    target_time = self.get_nearest_hour(target_time)
                    temperature = data_set['main']['temp']

                
                stamp_naive = datetime.datetime.fromtimestamp(self.get_date())
                timestamp = stamp_naive.replace(tzinfo=timezone.utc) 
                new_record = WeatherValue(temperature=temperature, 
                    timestamp=timestamp, target_time = target_time)
                results.append(new_record)
            except KeyError as k:
                # last value of data seams always to be gdps
                if "gdps" not in data_set:
                    raise k 
        return results
    
    def get_nearest_hour(self, date):
        if date.minute < 30:
            return date.replace(minute=0, second=0, microsecond=0)    
        return date.replace(hour = date.hour+1, 
                            minute=0, second=0, microsecond=0)
    
    def save_weather_forecast_three_hourly(self):
        results = self.get_weather_forecast(daily=False)
        for record in results: 
            record.save()
            
    def save_weather_forecast_daily(self):
        results = self.get_weather_forecast(daily=True)
        for record in results:
            record.save()
    
    def save_weather_forecast_daily_from_day_six(self):
        today = self.get_date()
        day_six = today + 5*25*60*60
        stamp_naive = datetime.datetime.fromtimestamp(day_six)
        timestamp_day_six = stamp_naive.replace(tzinfo=timezone.utc,
            hour=0, minute=0, second=0, microsecond=0) 
        
        results = self.get_weather_forecast(daily=True)
        for record in results:
            if record.target_time >= timestamp_day_six:
                record.save()
        
    def get_temperature_estimate(self, date):
        current_date = datetime.datetime.fromtimestamp(self.get_date())\
                      .replace(tzinfo=timezone.utc)
        if current_date > date:
            return self.get_temperature_of_passed_date(date)
        days_in_future = date.day - current_date.day
        self.update_weather_estimates()
        if days_in_future <=5:
            return self.get_forecast_temperature_hourly(date)
        else:
            return self.get_forecast_temperature_daily(date)
            
    def get_temperature_of_passed_date(self, date): 
        d = datetime.timedelta(0,60*15)
        earlier_stamp = date - d
        later_stamp = date + d

        entries = WeatherValue.objects.filter(
            target_time__gte = earlier_stamp,
            target_time__lte=later_stamp
            )
        if len(entries) > 1:            
            result = self.get_nearest_and_newest_weather_value(
                    entries[0], entries[1], date)
        else:
            result = entries[0]
        return float(result.temperature)
        
        
    def get_nearest_and_newest_weather_value(self, entry1, entry2, target_time):
        diff_1 = abs(target_time - entry1.target_time)
        diff_2 = abs(target_time - entry2.target_time)
        if diff_1 > diff_2:
            return entry2
        elif diff_1 < diff_2:
            return entry1
        else:
            sorted_list = sorted([entry1, entry2], key=lambda x: x.timestamp)
            return sorted_list[1]
            
    def get_forecast_temperature_hourly(self, date):
        if date.minute > 30:
            look_up_hour=date.hour+1
        else:
            look_up_hour=date.hour
        earlier_hour = (look_up_hour-2) % 24
        look_up_date_earlier = date.replace(hour= earlier_hour,
                                    minute=0, second=0, microsecond=0)
        later_hour = (look_up_hour+2) % 24                     
        look_up_date_later = date.replace(hour=later_hour,
                                    minute=0, second=0, microsecond=0)
        look_up_date = date.replace(hour=look_up_hour,
                                    minute=0, second=0, microsecond=0)
        entries = WeatherValue.objects.filter(
            target_time__gte = look_up_date_earlier,
            target_time__lte=look_up_date_later
            ) # entries contain one to two entries  
  
        if len(entries) > 1:
            value = self.get_nearest_and_newest_weather_value(entries[0],
                                                    entries[1],
                                                    look_up_date)
            result = value.temperature
        else:
            result = entries[0].temperature     
        return float(result)

    def get_forecast_temperature_daily(self, date):
        entries = WeatherValue.objects.filter(
                target_time = date.replace(hour= 0,
                                        minute=0, second=0, microsecond=0)
                ).order_by('-timestamp')
        return float(entries[0].temperature)
            
    def mix(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        return time.time()
