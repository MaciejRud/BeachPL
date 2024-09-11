'''Test for tournaments API.'''

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tournament

from tournament.serializers import TournamentSerializer


TOURNAMENTS_URL = reverse('tournament:tournament-list')

def create_user(**params):
    '''Create and return new user.'''
    return get_user_model().objects.create_user(**params)

def create_tournament(user, **params):
    '''Create and return a sample tournament'''
    defaults = {
        'name' : 'World Cup',
        'tour_type' : 'MA',
        'city' : 'Warszawa',
        'money_prize' : 15000,
        'sex' : "Female",
        'date_of_beginning' : "2024-09-10",
        'date_of_finishing' : '2024-09-12',
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

class PrivateTournamentAPITest(TestCase):
    '''Tests for authorized access to tournaments.'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='TestUser@example.com', password='123Test123')
        self.client.force_authenticate(self.user)

    def test_authorized_access_to_list_of_tournaments(self):
        """Test for return list of tournament for authorized user."""

        create_tournament(user=self.user)
        create_tournament(user=self.user)

        res = self.client.get(TOURNAMENTS_URL)

        tournaments = Tournament.objects.all().order_by('-id')
        serializer = TournamentSerializer(tournaments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
