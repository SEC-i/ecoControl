import unittest
from django.test import TestCase
from mock import MagicMock, patch
import json
import urllib2
from StringIO import StringIO
import datetime
import time
from django.utils.timezone import utc
from mock import Mock

from server.forecasting.forecasting.weather import WeatherForecast
import server.forecasting.forecasting.weather as weather
from server.models import Sensor, Device, SensorValue, WeatherSource, WeatherValue

absolute_zero_point = -273.15

class ForecastingTestDaily(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        self.data = '{"list": [{"dt":30, "temp": {"day": 30}}]}'
        resp = urllib2.addinfourl(StringIO(self.data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
        
        target_sec = 30 # dt
        target_time = aware_timestamp_from_seconds(target_sec).replace(
            hour=0, minute=0, second=0, microsecond=0)  
        
        seconds = 0
        self.time_mock = MagicMock(return_value = seconds)
        expected_timestamp = aware_timestamp_from_seconds(seconds)
        
        self.expected_weather_value = WeatherValue(temperature = 30, 
            timestamp = expected_timestamp, target_time = target_time)
        WeatherValue.objects.all().delete()
    
    def test_get_weather_forecast_daily_right_url(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            self.forecast.get_weather_forecast(daily=True)
        self.api_answer_mock.assert_called_with(self.forecast.daily_url)
            
    def test_get_weather_forecast(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', self.time_mock):
                result = self.forecast.get_weather_forecast(daily=True)
        self.assertTrue(len(result)==1)
        weathervalues_equal_attributes(result[0], self.expected_weather_value) # makes assertion
        
    def test_daily_records_out_of_json(self):
        "the method should return a list with WeatherValues with timestamp and target_time"
        input_json = json.loads(self.data)
        
        with patch('time.time', self.time_mock):
            result = self.forecast.set_up_records_out_of_json(input_json, daily=True)
        self.assertTrue(len(result)==1)
        weathervalues_equal_attributes(result[0], self.expected_weather_value)  # makes assertion
        
        # def test_wrong_list(self):
    #    ''' if a data set is not readable, save an invalid record an notify the system of the problem '''
        # data = '{"list" : [{"main": {"temp": 30}}, {"broken": 0}]}'
        # resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        # resp.code = 200
        # resp.msg = "Ok"
        # extern_information = resp      
        # api_answer_mock = MagicMock(return_value = extern_information)
        
        # with patch('urllib2.urlopen', api_answer_mock):
            # self.forecast.set_up_records_out_of_json()
        
        # results = WeatherValue.objects.filter(temperature < absolute_zero_point) # not valid, beneath the absolute zero point 
         

class ForecastingTestHourly(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        self.data = '{"list": [{"dt":30, "main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(self.data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
        
        target_sec = 30 # dt 
        target_time = aware_timestamp_from_seconds(target_sec).replace(
            minute=0, second=0, microsecond=0)    
        # the hourly target time should contain only the full hour
        
        seconds = 0
        self.time_mock = MagicMock(return_value = seconds)
        expected_timestamp = aware_timestamp_from_seconds(seconds)
        
        self.expected_weather_value = WeatherValue(temperature = 30, 
            timestamp = expected_timestamp, target_time = target_time)

    def test_get_weather_forecast_right_url(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            self.forecast.get_weather_forecast(daily=False)
        self.api_answer_mock.assert_called_with(self.forecast.three_hourly_url)
           
    def test_get_weather_forecast(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', self.time_mock):
                result = self.forecast.get_weather_forecast(daily=False)
        self.assertTrue(len(result)==1)
        weathervalues_equal_attributes(result[0], 
            self.expected_weather_value) # makes assertion
    
    def test_get_weather_forecast_with_almost_full_hour(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.
        If the returned target time is nearer at the next hour, store
        it for the next hour.'''
        
        self.data = '{"list": [{"dt":2100, "main": {"temp": 30}}]}'   
        resp = urllib2.addinfourl(StringIO(self.data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
        
        target_sec = 2100 # dt 35 Minutes
        full_hour = aware_timestamp_from_seconds(target_sec)
        target_time = full_hour.replace( 
            hour=full_hour.hour+1, minute=0, second=0, microsecond=0)    
        # the hourly target time should contain only the full hour
        expected_timestamp = aware_timestamp_from_seconds(self.time_mock())
        self.expected_weather_value = WeatherValue(temperature = 30, 
            timestamp = expected_timestamp, target_time = target_time)
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', self.time_mock):
                result = self.forecast.get_weather_forecast(daily=False)
        self.assertTrue(len(result)==1)
        weathervalues_equal_attributes(result[0], 
            self.expected_weather_value) # makes assertion

    def test_3hourly_records_out_of_json(self):
        "the method should return a list with WeatherValues with timestamp and target_time"
        input_json = json.loads(self.data)
        with patch('time.time', self.time_mock):
            result = self.forecast.set_up_records_out_of_json(input_json, daily = False)
        self.assertTrue(len(result)==1)
        weathervalues_equal_attributes(result[0],
            self.expected_weather_value) # makes assertion

    # def test_wrong_list(self):
    #    ''' if a data set is not readable, save an invalid record an notify the system of the problem '''
        # data = '{"list" : [{"main": {"temp": 30}}, {"broken": 0}]}'
        # resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        # resp.code = 200
        # resp.msg = "Ok"
        # extern_information = resp      
        # api_answer_mock = MagicMock(return_value = extern_information)
        
        # with patch('urllib2.urlopen', api_answer_mock):
            # self.forecast.set_up_records_out_of_json()
        
        # results = WeatherValue.objects.filter(temperature < absolute_zero_point) # not valid, beneath the absolute zero point 
         

class ForecastingDBTest(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        self.temperature = 30
        data = '{"list": [{"dt":30, "main": {"temp": 30}}]}'
        self.api_answer_mock = get_http_response_mock(data)
        
        data_daily = '{"list": [{"dt":30, "temp": {"day": 30}}]}' 
        self.api_answer_mock_daily = get_http_response_mock(data_daily)
        
        target_sec = 30 # dt
        self.hourly_target_time = aware_timestamp_from_seconds(target_sec).replace(
            minute=0, second=0, microsecond=0)
        self.daily_target_time = aware_timestamp_from_seconds(target_sec).replace(
            hour=0, minute=0, second=0, microsecond=0) 

        
        seconds = 0
        self.time_mock = MagicMock(return_value = seconds)
        self.timestamp = aware_timestamp_from_seconds(seconds)
        
        #self.expected_weather_value = WeatherValue(temperature = 30, 
        #    timestamp = expected_timestamp, target_time = target_time)
        
        WeatherValue.objects.all().delete()
            
    def test_if_weather_sources_in_db(self):
        '''In the database should at least exist one weather source.'''
        source = WeatherSource.objects.all()[0]
        self.assertTrue(source.location)
    
    def test_save_weather_forecast_three_hourly(self):
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', self.time_mock):
                self.forecast.save_weather_forecast_three_hourly()
        results = WeatherValue.objects.all().filter(temperature=self.temperature, 
            timestamp = self.timestamp, target_time=self.hourly_target_time)
        self.assertTrue(results)
        
    def test_save_weather_forecast_daily(self):
        # achtung! do you want to save four values?
        with patch('urllib2.urlopen', self.api_answer_mock_daily):
            with patch('time.time', self.time_mock):
                self.forecast.save_weather_forecast_daily()
        results = WeatherValue.objects.all().filter(temperature=self.temperature, 
            timestamp = self.timestamp, target_time=self.daily_target_time)
        self.assertTrue(results)
    
    def test_save_weather_forecast_daily_from_day_six(self):
        ''' We only need to save from the sixth to the 14th day, 
        because the three hourly forecast provides dates for the 
        first five days.
        '''
        # today + 5*25*60*60
        # 1399784400
        data_with_dates = '{"list": [{"dt":1399334400, "temp": {"day": 30 }}, {"dt":1399334400, "temp": {"day": 30}},{"dt":1399784460, "temp": {"day": 30}}]}'
        '''
        {"list":
            [
            {"dt":1399334400, "temp": {"day": 30}},
            {"dt":1399334400, "temp": {"day": 30}},
            {"dt":1399784460, "temp": {"day": 30}}
            ]
        }'''
        response_mock = get_http_response_mock(data_with_dates)
        today = 1399334400 #2014/5/6
        time_mock = MagicMock(return_value = today)
        timestamp_day_six = aware_timestamp_from_seconds(1399784460).\
                                replace(tzinfo=utc, 
                                    hour=0, minute=0, second=0, 
                                    microsecond=0)
        
        with patch('urllib2.urlopen', response_mock):
            with patch('time.time', time_mock):
                self.forecast.save_weather_forecast_daily_from_day_six()
        result = WeatherValue.objects.all()
        self.assertEqual(result[0].target_time, timestamp_day_six)
        
    # test if api returns expected target times and expected json format
    
    def test_calculate_weather_diff(self):
        '''calculate weather diff should return the difference between
        the last two temperatures saved for a time. You have to check if
        the temperatures are valid'''
        pass

    def test_get_average_outside_temperature(self):
        """get_average_outside_temperature(date, offset_days). Returns
        the average temperature of the given days of a year based on the
        last years"""
        # save entries for the same time period but different years
        # expected_temperature = calculate average
        # result = self.forecast.get_average_outside_temperature()
        # self.assertEqual(result)        
        
class UpdateWeatherEstimatesTest(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        daily_data = '{"cod":"200","message":2.2503,"city":{"id":2950159,"name":"Berlin","coord":{"lon":13.41053,"lat":52.524368},"country":"DE","population":0,"sys":{"population":0}},"cnt":14,"list":[{"dt":1399460400,"temp":{"day":14.67,"min":10.76,"max":14.67,"night":10.76,"eve":13.53,"morn":14.67},"pressure":1011.62,"humidity":80,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":8.41,"deg":253,"clouds":44,"rain":0.25},{"dt":1399546800,"temp":{"day":14.81,"min":11.63,"max":14.81,"night":12.07,"eve":13.98,"morn":11.63},"pressure":1015.82,"humidity":72,"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"speed":7.17,"deg":227,"clouds":80},{"dt":1399633200,"temp":{"day":15.12,"min":10.9,"max":15.12,"night":11.76,"eve":13.4,"morn":10.9},"pressure":1016.03,"humidity":79,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":6.32,"deg":239,"clouds":92,"rain":4},{"dt":1399719600,"temp":{"day":14,"min":10.04,"max":14,"night":11.58,"eve":12.98,"morn":10.04},"pressure":1010.5,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":5.1,"deg":211,"clouds":66,"rain":9.4},{"dt":1399806000,"temp":{"day":12.91,"min":9.93,"max":12.91,"night":9.93,"eve":11.16,"morn":11.51},"pressure":1002.52,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":7.85,"deg":245,"clouds":97,"rain":7.94},{"dt":1399892400,"temp":{"day":12.03,"min":10.12,"max":12.03,"night":10.53,"eve":11.91,"morn":10.12},"pressure":1011.86,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":8.19,"deg":254,"clouds":67,"rain":1.32},{"dt":1399978800,"temp":{"day":14.7,"min":8.98,"max":14.7,"night":8.98,"eve":12.11,"morn":9.73},"pressure":1015.62,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":5.3,"deg":256,"clouds":12,"rain":2.87},{"dt":1400065200,"temp":{"day":15.07,"min":10.89,"max":15.07,"night":12.88,"eve":14.43,"morn":10.89},"pressure":1018.33,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":2.98,"deg":184,"clouds":59,"rain":2.36},{"dt":1400151600,"temp":{"day":14.3,"min":11.23,"max":14.3,"night":11.23,"eve":13.85,"morn":12.71},"pressure":1014.67,"humidity":0,"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"speed":9.8,"deg":269,"clouds":20,"rain":4.32},{"dt":1400238000,"temp":{"day":15.52,"min":6.83,"max":15.52,"night":6.83,"eve":14.03,"morn":11.59},"pressure":1028.22,"humidity":0,"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"speed":6.09,"deg":291,"clouds":59},{"dt":1400324400,"temp":{"day":17.24,"min":10.14,"max":17.24,"night":11.86,"eve":16.34,"morn":10.14},"pressure":1029.04,"humidity":0,"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"speed":3.05,"deg":120,"clouds":7},{"dt":1400410800,"temp":{"day":18.58,"min":12.66,"max":18.58,"night":14.91,"eve":17.99,"morn":12.66},"pressure":1023.84,"humidity":0,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":8.68,"deg":131,"clouds":61,"rain":0.24},{"dt":1400497200,"temp":{"day":22.73,"min":15.39,"max":22.73,"night":17.04,"eve":21.9,"morn":15.39},"pressure":1016.4,"humidity":0,"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"speed":6.86,"deg":135,"clouds":3},{"dt":1400583600,"temp":{"day":22.35,"min":16.78,"max":22.35,"night":17.41,"eve":21.38,"morn":16.78},"pressure":1016.61,"humidity":0,"weather":[{"id":800,"main":"Clear","description":"sky is clear","icon":"01d"}],"speed":6.57,"deg":127,"clouds":0}]}'
        hourly_data = '{"cod":"200","message":0.243,"city":{"id":2950159,"name":"Berlin","coord":{"lon":13.41053,"lat":52.524368},"country":"DE","population":0,"sys":{"population":0}},"cnt":41,"list":[{"dt":1399464000,"main":{"temp":19.12,"temp_min":16.2,"temp_max":19.12,"pressure":1015.27,"sea_level":1021.03,"grnd_level":1015.27,"humidity":77,"temp_kf":2.92},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":24},"wind":{"speed":7.81,"deg":258.5},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-07 12:00:00"},{"dt":1399474800,"main":{"temp":17.95,"temp_min":15.17,"temp_max":17.95,"pressure":1016.79,"sea_level":1022.64,"grnd_level":1016.79,"humidity":73,"temp_kf":2.78},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":64},"wind":{"speed":7.51,"deg":264.001},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-07 15:00:00"},{"dt":1399485600,"main":{"temp":16.71,"temp_min":14.08,"temp_max":16.71,"pressure":1017.96,"sea_level":1023.79,"grnd_level":1017.96,"humidity":72,"temp_kf":2.63},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":68},"wind":{"speed":6.26,"deg":266.501},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-07 18:00:00"},{"dt":1399496400,"main":{"temp":14.79,"temp_min":12.31,"temp_max":14.79,"pressure":1019.08,"sea_level":1024.93,"grnd_level":1019.08,"humidity":76,"temp_kf":2.49},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":32},"wind":{"speed":5.07,"deg":254.501},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-07 21:00:00"},{"dt":1399507200,"main":{"temp":13.48,"temp_min":11.14,"temp_max":13.48,"pressure":1019.37,"sea_level":1025.45,"grnd_level":1019.37,"humidity":86,"temp_kf":2.34},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":4.82,"deg":243.001},"rain":{"3h":0.25},"sys":{"pod":"n"},"dt_txt":"2014-05-08 00:00:00"},{"dt":1399518000,"main":{"temp":12.87,"temp_min":10.68,"temp_max":12.87,"pressure":1019.92,"sea_level":1025.69,"grnd_level":1019.92,"humidity":86,"temp_kf":2.19},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":64},"wind":{"speed":4.66,"deg":247.004},"rain":{"3h":0.25},"sys":{"pod":"n"},"dt_txt":"2014-05-08 03:00:00"},{"dt":1399528800,"main":{"temp":13.88,"temp_min":11.84,"temp_max":13.88,"pressure":1020.13,"sea_level":1026.14,"grnd_level":1020.13,"humidity":89,"temp_kf":2.05},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":68},"wind":{"speed":4.67,"deg":236.502},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-08 06:00:00"},{"dt":1399539600,"main":{"temp":16.21,"temp_min":14.31,"temp_max":16.21,"pressure":1019.94,"sea_level":1025.81,"grnd_level":1019.94,"humidity":81,"temp_kf":1.9},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":24},"wind":{"speed":5.71,"deg":231.002},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-08 09:00:00"},{"dt":1399550400,"main":{"temp":17.1,"temp_min":15.35,"temp_max":17.1,"pressure":1019.39,"sea_level":1025.16,"grnd_level":1019.39,"humidity":74,"temp_kf":1.75},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":56},"wind":{"speed":6.47,"deg":230.501},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-08 12:00:00"},{"dt":1399561200,"main":{"temp":17.15,"temp_min":15.54,"temp_max":17.15,"pressure":1019.08,"sea_level":1024.87,"grnd_level":1019.08,"humidity":71,"temp_kf":1.61},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":76},"wind":{"speed":6.56,"deg":238.503},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-08 15:00:00"},{"dt":1399572000,"main":{"temp":15.85,"temp_min":14.39,"temp_max":15.85,"pressure":1019.04,"sea_level":1024.78,"grnd_level":1019.04,"humidity":70,"temp_kf":1.46},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":44},"wind":{"speed":5.46,"deg":235.509},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-08 18:00:00"},{"dt":1399582800,"main":{"temp":14.15,"temp_min":12.83,"temp_max":14.15,"pressure":1018.26,"sea_level":1024.1,"grnd_level":1018.26,"humidity":71,"temp_kf":1.32},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":56},"wind":{"speed":3.77,"deg":214.003},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-08 21:00:00"},{"dt":1399593600,"main":{"temp":13.28,"temp_min":12.11,"temp_max":13.28,"pressure":1016.73,"sea_level":1022.57,"grnd_level":1016.73,"humidity":78,"temp_kf":1.17},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":80},"wind":{"speed":3.41,"deg":192.501},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-09 00:00:00"},{"dt":1399604400,"main":{"temp":12.79,"temp_min":11.77,"temp_max":12.79,"pressure":1014.21,"sea_level":1020.18,"grnd_level":1014.21,"humidity":98,"temp_kf":1.02},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":5.61,"deg":198.002},"rain":{"3h":2.75},"sys":{"pod":"n"},"dt_txt":"2014-05-09 03:00:00"},{"dt":1399615200,"main":{"temp":13.13,"temp_min":12.25,"temp_max":13.13,"pressure":1012.75,"sea_level":1018.49,"grnd_level":1012.75,"humidity":98,"temp_kf":0.88},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":7.91,"deg":205.5},"rain":{"3h":2},"sys":{"pod":"d"},"dt_txt":"2014-05-09 06:00:00"},{"dt":1399626000,"main":{"temp":16.05,"temp_min":15.32,"temp_max":16.05,"pressure":1013.32,"sea_level":1019.24,"grnd_level":1013.32,"humidity":98,"temp_kf":0.73},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":68},"wind":{"speed":9.16,"deg":245.002},"rain":{"3h":0.5},"sys":{"pod":"d"},"dt_txt":"2014-05-09 09:00:00"},{"dt":1399636800,"main":{"temp":15.63,"temp_min":15.04,"temp_max":15.63,"pressure":1014.94,"sea_level":1020.55,"grnd_level":1014.94,"humidity":95,"temp_kf":0.58},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":64},"wind":{"speed":8.4,"deg":250.502},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-09 12:00:00"},{"dt":1399647600,"main":{"temp":15.64,"temp_min":15.2,"temp_max":15.64,"pressure":1014.94,"sea_level":1020.59,"grnd_level":1014.94,"humidity":87,"temp_kf":0.44},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":64},"wind":{"speed":7.16,"deg":243.505},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-09 15:00:00"},{"dt":1399658400,"main":{"temp":14.46,"temp_min":14.17,"temp_max":14.46,"pressure":1014.86,"sea_level":1020.71,"grnd_level":1014.86,"humidity":78,"temp_kf":0.29},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"clouds":{"all":88},"wind":{"speed":5.67,"deg":248.5},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-09 18:00:00"},{"dt":1399669200,"main":{"temp":11.93,"temp_min":11.78,"temp_max":11.93,"pressure":1015.07,"sea_level":1020.83,"grnd_level":1015.07,"humidity":78,"temp_kf":0.15},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":64},"wind":{"speed":5.12,"deg":245.509},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-09 21:00:00"},{"dt":1399680000,"main":{"temp":10.59,"temp_min":10.59,"temp_max":10.59,"pressure":1015.42,"sea_level":1021.18,"grnd_level":1015.42,"humidity":85},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":32},"wind":{"speed":6.96,"deg":249.5},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-10 00:00:00"},{"dt":1399690800,"main":{"temp":9.99,"temp_min":9.99,"temp_max":9.99,"pressure":1016.18,"sea_level":1022.07,"grnd_level":1016.18,"humidity":86},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"clouds":{"all":88},"wind":{"speed":6.96,"deg":258.502},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-10 03:00:00"},{"dt":1399701600,"main":{"temp":10.9,"temp_min":10.9,"temp_max":10.9,"pressure":1017.06,"sea_level":1022.85,"grnd_level":1017.06,"humidity":86},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":80},"wind":{"speed":7.47,"deg":248.004},"rain":{"3h":0.5},"sys":{"pod":"d"},"dt_txt":"2014-05-10 06:00:00"},{"dt":1399712400,"main":{"temp":11.02,"temp_min":11.02,"temp_max":11.02,"pressure":1017.36,"sea_level":1023.41,"grnd_level":1017.36,"humidity":90},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":7.61,"deg":263.001},"rain":{"3h":0.5},"sys":{"pod":"d"},"dt_txt":"2014-05-10 09:00:00"},{"dt":1399723200,"main":{"temp":13.91,"temp_min":13.91,"temp_max":13.91,"pressure":1017.95,"sea_level":1023.73,"grnd_level":1017.95,"humidity":80},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":64},"wind":{"speed":6.41,"deg":267.511},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-10 12:00:00"},{"dt":1399734000,"main":{"temp":14.9,"temp_min":14.9,"temp_max":14.9,"pressure":1016.66,"sea_level":1022.4,"grnd_level":1016.66,"humidity":74},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":24},"wind":{"speed":5.65,"deg":255.5},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-10 15:00:00"},{"dt":1399744800,"main":{"temp":13.71,"temp_min":13.71,"temp_max":13.71,"pressure":1015.01,"sea_level":1020.92,"grnd_level":1015.01,"humidity":70},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":80},"wind":{"speed":4.48,"deg":233.001},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-10 18:00:00"},{"dt":1399755600,"main":{"temp":11.83,"temp_min":11.83,"temp_max":11.83,"pressure":1013.26,"sea_level":1019.1,"grnd_level":1013.26,"humidity":89},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":80},"wind":{"speed":3.87,"deg":207.501},"rain":{"3h":0.5},"sys":{"pod":"n"},"dt_txt":"2014-05-10 21:00:00"},{"dt":1399766400,"main":{"temp":10.98,"temp_min":10.98,"temp_max":10.98,"pressure":1009.95,"sea_level":1015.74,"grnd_level":1009.95,"humidity":87},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04n"}],"clouds":{"all":92},"wind":{"speed":4.56,"deg":181.002},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-11 00:00:00"},{"dt":1399777200,"main":{"temp":10.69,"temp_min":10.69,"temp_max":10.69,"pressure":1006.71,"sea_level":1012.5,"grnd_level":1006.71,"humidity":96},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10n"}],"clouds":{"all":92},"wind":{"speed":5.35,"deg":186.506},"rain":{"3h":1.5},"sys":{"pod":"n"},"dt_txt":"2014-05-11 03:00:00"},{"dt":1399788000,"main":{"temp":11.22,"temp_min":11.22,"temp_max":11.22,"pressure":1004.51,"sea_level":1010.22,"grnd_level":1004.51,"humidity":100},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":92},"wind":{"speed":4.01,"deg":200.503},"rain":{"3h":1},"sys":{"pod":"d"},"dt_txt":"2014-05-11 06:00:00"},{"dt":1399798800,"main":{"temp":12.35,"temp_min":12.35,"temp_max":12.35,"pressure":1003.68,"sea_level":1009.56,"grnd_level":1003.68,"humidity":100},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":64},"wind":{"speed":3.66,"deg":232.502},"rain":{"3h":3},"sys":{"pod":"d"},"dt_txt":"2014-05-11 09:00:00"},{"dt":1399809600,"main":{"temp":12.48,"temp_min":12.48,"temp_max":12.48,"pressure":1004.22,"sea_level":1009.98,"grnd_level":1004.22,"humidity":100},"weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],"clouds":{"all":92},"wind":{"speed":6.48,"deg":252},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-11 12:00:00"},{"dt":1399820400,"main":{"temp":13,"temp_min":13,"temp_max":13,"pressure":1004.83,"sea_level":1010.55,"grnd_level":1004.83,"humidity":99},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":24},"wind":{"speed":6.86,"deg":247.005},"rain":{"3h":1},"sys":{"pod":"d"},"dt_txt":"2014-05-11 15:00:00"},{"dt":1399831200,"main":{"temp":11.45,"temp_min":11.45,"temp_max":11.45,"pressure":1005.76,"sea_level":1011.57,"grnd_level":1005.76,"humidity":92},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":68},"wind":{"speed":5.17,"deg":241.001},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-11 18:00:00"},{"dt":1399842000,"main":{"temp":10.23,"temp_min":10.23,"temp_max":10.23,"pressure":1006.6,"sea_level":1012.5,"grnd_level":1006.6,"humidity":92},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":24},"wind":{"speed":4.41,"deg":215.502},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-11 21:00:00"},{"dt":1399852800,"main":{"temp":9.11,"temp_min":9.11,"temp_max":9.11,"pressure":1006.77,"sea_level":1012.54,"grnd_level":1006.77,"humidity":94},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"clouds":{"all":64},"wind":{"speed":5.47,"deg":213.001},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-12 00:00:00"},{"dt":1399863600,"main":{"temp":8.71,"temp_min":8.71,"temp_max":8.71,"pressure":1006.49,"sea_level":1012.36,"grnd_level":1006.49,"humidity":91},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":20},"wind":{"speed":6.26,"deg":219.003},"rain":{"3h":0},"sys":{"pod":"n"},"dt_txt":"2014-05-12 03:00:00"},{"dt":1399874400,"main":{"temp":9.87,"temp_min":9.87,"temp_max":9.87,"pressure":1007.53,"sea_level":1013.39,"grnd_level":1007.53,"humidity":96},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":68},"wind":{"speed":6.56,"deg":225.009},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-12 06:00:00"},{"dt":1399885200,"main":{"temp":11.25,"temp_min":11.25,"temp_max":11.25,"pressure":1008.65,"sea_level":1014.51,"grnd_level":1008.65,"humidity":95},"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"clouds":{"all":64},"wind":{"speed":6.11,"deg":237.504},"rain":{"3h":1},"sys":{"pod":"d"},"dt_txt":"2014-05-12 09:00:00"},{"dt":1399896000,"main":{"temp":13.76,"temp_min":13.76,"temp_max":13.76,"pressure":1009.72,"sea_level":1015.54,"grnd_level":1009.72,"humidity":88},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],"clouds":{"all":56},"wind":{"speed":4.92,"deg":236.003},"rain":{"3h":0},"sys":{"pod":"d"},"dt_txt":"2014-05-12 12:00:00"}]}'  
        self.now = 1399464000 
        
        current_time = time.gmtime(self.now)
        hours = current_time.tm_hour
        self.current_day = self.now - hours*60*60
        
        last_target_time = self.current_day+13*24*60*60 #day 13, we should have values for day 14
        self.last_target_timestamp = aware_timestamp_from_seconds(
                                            last_target_time)\
                                    .replace(hour = 0, minute=0, 
                                            second=0, microsecond=0)
        
        self.early_new_stamp = aware_timestamp_from_seconds(self.current_day-60)
       
        self.time_mock = MagicMock(return_value = self.now)
        self.now_timestamp = aware_timestamp_from_seconds(self.now)
        response_daily = get_http_response(daily_data)
        response_hourly = get_http_response(hourly_data)
        
        def response(url):
            if(url==self.forecast.three_hourly_url):
                return response_hourly
            elif(url==self.forecast.daily_url):
                return response_daily
        self.response_mock = MagicMock(side_effect=response)
        
        WeatherValue.objects.all().delete()    
        '''the update function should save new forecasts 
        if enough time passed since the last saving or the last savings
        were invalid.
        it should make the query for as much entries as possible. 
        for open weather map that means 3-hourly and daily
        '''
        
    def test_crawled_data_in_db(self):
        '''the update function should save new forecasts 
        if 30 minutes passed since the last saving
        '''
        time_diff = self.now-31*60 
        last_timestamp = aware_timestamp_from_seconds(time_diff)
        WeatherValue(timestamp = last_timestamp, temperature=20, 
            target_time=last_timestamp).save()
        
        #with patch('urllib2.urlopen', self.response_mock):
            #with patch('time.time', self.time_mock):
                #self.forecast.update_weather_estimates()   
        self.forecast.update_weather_estimates() 
        results = WeatherValue.objects.filter(
            timestamp__gt = self.early_new_stamp,
            target_time__lt = self.last_target_timestamp 
            )
        '''results = WeatherValue.objects.all()
        for entry in results:
            print "WeatherValue(timestamp='{0}', target_time='{1}', temperature={2}).save()".format(entry.timestamp, entry.target_time, entry.temperature)
            #        WeatherValue(timestamp='2014-05-07 14:00:00+00:00', target_time='2014-05-07 14:00:00+00:00', temperature=19.12).save()  
        '''
        self.assertTrue(results)

    def test_to_little_time_passed(self):
        '''the update function shouldn't save new forecasts 
        if less than 30 minutes passed since the last savings.
        '''
        time_diff = self.now-15*60 
        last_timestamp = aware_timestamp_from_seconds(time_diff)
        WeatherValue(timestamp = last_timestamp,
                    temperature=20, 
                    target_time=last_timestamp).save()
        
        with patch('urllib2.urlopen', self.response_mock):
            with patch('time.time', self.time_mock):
                    self.forecast.update_weather_estimates()

        results = WeatherValue.objects.filter( 
            timestamp__gt = self.early_new_stamp,
            target_time__gt = self.last_target_timestamp)
        self.assertFalse(results)
    
    def test_no_values_saved(self):
        '''the update function should save new forecasts 
        if there aren't savings in the database.
        '''        
        with patch('urllib2.urlopen', self.response_mock):
            with patch('time.time', self.time_mock):
                    self.forecast.update_weather_estimates()
        results = WeatherValue.objects.all()
        self.assertTrue(results)        
    
    def test_only_invalid_values_saved(self):
        ''' the update function should save new forecasts 
        if there are only invalid records in the database.
        '''
        WeatherValue(timestamp = self.early_new_stamp, temperature= -274, 
            target_time=self.early_new_stamp).save()
        
        with patch('urllib2.urlopen', self.response_mock):
            with patch('time.time', self.time_mock):
                    self.forecast.update_weather_estimates()
    
        results = WeatherValue.objects.exclude(temperature= -274)
        self.assertTrue(results)  
    
    def test_invalid_and_valid_values_saved(self):
        '''it shouldn't save new forecasts, if the latest valid entry is new enough
        '''
        earlier_stamp = aware_timestamp_from_seconds(self.now-2*60) # one minute earlier than the early_new_stamp
        
        WeatherValue(timestamp = self.early_new_stamp, temperature= -274, 
            target_time=self.early_new_stamp).save()
            
        WeatherValue(timestamp = earlier_stamp, temperature= 20, 
            target_time=earlier_stamp).save() 
        
        with patch('urllib2.urlopen', self.response_mock):
            with patch('time.time', self.time_mock):
                    self.forecast.update_weather_estimates()
                    
        results = WeatherValue.objects.all()
        self.assertLess(len(results),3)

    
    def test_get_latest_valid_time(self):
        ''' Gets an list of WeatherValues ordered by their timestamp.
        Should return the timestamp of a valid value with the latest
        timestamp.'''
        values = []
        old_time = aware_timestamp_from_seconds(0)
        values.append(WeatherValue(temperature = 30, timestamp=old_time))
        latest_time = aware_timestamp_from_seconds(60)
        values.append(WeatherValue(temperature = -280, 
            timestamp=latest_time))
        timestamp = self.forecast.get_latest_valid_time(values)
        self.assertEqual(timestamp, old_time)
        
    def test_get_latest_valid_time_only_invalid(self):
        ''' Gets an list of WeatherValues ordered by their timestamp.
        Should return the timestamp of a valid value with the latest
        timestamp.'''
        latest_time = aware_timestamp_from_seconds(60)
        WeatherValue(temperature = -274, 
            timestamp=latest_time, 
            target_time=aware_timestamp_from_seconds(0)).save()
        values = WeatherValue.objects.all()
        timestamp = self.forecast.get_latest_valid_time(values)
        self.assertFalse(timestamp)
 
class GetWeatherForecastURLErrorTest(unittest.TestCase):
    def setUp(self):
        self.mock = MagicMock(side_effect=urllib2.URLError('No Response'))
        self.fcast = WeatherForecast()
    
    def test_url_error_handled(self):
        ''' if a data set is not readable, save an invalid record an notify the system of the problem '''
        with patch('urllib2.urlopen', self.mock):
            try:
                self.fcast.get_weather_forecast()
            except urllib2.URLError:
                self.fail("the weather forecast should know how to handle the unavailability of the weather api.")
    
    def test_url_error_logged(self):
        logger = weather.logger
        logger.warning = Mock()
        with patch('urllib2.urlopen', self.mock):
            self.fcast.get_weather_forecast()
        argument = logger.warning.call_args[0][0]
        self.assertIn("Couln't reach", argument)
    
    def test_return_value(self):
        '''there should be invalid return values.'''
        with patch('urllib2.urlopen', self.mock):
            result = self.fcast.get_weather_forecast()
        self.assertTrue(result, "get_weather_forecast should return values.")
        for entry in result:
            self.assertLess(float(entry.temperature), absolute_zero_point)
            
class ApiWorksAsExpectedTest(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        try:
            result = urllib2.urlopen(self.forecast.three_hourly_url)
            jsondata = result.read()
            self.hourly_data = json.loads(jsondata)
            self.three_valid = True
        except urllib2.URLError, e:
            self.three_valid = False

        try:
            result = urllib2.urlopen(self.forecast.daily_url)
            jsondata = result.read()
            self.daily_data = json.loads(jsondata)
            self.daily_valid = True
        except urllib2.URLError, e:
            self.daily_valid = False
        
        if not self.three_valid and not self.daily_valid:
            self.fail('Cannot access urls. Check internet connection. Or the API has changed again.')
        
    def test_three_hourly_url(self):
        if not self.three_valid:
            self.fail('Cannot acces hourly data. The url is not valid')
            
    def test_daily_url(self):
        if not self.daily_valid:
            self.fail('Cannot acces daily data. The url is not valid')
    
    def test_three_hourly_json(self):
        if self.three_valid:
            try:
                self.forecast.set_up_records_out_of_json(self.hourly_data, daily=False)
            except KeyError:
                self.fail('Json for hourly data, has an unexpected structure.')

    def test_daily_json(self):
        if self.daily_valid:
            try:
                self.forecast.set_up_records_out_of_json(self.daily_data, daily=True)
            except KeyError:
                self.fail('Json for daily data, has an unexpected structure.')
                
    def test_hourly_values(self):
        pass
        '''We expect from the hour which is nearest to the current time
        every three hours a value.
        '''
        '''
        if not self.three_valid:
            return
        records = self.forecast.set_up_records_out_of_json(self.hourly_data, daily=False)
        for i in records:
            print i.target_time
 
        stamp_naive = datetime.datetime.fromtimestamp(time.time())
        
        current_hour = stamp_naive.hour  
        print current_hour
        last_measurement = current_hour - current_hour % 3

        current_day_count = (24 - last_measurement)/3 # the current day has less measurements,
        next_four_days_count = 32 # 4*8, four days. eight measurements
        expected_count =  current_day_count + next_four_days_count
        
        self.assertEqual(len(records), expected_count)
         
        # the full days have per d  
        '''      
        
            

class GetWeatherTest(TestCase):
    
    def setUp(self):
        self.saveRecords()
        self.begin_seconds = 1400133600 #2014-05-15 08:00:00+00:00
        self.end_seconds = 1401228000
        now_stamp = 1400137394
        self.time_mock = MagicMock(return_value = now_stamp)
        self.forecast = WeatherForecast()
    
    def test_get_temperature_estimate_of_5days_date(self):
        '''get most accurate forecast for given date
        that can be derived from 5 days forecast, 14 days forecast or from history data.
        '''
        # case 1: the date is in the next five days. three hourly accurate.
        # return the temperature of the nearest target_time
        now = self.begin_seconds+2*24*60*60+23 # 2014-07-15 08:00:23+00:00
        now_stamp = aware_timestamp_from_seconds(now)
        with patch('time.time', self.time_mock):
            temperature = self.forecast.get_temperature_estimate(now_stamp)
        expected_temperature = '11.65'
        self.assertEqual(temperature, expected_temperature)
       
    def test_get_temperature_estimate_of_14days_date(self):
        # case 2: the date is in the next fourteen days. daily accurate.
        '''
        results = WeatherValue.objects.all()
        for entry in results:
            print "WeatherValue(timestamp={0}, target_time={1}, temperature={2})".format(entry.timestamp, entry.target_time, entry.temperature)
            #WeatherValue(timestamp='2014-05-07 14:00:00+00:00', target_time='2014-05-07 14:00:00+00:00', temperature=19.12).save()  
        '''
        now = self.begin_seconds+10*24*60*60+23  #'2014-05-25 8:00:23+00:00'
        now_stamp = aware_timestamp_from_seconds(now)
        with patch('time.time', self.time_mock):
            temperature = self.forecast.get_temperature_estimate(now_stamp)
        expected_temperature = '24.21'
        self.assertEqual(temperature, expected_temperature)
        
    def test_get_temperature_estimate_of_date_with_random_hour(self):
        # case 2: the date is in the next fourteen days. daily accurate.
        now = self.begin_seconds+10*24*60*60 - 10*60*60  # 2014-05-24 22:00:00+00:00
        now_stamp = aware_timestamp_from_seconds(now)
        with patch('time.time', self.time_mock):
            temperature = self.forecast.get_temperature_estimate(now_stamp)
        expected_temperature = '21.15'
        self.assertEqual(temperature, expected_temperature)
        
        
        
        # case 3: the date is in the past. We should know the correct temperature at least accurate for 15 minutes
        # it should return the newest entry
                # the date has a time which is not saved
    
    '''
    get_temperature_estimate
    get_forecast_temperature_hourly
    get_forecast_temperature_daily
    get_average_outside_temperature
    '''
    def saveRecords(self):
        WeatherValue(timestamp='2014-05-15 09:03:14.447479+00:00', target_time='2014-05-15 08:00:00+00:00', temperature=9.45).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447603+00:00', target_time='2014-05-15 11:00:00+00:00', temperature=12.66).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447674+00:00', target_time='2014-05-15 14:00:00+00:00', temperature=15).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447742+00:00', target_time='2014-05-15 17:00:00+00:00', temperature=15.65).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447809+00:00', target_time='2014-05-15 20:00:00+00:00', temperature=13.24).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447875+00:00', target_time='2014-05-15 23:00:00+00:00', temperature=10.28).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.447940+00:00', target_time='2014-05-16 02:00:00+00:00', temperature=7.9).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448013+00:00', target_time='2014-05-16 05:00:00+00:00', temperature=6.42).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448078+00:00', target_time='2014-05-16 08:00:00+00:00', temperature=9.89).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448144+00:00', target_time='2014-05-16 11:00:00+00:00', temperature=15.17).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448208+00:00', target_time='2014-05-16 14:00:00+00:00', temperature=17.22).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448273+00:00', target_time='2014-05-16 17:00:00+00:00', temperature=16.89).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448337+00:00', target_time='2014-05-16 20:00:00+00:00', temperature=15.45).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448400+00:00', target_time='2014-05-16 23:00:00+00:00', temperature=11.27).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448471+00:00', target_time='2014-05-17 02:00:00+00:00', temperature=8.26).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448535+00:00', target_time='2014-05-17 05:00:00+00:00', temperature=7.95).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448601+00:00', target_time='2014-05-17 08:00:00+00:00', temperature=11.65).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448665+00:00', target_time='2014-05-17 11:00:00+00:00', temperature=16.71).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448730+00:00', target_time='2014-05-17 14:00:00+00:00', temperature=18.67).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448794+00:00', target_time='2014-05-17 17:00:00+00:00', temperature=19).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448915+00:00', target_time='2014-05-17 20:00:00+00:00', temperature=16.74).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.448998+00:00', target_time='2014-05-17 23:00:00+00:00', temperature=12.63).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449073+00:00', target_time='2014-05-18 02:00:00+00:00', temperature=10.03).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449137+00:00', target_time='2014-05-18 05:00:00+00:00', temperature=8.4).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449200+00:00', target_time='2014-05-18 08:00:00+00:00', temperature=12.45).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449263+00:00', target_time='2014-05-18 11:00:00+00:00', temperature=18.01).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449327+00:00', target_time='2014-05-18 14:00:00+00:00', temperature=18.52).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449391+00:00', target_time='2014-05-18 17:00:00+00:00', temperature=16.58).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449462+00:00', target_time='2014-05-18 20:00:00+00:00', temperature=13.56).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449525+00:00', target_time='2014-05-18 23:00:00+00:00', temperature=10.48).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449590+00:00', target_time='2014-05-19 02:00:00+00:00', temperature=8.07).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449654+00:00', target_time='2014-05-19 05:00:00+00:00', temperature=7.21).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449718+00:00', target_time='2014-05-19 08:00:00+00:00', temperature=11.69).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449781+00:00', target_time='2014-05-19 11:00:00+00:00', temperature=14.35).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449844+00:00', target_time='2014-05-19 14:00:00+00:00', temperature=16.01).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449914+00:00', target_time='2014-05-19 17:00:00+00:00', temperature=14.42).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.449978+00:00', target_time='2014-05-19 20:00:00+00:00', temperature=14.28).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.450041+00:00', target_time='2014-05-19 23:00:00+00:00', temperature=12.78).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.450104+00:00', target_time='2014-05-20 02:00:00+00:00', temperature=13.74).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534157+00:00', target_time='2014-05-20 00:00:00+00:00', temperature=21.05).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534221+00:00', target_time='2014-05-21 00:00:00+00:00', temperature=23.61).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534285+00:00', target_time='2014-05-22 00:00:00+00:00', temperature=23.26).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534348+00:00', target_time='2014-05-23 00:00:00+00:00', temperature=18.25).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534412+00:00', target_time='2014-05-24 00:00:00+00:00', temperature=21.15).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534476+00:00', target_time='2014-05-25 00:00:00+00:00', temperature=24.21).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534539+00:00', target_time='2014-05-26 00:00:00+00:00', temperature=25.93).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534602+00:00', target_time='2014-05-27 00:00:00+00:00', temperature=27.56).save()
        WeatherValue(timestamp='2014-05-15 09:03:14.534665+00:00', target_time='2014-05-28 00:00:00+00:00', temperature=25.28).save()
       
def aware_timestamp_from_seconds(seconds):
    naive = datetime.datetime.fromtimestamp(seconds)
    return naive.replace(tzinfo=utc)
    
def weathervalues_equal_attributes(value1, value2):
    assert value1.temperature == value2.temperature, "{0} != {1}".format(value1.temperature, value2.temperature)
    assert value1.timestamp == value2.timestamp, "{0} != {1}".format(value1.timestamp, value2.timestamp)
    assert value1.target_time == value2.target_time, "{0} != {1}".format(value1.target_time, value2.target_time)  
    
def get_http_response(content):
    resp = urllib2.addinfourl(StringIO(content), 'fill', '')
    resp.code = 200
    resp.msg = "Ok"
    return resp

def get_http_response_mock(content):
    extern_information = get_http_response(content)  
    return MagicMock(return_value = extern_information)


                
if __name__ == '__main__':
    unittest.main()
