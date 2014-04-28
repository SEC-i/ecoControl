#import unittest
from server.forecasting.forecasting.weather import WeatherForecast
from django.test import TestCase
#from server.models import Device, Sensor, SensorEntry

''''class ForecastingTest(unittest.TestCase):
	def test_test(self):
		cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
	def test_crawled_data_in_data(self):
		pass



if __name__ == '__main__':
    unittest.main()
