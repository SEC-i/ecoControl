from django.test import TestCase
from mock import MagicMock, patch
import json
import urllib2
from StringIO import StringIO
from datetime import date

from server.forecasting.forecasting.weather import WeatherForecast
from server.models import Sensor, Device, SensorValue, WeatherSource, WeatherValue


''''class ForecastingTest(unittest.TestCase):
    def test_test(self):
        cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        data = '{"list" : [{"main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
        WeatherValue.objects.all().delete()
    
    def test_if_weather_sources_in_db(self):
        '''In the database should at least exist one weather source.'''
        source = WeatherSource.objects.all()[0]
        self.assertTrue(source.location)
                         
    def test_crawled_data_in_db(self):
        expected_timestamp = date.fromtimestamp(0)
        time_mock = MagicMock(return_value = 0)
        self.forecast.get_date = MagicMock(return_value=0)

        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                self.forecast.get_weather_forecast()                    
                
        results = WeatherValue.objects.filter(temperature=30, timestamp = expected_timestamp)
        
        self.assertTrue(results)
        # consider requested time and request time and other fields of Weather value
        # requests to the api shouldn't be done twice in a small time intervall
        # But: we need to seperate saving asking anyway.       
        # choose the right source for weather
    
    def test_time_of_forecast(self): 
        pass 
    
    def test_wrong_list(self):
        data = '{"list" : [{"main": {"temp": 30}}, {"broken": 0}]}'
        resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp      
        api_answer_mock = MagicMock(return_value = extern_information)
        
        with patch('urllib2.urlopen', api_answer_mock):
            self.forecast.get_weather_forecast()                  
                
if __name__ == '__main__':
    unittest.main()
