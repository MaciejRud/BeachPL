'''
Tests for the user API.
'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import User

from user.serializers import (
    UserListSerializer,
    UserSerializers,
)


CREATE_USER_URL = reverse('user:create')
ME_URL = reverse('user:me')
LIST_OF_USERS_URL = reverse('user:player-list')


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
            'nazwisko': "Nazwa",
            'gender':'MALE',
            'pesel': '12345612345',
            'user_type': 'PL'
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
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test for creating an user with password shorter than 5 char."""
        payload = {
            'email': 'test@example.com',
            'password': '1234',
            'imie': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    def test_access_denied_with_no_authentication(self):
        '''Test for unauthorized access to acount.'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_denied_for_list_of_players_without_authentication(self):
        '''Test for unathorized access to list of players.'''

        res = self.client.get(LIST_OF_USERS_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateUserAPITests(TestCase):
    """Test API User that require authentication."""

    def setUp(self):
        self.user = create_user(
            imie='Test Name',
            email='testuser@example.com',
            password='TestPass',
            gender='MALE'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_succes(self):
        '''Test for authorized access to acount.'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'testuser@example.com',
            'imie': 'Test Name',
            'nazwisko': '',
            'gender':'MALE',
            'pesel': None,
            'user_type': ''
            })

    def test_creating_account_after_login(self):
        '''Test for access to post function on me url point.'''\

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_user_data(self):
        '''Test for updating user data.'''

        payload = {
            'password': "newpassword123",
            'imie': "New Name",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.imie, payload['imie'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_retrieving_list_of_players(self):
        '''Test for retrieving list of players.'''

        create_user(
            imie='Hubert',
            nazwisko = 'Testowy1',
            email='testuser1@example.com',
            password='TestPass',
            user_type = 'PL',
        )

        create_user(
            imie='Andrzej',
            nazwisko = 'Testowy2',
            email='testuser2@example.com',
            password='TestPass',
            user_type = 'PL',
        )

        create_user(
            imie='Wojtek',
            nazwisko = 'Testowy3',
            email='testuser3@example.com',
            password='TestPass',
            user_type = 'PL',
        )

        res = self.client.get(LIST_OF_USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        list_of_tournaments = User.objects.filter(user_type='PL').order_by('nazwisko')
        serializer = UserListSerializer(list_of_tournaments, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_list_of_players_only_same_gender(self):
        '''Test for retrieving list of players only same gender.'''

        create_user(
            imie='Hubert',
            nazwisko = 'Testowy1',
            email='testuser1@example.com',
            password='TestPass',
            user_type = 'PL',
            gender = 'MALE',
        )

        create_user(
            imie='Andrzej',
            nazwisko = 'Testowy2',
            email='testuser2@example.com',
            password='TestPass',
            user_type = 'PL',
            gender = 'MALE',
        )

        create_user(
            imie='Wojtek',
            nazwisko = 'Testowy3',
            email='testuser3@example.com',
            password='TestPass',
            user_type = 'PL',
            gender = 'MALE',
        )

        create_user(
            imie='Alina',
            nazwisko = 'Testowa4',
            email='testuser4@example.com',
            password='TestPass',
            user_type = 'PL',
            gender = 'FEMALE',
        )

        res = self.client.get(LIST_OF_USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        list_of_users = User.objects.filter(user_type='PL', gender="MALE").order_by('nazwisko')
        serializer = UserListSerializer(list_of_users, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_list_of_players(self):
        '''Test for retrieving list of only players.'''

        create_user(
            imie='Hubert',
            nazwisko = 'Testowy1',
            email='testuser1@example.com',
            password='TestPass',
            user_type = 'PL',
            gender="MALE",
        )

        create_user(
            imie='Andrzejt',
            nazwisko = 'Testowy2',
            email='testuser2@example.com',
            password='TestPass',
            user_type = 'PL',
            gender="MALE"
        )

        user_organizer = create_user(
            imie='Wojtek',
            nazwisko = 'Testowy3',
            email='testuser3@example.com',
            password='TestPass',
            user_type = 'OR',
        )

        res = self.client.get(LIST_OF_USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        for user in res.data:
            self.assertNotIn(user_organizer.imie, user['imie'])
