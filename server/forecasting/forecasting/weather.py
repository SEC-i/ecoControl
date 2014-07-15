import urllib2
import json
import time
import logging
import calendar
from datetime import datetime, timedelta

from server.forecasting.systems.data.old_demands import outside_temperatures_2013, outside_temperatures_2012
from server.forecasting.forecasting.helpers import cached_data,\
    approximate_index
from server.models import WeatherValue, RealWeatherValue
from django.utils.timezone import utc

logger = logging.getLogger('simulation')

class DemoWeather:
    def __init__(self, env=None, city="Berlin"):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.hourly = True
        
        self.cache_day = {}
        self.cache_real_values = [[],[]]
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
        if self.cache_real_values == [[],[]]:
            real_temps = RealWeatherValue.objects.all()
            for entry in real_temps:
                self.cache_real_values[0].append(calendar.timegm(entry.timestamp.utctimetuple()))
                self.cache_real_values[1].append(float(entry.temperature))
        
        if len(self.cache_real_values[1]) < 2:
            raise Exception("not enough weather values in database")
        idx = approximate_index(self.cache_real_values[0], calendar.timegm(date.utctimetuple()))
        return  self.cache_real_values[1][idx]

   
        
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



class WeatherForecast:
    def __init__(self, env=None, city="Berlin"):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.hourly = True

        self.city_id = self.find_city(city)['default']

    """
    returns a dictionary with city id, names and country based on the given search name
    the first search result is returnd as 'default' too
    """
    def find_city(self, name):
        url = "http://api.openweathermap.org/data/2.5/find?q=" + name + "&mode=json"
        cities = {}
        first_city = None
        try:
            result = urllib2.urlopen(url)
            jsondata = result.read()
            data = json.loads(jsondata)

            for data_set in data["list"]:
                if first_city is None:
                    first_city = data_set['id']
                cities[data_set['id']] = {'name':data_set['name'],
                                          'country':data_set['sys']['country']}
        except urllib2.URLError, KeyError:
            print "error in weatherforecast"
            print "use default city 'Berlin'"
            return {'default':2950159, 'cities':{}}

        return {'default':first_city, 'cities':cities}

    def get_weather_forecast(self, hourly=True):
        self.hourly = hourly
        # only permit forecast queries every 30min, to save some api requests
        if self.forecast_query_date is not None and self.forecast_query_date - self.get_date() < 60 * 30:
            if hourly and self.forecast_temperatures_3hourly != []:
                return self.forecast_temperatures_3hourly
            elif not hourly and self.forecast_temperatures_daily != []:
                return self.forecast_temperatures_daily

        forecast_temperatures = []
        self.forecast_query_date = self.get_date()

        jsondata = cached_data('openweathermap', data_function=self.get_openweathermapdata, max_age=3600)
        data = json.loads(jsondata)

        for data_set in data["list"]:
            try:
                forecast_temperatures.append(data_set["main"]["temp"])
            except:
                logger.warning("WeatherForecast: Problems while json parsing")
                if "gdps" not in data_set:
                    logger.error("WeatherForecast: Couldn't read temperature values from openweathermap")
        logger.info("WeatherForecast: Fetched %d tempterature values" % len(forecast_temperatures))
        return forecast_temperatures

    def get_openweathermapdata(self):
        if self.hourly:
            # 3-hourly forecast for 5 days for Berlin
            url = "http://openweathermap.org/data/2.5/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5&mode=json"
        else:
            url = "http://openweathermap.org/data/2.5/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5?mode=daily_compact"
        try:
            return urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            logger.error("WeatherForecast: URLError during API call")
            # Use history data
            result = []
            for i in range(0, 40):
                result.append(
                    self.get_average_outside_temperature(self.get_date(), i))
            return result

    def get_temperature_estimate(self, date):
        """get most accurate forecast for given date
        that can be derived from 5 days forecast, 14 days forecast or from history data"""
        time_passed = (calendar.timegm(date.timetuple()) - self.env.now) / (60.0 * 60.0 * 24)  # in days
        if time_passed < 0.0 or time_passed > 13.0:
            history_data = self.get_average_outside_temperature(date)
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
        time_passed = int((calendar.timegm(date.timetuple()) - self.env.now) / (60.0 * 60.0))  # in hours
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
        time_passed = int((calendar.timegm(date.timetuple()) - self.env.now) / (60.0 * 60.0))  # in days
        weight = (time_passed % 24) / 24.0
        t0 = min(int(time_passed / 24), len(
            self.forecast_temperatures_daily) - 1)
        t1 = min(t0 + 1, len(self.forecast_temperatures_daily) - 1)
        a0 = self.forecast_temperatures_daily[t0]
        a1 = self.forecast_temperatures_daily[t1]
        return self.mix(a0, a1, weight)

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