import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from server.models import DeviceConfiguration, Notification, Threshold


class TechnicianHooksTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test user for all tests
        User.objects.create_user(
            username="test_user2", password="demo123", first_name="test_fn", last_name="test_ln")

    def setUp(self):
        self.client = Client()

    def test_update_system_configurations(self):
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

    def test_forecast(self):
        response = self.client.get('/api/forecast/')
        self.assertEqual(response.status_code, 200)

    def test_notifications_hook(self):
        threshold = Threshold(sensor_id=1)
        threshold.save()

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 0)

        notification = Notification(threshold=threshold, category=Notification.Danger)
        notification.save()

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['threshold_id'], threshold.id)
        self.assertEqual(data[0]['category'], Notification.Danger)
