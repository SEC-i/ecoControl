import unittest
from django.test import Client

from server.models import Device, Sensor, SensorEntry
from functions import crawl_and_save_data
from helpers import extract_data

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Add test device with test data_source
        self.device = Device.objects.create(name="test_name", data_source="http://graph.facebook.com/hassoplattnerinstitute")

        # Add test sensor
        self.sensor = Sensor.objects.create(device=self.device, name="test_name", key_name="id", unit="test_unit")

    def test_crawl_and_save_data(self):
        # Execute function
        crawl_and_save_data()

        # Get latest sensor entry
        sensors_entry = SensorEntry.objects.filter(sensor = self.sensor).latest('timestamp')

        # Check if value matches id of HPI's facebook page
        self.assertEqual(sensors_entry.value, "463909633639109")

    def test_extract_data(self):
        # Prepare test dictionary
        test_data = {
            'a': 1,
            'c': 9,
            'f': {
                's': 'foo',
                't': 'bar',
                'r': {
                    'foo': 'bar2'
                },
            },
            'z': 'foo1',
        }

        # Check various combinations
        self.assertEqual(extract_data(test_data,"a"), 1)
        self.assertEqual(extract_data(test_data,"f/s"), 'foo')
        self.assertEqual(extract_data(test_data,"f/{2}"), 'bar')
        self.assertEqual(extract_data(test_data,"f/r/foo"), 'bar2')
        self.assertEqual(extract_data(test_data,"z"), 'foo1')

        # Check that extract_data return '' if key not found or any other error
        self.assertEqual(extract_data(test_data,"r/s/t"), '')
        self.assertEqual(extract_data(test_data,"//"), '')