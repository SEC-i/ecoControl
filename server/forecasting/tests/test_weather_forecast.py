#import unittest
from server.forecasting.forecasting.weather import WeatherForecast
from django.test import TestCase
from server.models import Sensor, Device

''''class ForecastingTest(unittest.TestCase):
	def test_test(self):
		cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
	def test_if_weather_sources_in_db(self):
		source = Device.objects.get(name='Internet')
		sensors = Sensor.objects.filter(device=source)
		assertGreater(len(sensor), 0)
		
	def test_crawled_data_in_data(self):
		pass



if __name__ == '__main__':
    unittest.main()
