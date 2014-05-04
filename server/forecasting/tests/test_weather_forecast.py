from django.test import TestCase
from mock import MagicMock, patch
import json
import urllib2
from StringIO import StringIO
from datetime import date
import datetime
import time
from django.utils.timezone import utc

from server.forecasting.forecasting.weather import WeatherForecast
from server.models import Sensor, Device, SensorValue, WeatherSource, WeatherValue



''''class ForecastingTest(unittest.TestCase):
    def test_test(self):
        cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
    def setUp(self):
        self.forecast = WeatherForecast()
        self.data = '{"list" : [{"main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(self.data), 'fill', '')
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
        expected_timestamp = datetime.datetime.fromtimestamp(0).replace(tzinfo=utc)
        time_mock = MagicMock(return_value = 0)
        self.forecast.get_date = MagicMock(return_value=0)

        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                self.forecast.update_weather_estimates()                    
                
        results = WeatherValue.objects.filter(temperature=30, timestamp = expected_timestamp)
        
        self.assertTrue(results)
    
    def test_time_of_forecast_three_hourly(self): 
        # consider requested time. a request is always made at the current date
        # and in a 3-hourly distance to the next request
        data = '{"list" : [{"main": {"temp": 30}}, {"main": {"temp": 30}}, {"main": {"temp": 30}}, {"main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
        
        time_mock = MagicMock(return_value = 0)
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                self.forecast.get_weather_forecast_three_hourly() 
                
        results = WeatherValue.objects.order_by('target_time')

        i = 0
        for entry in results:
            self.assertEqual(entry.target_time, datetime.datetime.fromtimestamp(0+i).replace(tzinfo=utc))
            i = i+10800 # seconds of three hour 3*60*60
    
    def test_get_weather_forecast(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            self.forecast.get_weather_forecast("test_url")
        self.api_answer_mock.assert_called_with("test_url")
    
    def test_wrong_list(self):
        ''' if a data set is not readable, save an invalid record an notify the system of the problem '''
        data = '{"list" : [{"main": {"temp": 30}}, {"broken": 0}]}'
        resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp      
        api_answer_mock = MagicMock(return_value = extern_information)
        
        with patch('urllib2.urlopen', api_answer_mock):
            self.forecast.get_weather_forecast("some_url")
        
        results = WeatherValue.objects.filter(temperature = -274) # not valid, beneath the absolute zero point  

    def test_set_up_records_out_of_json(self):
        expected_timestamp = datetime.datetime.fromtimestamp(0).replace(tzinfo=utc)
        expected_records = [WeatherValue(temperature = 30, timestamp=expected_timestamp)]   #'{"list" : [{"main": {"temp": 30}}]}'
        time_mock = MagicMock(return_value = 0)
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                records = self.forecast.set_up_records_out_of_json( json.loads(self.data))
        self.assertListEqual(records, expected_records)

    def test_update_weather_estimates(self):
        '''the update function should save new forecasts 
        if enough time passed since the last saving or the last savings
        were invalid.
        it should make the query for as much entries as possible. 
        for open weather map that means 3-hourly and daily
        '''
        #last_timestamp = datetime.datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
        # WeatherValue(timestamp = last_timestamp, temperature=20, target_time=)
        #time_mock = MagicMock(return_value = last_timestamp+31 Minute) #
        #with patch('time.time', time_mock):
                #self.forecast.update_weather_estimate()
        
        #results = WeatherValue.objects.filter(timestamp.hours and minutes = aktuelle  hour und minutes)
        #self.assertTrue(results)
        pass
    
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
        
        
                
if __name__ == '__main__':
    unittest.main()
