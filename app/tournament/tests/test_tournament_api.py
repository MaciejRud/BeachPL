'''Test for tournaments API.'''

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tournament,
    Team,
    PlayerTournamentResult,
)

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

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retriving_public_list_of_tournaments(self):
        '''Test for available for any user getiing list of tournaments.'''

        user1 = create_user(
            email="hubert@example.com",
            password="Test123",
        )

        user2 = create_user(
            email="aleks@example.com",
            password="Test123",
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
                                password='123Test123',
                                user_type='OR',)
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

    def test_creating_tournament_by_organizer(self):
        '''Test for creating tournament by organizer.'''

        payload = {
            'name': 'World Cup',
            'tour_type': 'MA',
            'city': 'Warszawa',
            'money_prize': 15000,
            'sex': "FEMALE",
            'date_of_beginning': datetime.date(2024, 9, 10),
            'date_of_finishing': datetime.date(2024, 9, 12),
        }

        # Create an organizer user
        organizer = create_user(
            email='organizer@example.com',
            password='TestPass123',
            imie="Organizer",
            user_type='OR'
        )
        self.client.force_authenticate(organizer)

        res = self.client.post(TOURNAMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tournament = Tournament.objects.get(id=res.data['id'])
        for i, v in payload.items():
            self.assertEqual(getattr(tournament, i), v)
        self.assertEqual(tournament.user, organizer)


    def test_creating_tournament_by_non_organizer(self):
        '''Test that non-organizers cannot create tournaments.'''

        payload = {
            'name': 'World Cup',
            'tour_type': 'MA',
            'city': 'Warszawa',
            'money_prize': 15000,
            'sex': "FEMALE",
            'date_of_beginning': datetime.date(2024, 9, 10),
            'date_of_finishing': datetime.date(2024, 9, 12),
        }

        # Create a non-organizer user
        non_organizer = create_user(
            email='nonorganizer@example.com',
            password='TestPass123',
            imie="Non-Organizer",
            user_type='PL'
        )
        self.client.force_authenticate(non_organizer)

        res = self.client.post(TOURNAMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Tournament.objects.count(), 0)

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

    def test_delete_other_users_tournament_error(self):
        """Test trying to delete another users tournament gives error."""
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

class TournamentTeamTestCase(TestCase):
    '''Tests for managing teams in tournament.'''
    def setUp(self):
        self.client = APIClient()
        self.organizer = create_user(email='organizer@example.com', password='TestPass123',
                                     user_type='OR',)
        self.player1 = create_user(email='player1@example.com', password='TestPass123',
                                   user_type='PL', gender='MALE',)
        self.player2 = create_user(email='player2@example.com', password='TestPass123',
                                   user_type='PL', gender='MALE',)
        self.client.force_authenticate(self.organizer)
        self.tournament = create_tournament(user=self.organizer, sex="MALE")
        self.url = detail_url(self.tournament.id)

    def test_create_team(self):
        '''Test for create a team by player.'''
        payload = {
            'players': [self.player1.id, self.player2.id]
        }

        self.client.force_authenticate(self.player1)
        res = self.client.post(f'{self.url}create_team/', payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.tournament.teams.filter(players__in=[self.player1, self.player2]).exists())


class RemoveTeamFromTournamentTests(TestCase):
    '''Tests for removing a team from a tournament.'''

    def setUp(self):
        '''Setup for the test cases.'''
        self.client = APIClient()

        self.organizer = create_user(
            email='organizer@example.com',
            password='testpass123',
            user_type='OR',
        )

        self.tournament = create_tournament(self.organizer)
        self.url = detail_url(self.tournament.id)

        # Tworzymy dwóch graczy
        self.player1 = create_user(
            email='player1@example.com',
            password='testpass123',
            user_type='PL',
        )
        self.player2 = create_user(
            email='player2@example.com',
            password='testpass123',
            user_type='PL',
        )

        # Tworzymy drużynę
        self.team = Team.objects.create()
        self.team.players.set([self.player1, self.player2])

        # Przypisujemy drużynę do turnieju
        self.tournament.teams.add(self.team)

        # Ustawiamy URL
        self.url = reverse('tournament:tournament-remove-team', kwargs={'pk': self.tournament.id})

    def test_remove_team_success(self):
        '''Test that a user can remove a team they are part of.'''
        self.client.force_authenticate(user=self.player1)

        payload = {'team_id': self.team.id}
        res = self.client.delete(self.url, data=payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.team, self.tournament.teams.all())

    def test_remove_team_not_member(self):
        '''Test that a user who is not part of a team cannot remove it.'''
        other_user = create_user(
            email='otheruser@example.com',
            password='testpass123',
            user_type='PL',
        )
        self.client.force_authenticate(user=other_user)

        payload = {'team_id': self.team.id}
        res = self.client.delete(self.url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_team_does_not_exist(self):
        '''Test that trying to remove a non-existent team returns 404.'''
        self.client.force_authenticate(user=self.player1)

        payload = {'team_id': 999}  # Nieistniejąca drużyna
        res = self.client.delete(self.url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_team_not_deletes_if_part_of_other_tournaments(self):
        '''Test that a team is not deleted if it is part of another tournament.'''
        other_tournament = create_tournament(
            user=self.organizer,
            name='Second Tournament',
            city='Krakow',
            money_prize=1500,
            sex='MALE',
            tour_type='SR',
            ranking_type='OneStar',
            date_of_beginning='2024-10-01',
            date_of_finishing='2024-10-02',
        )
        other_tournament.teams.add(self.team)

        self.client.force_authenticate(user=self.player1)

        payload = {'team_id': self.team.id}
        res = self.client.delete(self.url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.team, other_tournament.teams.all())  # Drużyna pozostaje w innym turnieju

class TournamentPointsTests(TestCase):
    def setUp(self):
        # Tworzenie użytkownika organizatora, turnieju i drużyn
        self.client = APIClient()
        self.organizer = create_user(email='organizer@example.com', password='password', user_type='OR')
        self.tournament = create_tournament(name='Test Tournament', user=self.organizer)
        self.player1 = create_user(email="player1@example.com", password='123TestPass', user_type="PL")
        self.player2 = create_user(email="player2@example.com", password='123TestPass', user_type="PL")
        self.team = Team.objects.create()
        self.team.players.set([self.player1, self.player2])
        self.tournament.teams.add(self.team)
        self.url = reverse('tournament:tournament-award-points', kwargs={'pk': self.tournament.id})

    def test_award_points_success(self):
        self.client.force_authenticate(self.organizer)

        payload = {
            "team_results": [
                {"team_id": self.team.id, "position": 1}
            ]
        }

        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(PlayerTournamentResult.objects.count(), 2)
        player1_result = PlayerTournamentResult.objects.filter(player=self.player1).first()
        self.assertEqual(player1_result.points_awarded, 100)

    def test_award_points_permission_denied(self):
        '''Test for awarding points denied if the player wants to do it.'''
        self.client.force_authenticate(self.player1)

        payload = {
            "team_results": [
                {"team_id": self.team.id, "position": 1}
            ]
        }

        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
