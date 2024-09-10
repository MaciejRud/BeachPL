'''
Tests for the user API.
'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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

    def test_creating_token_for_user(self):
        '''Test for creating a token for user.'''
        user_details = {
            'imie' : "Test123",
            'email' : 'test@example.com',
            'password' : 'Test-password-123',
        }
        create_user(**user_details)

        payload = {
            'email' : user_details['email'],
            'password' : user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        '''Test returns error if bad credentials.'''
        create_user(email = 'test123@example.com', password = 'goodpass')

        payload = {
            'email' : 'test123@example.com',
            'password' : 'badpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_blank_password(self):
        """Test returns error if blank password."""

        payload = {'email' : 'test@example.com', 'password' : ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_denied_with_no_authentication(self):
        '''Test for unauthorized access to acount.'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API User that require authentication."""

    def setUp(self):
        self.user = create_user(
            imie='Test Name',
            email='testuser@example.com',
            password='TestPass',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_succes(self):
        '''Test for authorized access to acount.'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'imie':self.user.imie,
            'email':self.user.email,
        })

    def test_creating_account_after_login(self):
        '''Test for access to post function on me url point.'''\

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_user_data(self):
        '''Test for updating user data.'''

        payload = {
            'password' : "newpassword123",
            'imie' : "New Name",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.imie, payload['imie'])
        self.assertTrue(self.user.check_password(payload['password']))

