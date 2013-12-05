import unittest
import json
from django.test import Client
from django.contrib.auth.models import User

from server.models import Device

class SimpleTest(unittest.TestCase):
    @classmethod  
    def setUpClass(cls): 
        # Create test user for all tests
        User.objects.create_user(username = "test_user", password = "demo123", first_name="test_fn", last_name="test_ln")

        # Add test device
        Device.objects.create(name="test_name", data_source="test_data_source", interval=60)

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_login_inactive(self):
        # Issue a GET request.
        response = self.client.get('/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {"login": "inactive"})

    def test_login_procedure(self):
        # Issue a GET request.
        response = self.client.post('/login/', {'username': 'test_user', 'password': 'demo123'})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "active"}
        self.assertEqual(json.loads(response.content), {"login": "successful", "user": "test_fn test_ln"})

        # Issue a GET request.
        response = self.client.get('/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {"login": "active", "user": "test_fn test_ln"})

    def test_permission_denied(self):
        # test multipe urls for {"permission": "denied"}
        for url in ['devices/', 'device/1/', 'device/1/sensors/', 'device/1/entries/', 'sensor/1/', 'sensor/1/entries/', 'entry/1/', 'device/1/']:
            response = self.client.get('/' + url)
            self.assertEqual(json.loads(response.content), {"permission": "denied"})

    def test_add_device(self):
        # Log in client
        self.client.login(username='test_user', password='demo123')

        # Issue GET request for device details
        d = Device.objects.get(name="test_name")
        response = self.client.get('/device/' + str(d.id) + '/')

        # Check that the response contains the test device
        self.assertEqual(json.loads(response.content), [{"data_source": "test_data_source", "id": 1, "name": "test_name", "interval": 60}])
        