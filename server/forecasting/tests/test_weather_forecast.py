import unittest
from django.test import TestCase
from mock import MagicMock, patch
import json
import urllib2
from StringIO import StringIO
import datetime
import time
from django.utils.timezone import utc

from server.forecasting.forecasting.weather import WeatherForecast
from server.models import Sensor, Device, SensorValue, WeatherSource, WeatherValue

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
            self.assertEqual(entry.target_time, 
                datetime.datetime.fromtimestamp(0+i).replace(tzinfo=utc))
            i = i+10800 # seconds of three hour 3*60*60
    
    def test_get_weather_forecast(self):
        '''the function returns the temperatures as a list of TemperatureValues.
        it opens the given url of openweather map ans extracts the data.'''
        with patch('urllib2.urlopen', self.api_answer_mock):
            self.forecast.get_weather_forecast("test_url")
        self.api_answer_mock.assert_called_with("test_url")
    
        # commented out because I rather see the error
    # def test_wrong_list(self):
        ''' if a data set is not readable, save an invalid record an notify the system of the problem '''
        # data = '{"list" : [{"main": {"temp": 30}}, {"broken": 0}]}'
        # resp = urllib2.addinfourl(StringIO(data), 'fill', '')
        # resp.code = 200
        # resp.msg = "Ok"
        # extern_information = resp      
        # api_answer_mock = MagicMock(return_value = extern_information)
        
        # with patch('urllib2.urlopen', api_answer_mock):
            # self.forecast.get_weather_forecast("some_url")
        
        # results = WeatherValue.objects.filter(temperature = -274) # not valid, beneath the absolute zero point 
         

    def test_set_up_records_out_of_json(self):
        naive_timestamp = datetime.datetime.fromtimestamp(0)
        expected_timestamp = naive_timestamp.replace(tzinfo=utc)
        expected_records = [WeatherValue(temperature = 30, 
            timestamp=expected_timestamp)]   #'{"list" : [{"main": {"temp": 30}}]}'
        time_mock = MagicMock(return_value = 0)
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                values = json.loads(self.data)
                records = self.forecast.set_up_records_out_of_json(values)
        self.assertListEqual(records, expected_records)
        
    
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
        self.data = '{"list" : [{"main": {"temp": 30}}]}'
        resp = urllib2.addinfourl(StringIO(self.data), '', '')
        resp.code = 200
        resp.msg = "Ok"
        extern_information = resp  
        self.api_answer_mock = MagicMock(return_value = extern_information)
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
        last_timestamp = aware_timestamp_from_seconds(0)
        WeatherValue(timestamp = last_timestamp, temperature=20, 
            target_time=last_timestamp).save()
        
        current_seconds = 1860 # 31*60: 31 minutes later
        time_mock = MagicMock(return_value = current_seconds) 

        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                self.forecast.update_weather_estimates()                            
        new_time = aware_timestamp_from_seconds(current_seconds)
        results = WeatherValue.objects.filter(temperature=30, 
            timestamp = new_time)
        self.assertTrue(results)
    
    def test_to_little_time_passed(self):
        '''the update function shouldn't save new forecasts 
        if less than 30 minutes passed since the last savings.
        '''
        last_timestamp = aware_timestamp_from_seconds(0)
        target_timestamp = aware_timestamp_from_seconds(15)
        WeatherValue(timestamp = last_timestamp, temperature=20, target_time=target_timestamp).save()
        current_timestamp = 900 # 15*60: 15 minutes later
        time_mock = MagicMock(return_value = current_timestamp) 
        
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                    self.forecast.update_weather_estimates()
        expected_timestamp = aware_timestamp_from_seconds(current_timestamp)
        results = WeatherValue.objects.filter(timestamp = expected_timestamp)
        self.assertFalse(results)
    
    def test_no_values_saved(self):
        '''the update function should save new forecasts 
        if there aren't savings in the database.
        '''
        current_timestamp = 0
        time_mock = MagicMock(return_value = current_timestamp) 
        
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                    self.forecast.update_weather_estimates()
        expected_timestamp = aware_timestamp_from_seconds(current_timestamp)
        results = WeatherValue.objects.filter(timestamp = expected_timestamp)
        self.assertTrue(results)        
    
    def test_only_invalid_values_saved(self):
        ''' the update function should save new forecasts 
        if there are only invalid records in the database.
        '''
        last_timestamp = aware_timestamp_from_seconds(0)
        target_timestamp = aware_timestamp_from_seconds(15)
        invalid_temperature = -274
        WeatherValue(timestamp = last_timestamp, temperature= -274, 
            target_time=target_timestamp).save()
        
        current_seconds = 30
        time_mock = MagicMock(return_value = current_seconds) 
        
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                    self.forecast.update_weather_estimates()
        
        expected_timestamp = aware_timestamp_from_seconds(current_seconds)            
        results = WeatherValue.objects.filter(timestamp = expected_timestamp)
        self.assertTrue(results)  
    
    def test_invalid_and_valid_values_saved(self):
        '''it shouldn't save new forecasts, if the latest valid entry is new enough
        '''
        last_timestamp = aware_timestamp_from_seconds(5)
        target_timestamp = aware_timestamp_from_seconds(15)
        invalid_temperature = -274
        WeatherValue(timestamp = last_timestamp, temperature= -274, 
            target_time=target_timestamp).save()
        passed_timestamp = aware_timestamp_from_seconds(0)
        WeatherValue(timestamp = passed_timestamp, temperature= 20, 
            target_time=target_timestamp).save()
        
        current_seconds = 30
        time_mock = MagicMock(return_value = current_seconds) 
        
        with patch('urllib2.urlopen', self.api_answer_mock):
            with patch('time.time', time_mock):
                    self.forecast.update_weather_estimates()
        
        expected_timestamp = aware_timestamp_from_seconds(current_seconds)            
        results = WeatherValue.objects.filter(timestamp = expected_timestamp)
        self.assertFalse(results)

    
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
        
def aware_timestamp_from_seconds(seconds):
    naive = datetime.datetime.fromtimestamp(seconds)
    return naive.replace(tzinfo=utc)
                
if __name__ == '__main__':
    unittest.main()
