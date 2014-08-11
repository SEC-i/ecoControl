import json
import re

from django.test import TestCase, Client
from django.contrib.auth.models import User

from server.models import DeviceConfiguration, Notification, Threshold
from server.urls import urlpatterns


class APITestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test user for all tests
        User.objects.create_user(
            username="test_user", password="demo123", first_name="test_fn", last_name="test_ln")

        User.objects.create_superuser(
            'test_admin', 'admin@localhost', 'demo321')

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
        self.assertDictContainsSubset(
            {"login": True, "user": "test_fn test_ln", "system_status": "init"}, json.loads(response.content))

        # Issue a request to logout
        response = self.client.get('/api/logout/')

        response = self.client.get('/api/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertDictContainsSubset(
            {"login": False, "system_status": "init"}, json.loads(response.content))

    def test_all_hooks_simple(self):
        for pattern in urlpatterns:
            url = re.sub(
                '\((.)*', '', pattern.regex.pattern).replace('^', '/').replace('$', '')
            response = self.client.get(url)
            self.assertTrue(response.status_code in [200, 301, 403, 405])
            response = self.client.post(url)
            self.assertTrue(response.status_code in [200, 301, 403, 405])
            response = self.client.post(url, data=json.dumps({}), content_type="application/json")
            self.assertTrue(response.status_code in [200, 301, 403, 405])

    def test_all_hooks_simple_authenticated(self):
        for pattern in urlpatterns:
            url = re.sub(
                '\((.)*', '', pattern.regex.pattern).replace('^', '/').replace('$', '')

            # Log in as admin. For some reason, this is only valid once.
            self.client.login(username='test_admin', password='demo321')

            response = self.client.get(url)
            self.assertTrue(response.status_code in [200, 301, 403, 405])
            response = self.client.post(url)
            self.assertTrue(response.status_code in [200, 301, 403, 405])
            response = self.client.post(url, data=json.dumps({}), content_type="application/json")
            self.assertTrue(response.status_code in [200, 301, 403, 405])
