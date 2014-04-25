import json

from django.test import TestCase, Client
from django.contrib.auth.models import User


class APITestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test user for all tests
        User.objects.create_user(
            username="test_user", password="demo123", first_name="test_fn", last_name="test_ln")

    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.post(
            '/', {'username': 'john', 'password': 'smith'})

    def test_authentication_procedures(self):
        # Issue a POST request to login
        response = self.client.post(
            '/login/', {'username': 'test_user', 'password': 'demo123'})

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "active"}
        self.assertEqual(json.loads(response.content), {
                         "login": "successful", "user": "test_fn test_ln"})

        response = self.client.get('/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {
                         "login": "active", "user": "test_fn test_ln"})

        # Issue a request to logout
        response = self.client.get('/logout/')

        response = self.client.get('/status/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the response equals {"login": "inactive"}
        self.assertEqual(json.loads(response.content), {"login": "inactive"})
