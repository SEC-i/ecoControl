import urllib2
import json
import time
import logging
import calendar
from datetime import datetime, timedelta

from server.forecasting.systems.data.old_demands import outside_temperatures_2013, outside_temperatures_2012
from server.forecasting.forecasting.helpers import cached_data
from server.models import WeatherValue, RealWeatherValue
from django.utils.timezone import utc
from django.db.models import F
from django.db.models.query_utils import Q

logger = logging.getLogger('simulation')

class WeatherForecast:
    def __init__(self, env=None, city="Berlin"):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.hourly = True
        
        self.cache_day = {}
        self.cache_real_values = {}
        self.error_day_cache = {}
        
    def get_temperature_estimate(self, date_time):
        """get most accurate forecast for given date_time
        that can be derived from 5 days forecast, 14 days forecast or from history data"""
        time_passed = (calendar.timegm(date_time.timetuple()) - self.env.now) / (60.0 * 60.0 * 24)  # in days
        
        initial0 = self.env.initial_date.replace(minute=0,second=0)
        initial1 = initial0 + timedelta(hours=1)
        
        target_date = date_time.replace(hour=0,minute=0,second=0)
        target_date_key = target_date.strftime("%Y-%m-%d")
        
        
        
        if self.error_day_cache.has_key(target_date_key):
            return self.error_day_cache[target_date_key][date_time.hour]
        
        if not self.cache_day.has_key(target_date_key):
            forecasts_until_now = WeatherValue.objects.filter(timestamp__lte=initial0)
            if len(forecasts_until_now) == 0:
                #print "Warning, date_time not in weatherforecasts ", date_time, " getting real data" ,"initial", initial0
                return self.get_temperature(date_time)
            newest_creation_timestamp = forecasts_until_now.latest('timestamp').timestamp
            
            
            values0 = WeatherValue.objects.filter(timestamp=newest_creation_timestamp).filter(target_time__range = [target_date.replace(hour=0), target_date.replace(hour=23,minute=59)])
            day_values0 =  values0.order_by("-timestamp")

            test_list = [(float(v.temperature),v.target_time.hour) for v in day_values0]
            if len(test_list) < 24:
                self.error_day_cache[target_date_key] = self.fill_error_gaps(test_list, date_time)
                return self.error_day_cache[target_date_key][date_time.hour]
            
            self.cache_day[target_date_key] = [float(v.temperature) for v in day_values0]
        
        
        values0 =self.cache_day[target_date_key]
        return self.mix(values0[date_time.hour],values0[min(date_time.hour+1,23)], target_date.minute / 60.0)
    
    def fill_error_gaps(self, input_list, date):
        print "not enough dates in list ", len(input_list), " ", date
        output = [None for i in range(24)]
        for temp_date in input_list:
            output[temp_date[1]] = temp_date[0]
        
        for i,v in enumerate(output):
            if v == None:
                if len(self.cache_day) == 0:
                    output[i] = self.get_temperature(date.replace(hour=i))
                else:
                    #get the latest cached day
                    latest = sorted(self.cache_day,reverse=True)[0]
                    output[i] = self.cache_day[latest][i]
        return output

    
    def get_temperature(self,date):
        if not self.cache_real_values.has_key(date.strftime("%Y-%m-%d %H")):
            real_temps = RealWeatherValue.objects.all()
            for entry in real_temps:
                self.cache_real_values[entry.timestamp.strftime("%Y-%m-%d %H")] = float(entry.temperature)
                
        return  self.mix(self.cache_real_values[date.strftime("%Y-%m-%d %H")], 
                         self.cache_real_values[(date + timedelta(hours=1)).strftime("%Y-%m-%d %H")],
                          date.minute / 60.0)

   
        
    def get_average_outside_temperature(self, date, offset_days=0):
        date = int(calendar.timegm(date.timetuple()))
        day = int(time.gmtime(date).tm_yday + offset_days) % 365
        hour = time.gmtime(date).tm_hour
        d0 = outside_temperatures_2013[day * 24 + hour]
        d1 = outside_temperatures_2012[day * 24 + hour]
        return (d0 + d1) / 2.0

    def mix(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        return time.time()  # for debugging, use self.env.now
