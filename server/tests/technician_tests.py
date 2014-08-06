import json
import csv
from io import BytesIO
from os.path import join
from datetime import datetime

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.db import connection

from server.models import DeviceConfiguration, Notification, Threshold, SensorValue
from server.settings import BASE_DIR
from server.worker.functions import refresh_views


class TechnicianHooksTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test user for all tests
        User.objects.create_superuser(
            'test_tech', 'admin@localhost', 'testing')

    def load_sensor_values(self):
        directory = join(
            BASE_DIR, "server", "tests", "data")

        sensor_values = []
        with open(join(directory, 'test_sensor_values.csv'), "rb") as file_obj:
            reader = csv.reader(file_obj, delimiter=",")
            header = reader.next()

            s_index = header.index('sensor_id')
            v_index = header.index('value')
            t_index = header.index('timestamp')
            for row in reader:
                sensor = row[s_index]
                value = row[v_index]
                timestamp = datetime.strptime(row[t_index], "%Y-%m-%d %H:%M:%S+%f").replace(tzinfo=utc)
                sensor_values.append(SensorValue(sensor_id=sensor, value=value, timestamp=timestamp))

        SensorValue.objects.bulk_create(sensor_values)

        refresh_views()

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_tech', password='testing')

    def test_statistics(self):
        self.load_sensor_values()
        response = self.client.get('/api/statistics/')
        self.assertEqual(response.status_code, 200)

    def test_update_device_configurations(self):
        self.assertEqual(len(DeviceConfiguration.objects.all()), 15)

        data = [
            {'device': '1', 'key': 'capacity',
                'value': '12344', 'type': '1', 'unit': 'l'},
            {'device': '3', 'key': 'max_gas_input', 'value': '223445', 'type': '2', 'unit': 'kWh'}]
        response = self.client.post(
            '/api/configure/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "success"})

        self.assertEqual(len(DeviceConfiguration.objects.all()), 15)

    def test_notifications_hook(self):
        threshold = Threshold(sensor_id=1)
        threshold.save()

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['total'], 0)
        self.assertEqual(len(data['notifications']), 0)

        notification = Notification(
            threshold=threshold, category=Notification.Danger, show_manager=True)
        notification.save()

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['total'], 1)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(
            data['notifications'][0]['threshold_id'], threshold.id)
        self.assertEqual(
            data['notifications'][0]['category'], Notification.Danger)
