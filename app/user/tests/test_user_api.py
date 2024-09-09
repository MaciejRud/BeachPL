'''
Tests for the user API.
'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    '''Create and return a new user.'''
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    '''Test the public feature of the user API.'''

    def setUp(self):
        self.client = APIClient()

    def test_create_user_succes(self):
        '''Test creating new user is successful.'''
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'imie': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        '''Test for creating an user with existing email.'''
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'imie': 'Test Name',
        }
        user = create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test for creating an user with password shorter than 5 char."""
        payload = {
            'email' : 'test@example.com',
            'password' : '1234',
            'imie' : 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email = payload['email']).exists()
        self.assertFalse(user_exists)
