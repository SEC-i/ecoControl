import unittest
from django.test import Client

from server.models import Device, Sensor, SensorEntry
from functions import crawl_and_save_data

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
        