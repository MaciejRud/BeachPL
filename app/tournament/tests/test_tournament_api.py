'''Test for tournaments API.'''

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tournament

from tournament.serializers import TournamentDetailSerializer

import datetime


TOURNAMENTS_URL = reverse('tournament:tournament-list')
PUBLIC_TOURNAMENTS_URL = reverse('tournament:public-tournament-list')


def detail_url(tournament_id):
    '''Return URL for tournament detail.'''
    return reverse('tournament:tournament-detail', args=[tournament_id])


def create_user(**params):
    '''Create and return new user.'''
    return get_user_model().objects.create_user(**params)


def create_tournament(user, **params):
    '''Create and return a sample tournament'''
    defaults = {
        'name': 'World Cup',
        'tour_type': 'MA',
        'city': 'Warszawa',
        'money_prize': 15000,
        'sex': "Female",
        'date_of_beginning': "2024-09-10",
        'date_of_finishing': '2024-09-12',
    }
    defaults.update(params)

    tournament = Tournament.objects.create(user=user, **defaults)
    return tournament


class PublicTournamentAPITests(TestCase):
    '''Tests for unauthorized access to tournaments.'''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''Test auth is required to call API.'''

        res = self.client.get(TOURNAMENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retriving_public_list_of_tournaments(self):
        '''Test for available for any user getiing list of tournaments.'''

        user1 = create_user(
            email = "hubert@example.com",
            password = "Test123",
        )

        user2 = create_user(
            email = "aleks@example.com",
            password = "Test123",
        )

        payload = {
            'name': 'Mistrzostwa Polski',
            'tour_type': 'MA',
            'city': 'Iława',
            'money_prize': 5000,
            'sex': "Female",
            'date_of_beginning': "2024-11-28",
            'date_of_finishing': '2024-11-29',
        }

        create_tournament(user=user1)
        create_tournament(user=user2, **payload)

        res = self.client.get(PUBLIC_TOURNAMENTS_URL)

        tournaments = Tournament.objects.all().order_by('date_of_beginning')
        serializer = TournamentDetailSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)





class PrivateTournamentAPITest(TestCase):
    '''Tests for authorized access to tournaments.'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='TestUser@example.com',
                                password='123Test123')
        self.client.force_authenticate(self.user)

    def test_authorized_access_to_list_of_tournaments(self):
        """Test for return list of tournament for authorized user."""

        create_tournament(user=self.user)
        create_tournament(user=self.user)

        res = self.client.get(TOURNAMENTS_URL)

        tournaments = Tournament.objects.all().order_by('-id')
        serializer = TournamentDetailSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_details_of_tournament(self):
        '''Test for return details of tournamnet.'''

        tournament = create_tournament(user=self.user)

        url = detail_url(tournament.id)
        res = self.client.get(url)

        serializer = TournamentDetailSerializer(tournament)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_creating_tournament(self):
        '''Test for creating tournamtent.'''

        payload = {
            'name': 'World Cup',
            'tour_type': 'MA',
            'city': 'Warszawa',
            'money_prize': 15000,
            'sex': "FEMALE",
            'date_of_beginning': datetime.date(2024, 9, 10),
            'date_of_finishing': datetime.date(2024, 9, 12),
        }

        res = self.client.post(TOURNAMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tournament = Tournament.objects.get(id=res.data['id'])
        for i, v in payload.items():
            self.assertEqual(getattr(tournament, i), v)
        self.assertEqual(tournament.user, self.user)

    def test_partially_updating_tournament(self):
        '''Test for partially updating tournament.'''

        tournament = create_tournament(user=self.user)

        payload = {
            'city': "Krakow",
            'sex': "MALE",
        }
        url = detail_url(tournament.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tournament.refresh_from_db()
        self.assertEqual(tournament.city, payload['city'])
        self.assertEqual(tournament.user, self.user)

    def test_updating_tournament_without_permission(self):
        '''Test for unauthorized try to update permission.'''

        user2 = create_user(email='anotheruser@example.com',
                            password='Test123123')
        tournament = create_tournament(user=user2, city='Krakow')

        payload = {
            'city': "Krakow",
            'sex': "MALE",
        }
        url = detail_url(tournament.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        tournament.refresh_from_db()
        self.assertEqual(tournament.city, "Krakow")

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com',
                               password='test123')
        tournament = create_tournament(user=new_user)

        url = detail_url(tournament.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tournament.objects.filter(id=tournament.id).exists())

    def test_destroying_tournament(self):
        """Test for canceling the tournament."""

        tournament = create_tournament(user=self.user)
        url = detail_url(tournament.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tournament.objects.filter(id=tournament.id).exists())
