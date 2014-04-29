from django.test import TestCase
from mock import MagicMock, patch
import json
import urllib2
from StringIO import StringIO

from server.forecasting.forecasting.weather import WeatherForecast
from server.models import Sensor, Device, SensorValue, WeatherSource, WeatherValue


''''class ForecastingTest(unittest.TestCase):
    def test_test(self):
        cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
    def test_if_weather_sources_in_db(self):
        '''In the database should at least exist one weather source.'''
        source = WeatherSource.objects.all()[0]
        self.assertTrue(source.location)
                         
    def test_crawled_data_in_db(self):
        WeatherValue.objects.all().delete()
        forecast = WeatherForecast()
        data = '{"list" : [{"main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp
        api_answer_mock = MagicMock(return_value = extern_information)
        forecast.get_date = MagicMock(return_value=0)
        with patch('urllib2.urlopen', api_answer_mock):
            forecast.get_weather_forecast()           
        results = WeatherValue.objects.filter(temperature=30)
        self.assertTrue(results)
        # consider requested time and request time and other fields of Weather value
        # requests to the api shouldn't be donde twice in a small time intervall
        # But: we need to seperate saving asking anyway.       
        # choose the right source for weather
                
if __name__ == '__main__':
    unittest.main()
