import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from models import DeviceConfiguration


class APITestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test user for all tests
        User.objects.create_user(
            username="test_user", password="demo123", first_name="test_fn", last_name="test_ln")

    def setUp(self):
        self.client = Client()

    def test_authentication_procedures(self):
        # Issue a POST request to login
        response = self.client.post(
            '/api/login/', {'username': 'test_user', 'password': 'demo123'})

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "active"}
        self.assertEqual(json.loads(response.content), {
                         "login": "successful", "user": "test_fn test_ln"})

        response = self.client.get('/api/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {
                         "login": "active", "user": "test_fn test_ln", "system": "init"})

        # Issue a request to logout
        response = self.client.get('/api/logout/')

        response = self.client.get('/api/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {
                         "login": "inactive", "system": "init"})

    def test_system_configurations(self):
        data = [
            {'device_id': '1', 'key': 'capacity',
                'value': '2500', 'value_type': '1'},
            {'device_id': '3', 'key': 'max_gas_input', 'value': '25', 'value_type': '2'}]
        response = self.client.post(
            '/api/configure/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "success"})

        self.assertEqual(len(DeviceConfiguration.objects.all()), 2)

    def test_forecast(self):
        response = self.client.get('/api/forecast/')
        self.assertEqual(response.status_code, 200)
