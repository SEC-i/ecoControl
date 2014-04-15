import urllib2
import json
from systems.data import outside_temperatures_2013, outside_temperatures_2012
import time
import datetime


class WeatherForecast:

    def __init__(self, env=None):
        self.env = env

        self.forecast_query_date = None
        self.forecast_temperatures_3hourly = []
        self.forecast_temperatures_daily = []

    def get_weather_forecast(self, hourly=True):
        # only permit forecast queries every 30min, to save some api requests
        if self.forecast_query_date is not None and self.forecast_query_date - self.get_date() < 60 * 30:
            if hourly and self.forecast_temperatures_3hourly != []:
                return self.forecast_temperatures_3hourly
            elif not hourly and self.forecast_temperatures_daily != []:
                return self.forecast_temperatures_daily

        if hourly:
            # 3-hourly forecast for 5 days for Berlin
            url = "http://openweathermap.org/data/2.3/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5&mode=json"
        else:
            url = "http://openweathermap.org/data/2.3/forecast/city?q=Berlin&units=metric&APPID=b180579fb094bd498cdeab9f909870a5?mode=daily_compact"
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
                    # last value of data seams always to be gdps
                    if "gdps" not in data_set:
                        print "error reading temperatures from: \n", json.dumps(data_set, sort_keys=True, indent=4, separators=(',', ': '))
            print "read ", len(forecast_temperatures), "temperatures", "hourly = ", hourly

        except urllib2.URLError, e:
            print e
            # Use history data
            result = []
            for i in range(0, 40):
                result.append(
                    self.get_average_outside_temperature(self.get_date(), i))
            return result

        return forecast_temperatures

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

    def mix(self, a, b, x):
        return a * (1 - x) + b * x

    def get_date(self):
        # return self.env.now
        return time.time()  # for debugging, use self.env.now otherwise
