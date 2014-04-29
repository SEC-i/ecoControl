#import unittest
from server.forecasting.forecasting.weather import WeatherForecast
from django.test import TestCase
from server.models import Sensor, Device, SensorValue

''''class ForecastingTest(unittest.TestCase):
    def test_test(self):
        cast = WeatherForecast()
'''
class ForecastingDBTest(TestCase):
    def test_if_weather_sources_in_db(self):
        '''In the database should at least exist one weather source.'''
        try:
            sources = WeatherSource.objects.all()
        except NameError:
            self.fail('No weather source found.')
    def test_crawled_data_in_data(self):
        pass
        '''net = Device(name='File', device_type=Device.NET)
        net.save()
        sensor = Sensor(device=net, name='Weather Forecast',
                       key='testresource', unit='C', value_type=Sensor.FLOAT)
        sensor.save()
        forecast = WeatherForecast()
        forecast.get_weather_forecast()
        print forecast.get_weather_forecast()
        # start crawling of a static resource
        # ask fpor the crawled data
        #SensorValue.objects.filter()
        '''



if __name__ == '__main__':
    unittest.main()
