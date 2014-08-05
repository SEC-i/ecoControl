"""This module handles crawling, storing and retrieving of weather values.

It is split into two Classes.

.. autosummary::
    ~DemoWeather
    ~CurrentWeatherForecast

"""

import urllib2
import json
import time
import logging
import calendar
from datetime import datetime, timedelta

from server.forecasting.simulation.demodata.old_demands import outside_temperatures_2013, outside_temperatures_2012
from server.forecasting.helpers import cached_data,\
    approximate_index
from server.models import WeatherValue, RealWeatherValue
from django.utils.timezone import utc

logger = logging.getLogger('simulation')

demo_weather = None
current_weather = None

def get_temperature(env, date):
    """ General function to retrieve forecasts.
    Will decide upon the `env` parameter, if :class:`DemoWeather` or :class:`CurrentWeatherForecast` should be used.


    :param ``BaseEnvironment`` env: the current environment
    :param ``datetime`` date: the time of which to retrieve the weather(forecast)
    """
    global demo_weather
    global current_weather
    # check if demo_mode mode
    if env.demo_mode:
        if demo_weather == None:
            demo_weather = DemoWeather(env)

        if env.forecast:
            return demo_weather.get_temperature_estimate(date)
        else:
            return demo_weather.get_temperature(date)
    #real mode, get todays forecast
    else:
        if current_weather == None:
            current_weather = CurrentWeatherForecast(env)
        return current_weather.get_temperature_estimate(date)


class DemoWeather:
    """ Gets Weathervalues from the database. The demo_mode operates on stored data from the past.
    For maximum realism, the past data should contain the real weather values as well as stored weather forecasts.

    The data is stored in the database, with :class:`server.models.RealWeatherValue` for history weather and :class:`server.models.WeatherValue` for stored forecasts.
    """
    def __init__(self, env=None):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.hourly = True

        self.cache_day = {}
        self.cache_real_values = [[],[]]
        self.error_day_cache = {}

    def get_temperature(self,date):
        """ Retrieve a temperature at a certain time. The class will cache the
        values after the first query to speed up subsequent requests.

        :param datetime date: The time

        Raises an ``Exception`` if there are no values in the database for the current time.
        """
        if self.cache_real_values == [[],[]]:
            real_temps = RealWeatherValue.objects.all()
            for entry in real_temps:
                self.cache_real_values[0].append(calendar.timegm(entry.timestamp.utctimetuple()))
                self.cache_real_values[1].append(float(entry.temperature))

        if len(self.cache_real_values[1]) < 2:
            raise Exception("not enough weather values in database")
        idx = approximate_index(self.cache_real_values[0], calendar.timegm(date.utctimetuple()))
        return  self.cache_real_values[1][idx]

    def get_temperature_estimate(self, target_date):
        """Retrieve a forecasted temperature at a certain time. The target_date must be between 0 and 10 days away from the creation_date,
        as weather forecasts only cover 10 days.

        The class will cache the
        values after the first query to speed up subsequent requests.

        :param datetime date: The timepoint

        """

        time_passed = (target_date - datetime.fromtimestamp(self.env.initial_date)).total_seconds() / \
                (60.0 * 60.0 * 24)  # in days

        initial0 = datetime.fromtimestamp(self.env.initial_date).replace(minute=0,second=0)
        initial1 = initial0 + timedelta(hours=1)

        target_date = target_date.replace(hour=0,minute=0,second=0)
        target_date_key = target_date.strftime("%Y-%m-%d")



        if self.error_day_cache.has_key(target_date_key):
            return self.error_day_cache[target_date_key][target_date.hour]

        if not self.cache_day.has_key(target_date_key):
            forecasts_until_now = WeatherValue.objects.filter(timestamp__lte=initial0)
            if len(forecasts_until_now) == 0:
                #print "Warning, date_time not in weatherforecasts ", date_time, " getting real data" ,"initial", initial0
                return self.get_temperature(target_date)
            newest_creation_timestamp = forecasts_until_now.latest('timestamp').timestamp


            values0 = WeatherValue.objects.filter(timestamp=newest_creation_timestamp).filter(target_time__range = [target_date.replace(hour=0), target_date.replace(hour=23,minute=59)])
            day_values0 =  values0.order_by("-timestamp")

            test_list = [(float(v.temperature),v.target_time.hour) for v in day_values0]
            if len(test_list) < 24:
                self.error_day_cache[target_date_key] = self._fill_error_gaps(test_list, target_date)
                return self.error_day_cache[target_date_key][target_date.hour]

            self.cache_day[target_date_key] = [float(v.temperature) for v in day_values0]


        values0 =self.cache_day[target_date_key]
        return self.mix(values0[target_date.hour],values0[min(target_date.hour+1,23)], target_date.minute / 60.0)

    def _fill_error_gaps(self, input_list, date):
        """ fill gaps of data, if missing or prediction are asked for intervals > 10 days"""
        logger.warning("not enough dates in list "+  len(input_list) + " " + date)
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

    def mix(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        return time.time()  # for debugging, use self.env.now



class CurrentWeatherForecast:
    """ Gets the current Weatherforecast from an online service.
    This is http://api.openweathermap.org/ at the moment, but may change in future versions.
    """
    def __init__(self, env=None, city="Berlin"):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []
        self.hourly = True

        self.city_id = self.find_city(city)['default']

    def get_temperature_estimate(self, date):
        """Get the most accurate forecast for given date
        that can be derived from 5 days forecast, 14 days forecast or from history data.
        This is the public getter for forecasts and should be used

        :param datetime date: the timepoint for which to get the forecast
        :returns: temperature (float)"""
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
        """ Get the hourly forecast for the given date. """
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
        """ get the forecast for given date. This only has day accuracy, but the forecast span is longer"""
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

    def find_city(self, name):
        """returns a dictionary with city id, names and country based on the given search name
        the first search result is returned as 'default' too.

        :param string name: f.e. "Berlin"
        """
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
        """ retrieves an entire forecast. Tries to get forecast from internal list or filesystem cache.
        If that fails or data is too old, the online service will be queried"""
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
                logger.warning("CurrentWeatherForecast: Problems while json parsing")
                if "gdps" not in data_set:
                    logger.error("CurrentWeatherForecast: Couldn't read temperature values from openweathermap")
        logger.info("CurrentWeatherForecast: Fetched %d tempterature values" % len(forecast_temperatures))
        return forecast_temperatures

    def get_openweathermapdata(self):
        """ read from openweathermap. If this fails, use :meth:`~CurrentWeatherForecast.get_average_outside_temperature`"""
        if self.hourly:
            # 3-hourly forecast for 5 days for Berlin
            url = "http://openweathermap.org/data/2.5/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5&mode=json"
        else:
            url = "http://openweathermap.org/data/2.5/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5?mode=daily_compact"
        try:
            return urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            logger.error("CurrentWeatherForecast: URLError during API call")
            # Use history data
            result = []
            for i in range(0, 40):
                result.append(
                    self.get_average_outside_temperature(datetime.fromtimestamp(self.get_date()), i))
            return result





    def get_average_outside_temperature(self, date, offset_days=0):
        """ return an average Berlin temperature in 2012/2013 for a given date.

        :param int offset_days: offset the real days, f.e. to get some randomness
        """
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