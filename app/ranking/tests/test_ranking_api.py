"""
Tests for Ranking API.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import (
    User,
    Ranking,
    PlayerTournamentResult,
)

class RankingViewSetTests(APITestCase):
    def setUp(self):
        # Tworzenie użytkowników testowych
        self.male_user1 = User.objects.create_user(username='male_user1', password='password123', gender=User.Gender.MALE)
        self.male_user2 = User.objects.create_user(username='male_user2', password='password123', gender=User.Gender.MALE)
        self.female_user1 = User.objects.create_user(username='female_user1', password='password123', gender=User.Gender.FEMALE)

        # Dodanie wyników turniejów dla mężczyzn
        for i in range(3):
            PlayerTournamentResult.objects.create(user=self.male_user1, tournament_id=i, points_awarded=100-i)

        for i in range(2):
            PlayerTournamentResult.objects.create(user=self.male_user2, tournament_id=i, points_awarded=50-i)

        # Dodanie wyników turniejów dla kobiet
        for i in range(3):
            PlayerTournamentResult.objects.create(user=self.female_user1, tournament_id=i, points_awarded=80-i)

    def test_generate_ranking(self):
        url = reverse('ranking-list')  # Upewnij się, że to jest poprawny URL dla Twojego RankingViewSet

        response = self.client.post(url)

        # Sprawdzenie odpowiedzi
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ranking.objects.count(), 2)  # Sprawdzamy, czy utworzono 2 rankingi (mężczyźni, kobiety)

        # Sprawdzanie, czy rankingi mają odpowiednie dane
        male_ranking = Ranking.objects.filter(gender=User.Gender.MALE).first()
        female_ranking = Ranking.objects.filter(gender=User.Gender.FEMALE).first()

        self.assertIsNotNone(male_ranking)
        self.assertIsNotNone(female_ranking)

        self.assertGreater(male_ranking.rankings[0][1], male_ranking.rankings[1][1])  # Sprawdzamy, czy pierwszy gracz ma więcej punktów niż drugi
        self.assertGreater(female_ranking.rankings[0][1], female_ranking.rankings[1][1])  # To samo dla kobiet

    def test_generate_ranking_no_results(self):
        # Usuwamy wyniki turniejów, aby przetestować scenariusz bez wyników
        PlayerTournamentResult.objects.all().delete()

        url = reverse('ranking-list')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ranking.objects.count(), 2)  # Nadal powinno być 2 rankingi, ale bez danych

        male_ranking = Ranking.objects.filter(gender=User.Gender.MALE).first()
        female_ranking = Ranking.objects.filter(gender=User.Gender.FEMALE).first()

        self.assertIsNotNone(male_ranking)
        self.assertIsNotNone(female_ranking)

        self.assertEqual(male_ranking.rankings, [])  # Sprawdzamy, czy ranking mężczyzn jest pusty
        self.assertEqual(female_ranking.rankings, [])  # Sprawdzamy, czy ranking kobiet jest pusty
