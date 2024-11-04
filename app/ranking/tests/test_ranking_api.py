"""
Tests for Ranking API.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import resolve


from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    User,
    Ranking,
    PlayerTournamentResult,
    Team,
    Tournament,
)


def create_user(**params):
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)


class RankingAPITestCase(TestCase):
    def setUp(self):
        # Tworzenie przykładowych drużyn
        self.client = APIClient()
        self.maleuser1 = create_user(
            email="player1@example.com",
            password="testpassword",
            imie="Jan",
            nazwisko="Kowalski",
            gender="MALE",
            user_type="PL",
        )
        self.maleuser2 = create_user(
            email="player2@example.com",
            password="testpassword",
            imie="Marcin",
            nazwisko="Kowalski",
            gender="MALE",
            user_type="PL",
        )
        self.maleuser3 = create_user(
            email="player3@example.com",
            password="testpassword",
            imie="Aleksander",
            nazwisko="Kowalski",
            gender="MALE",
            user_type="PL",
        )
        self.maleuser4 = create_user(
            email="player4@example.com",
            password="testpassword",
            imie="Kamil",
            nazwisko="Kowalski",
            gender="MALE",
            user_type="PL",
        )

        self.team1 = Team.objects.create()
        self.team1.players.add(self.maleuser1)
        self.team1.players.add(self.maleuser2)
        self.team2 = Team.objects.create()
        self.team2.players.add(self.maleuser3)
        self.team2.players.add(self.maleuser4)

        self.organizator = create_user(
            email="organizator@example.com",
            password="testpassword",
            imie="Wojtek",
            nazwisko="Kowalski",
            gender="MALE",
            user_type="OR",
        )

        # Tworzenie przykładowych turniejów
        self.tournament = Tournament.objects.create(
            user=self.organizator,  # Organizator
            name="Tournament A",
            tour_type="SR",
            city="Warsaw",
            money_prize=1000,
            sex="MALE",
            ranking_type="NoneRank",
            date_of_beginning="2024-01-01",
            date_of_finishing="2024-01-02",
        )

        # Tworzenie przykładowych wyników turniejów
        PlayerTournamentResult.objects.create(
            player=self.team1.players.first(),
            tournament=self.tournament,
            team=self.team1,
            points_awarded=100,
            position=2,
            tournament_date="2024-01-02",
        )
        PlayerTournamentResult.objects.create(
            player=self.team2.players.first(),
            tournament=self.tournament,
            team=self.team2,
            points_awarded=150,
            position=1,
            tournament_date="2024-01-02",
        )

    def test_create_ranking(self):
        self.client.force_authenticate(self.organizator)
        url = reverse(
            "ranking:ranking-list"
        )  # Upewnij się, że ta nazwa jest poprawna
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Ranking.objects.first().rankings["1"]["full_name"],
            f"{self.maleuser3.imie} {self.maleuser3.nazwisko}",
        )
        self.assertEqual(
            Ranking.objects.count(), 2
        )  # Oczekujemy 2 rankingi (MALE i FEMALE)

    def test_get_last_ranking(self):
        self.client.force_authenticate(self.organizator)
        url = reverse("ranking:ranking-get-last-ranking") + "?gender=MALE"

        # Tworzenie rankingu przed testem
        Ranking.objects.create(
            date="2024-01-01",
            gender="MALE",
            rankings={
                1: {"user_id": self.team1.players.first().id, "points": 100}
            },
        )

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(
            "rankings", res.data
        )  # Oczekujemy, że dane rankingu będą w odpowiedzi

    def test_get_last_ranking_invalid_gender(self):
        url = "/api/ranking/last-ranking/" + "?gender=INVALID"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, {"error": "Invalid gender parameter"})

    def test_get_last_ranking_no_rankings(self):
        url = "/api/ranking/last-ranking/" + "?gender=MALE"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data, {"error": "No rankings found"})
