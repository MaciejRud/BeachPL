"""
Views for ranking API.
"""

from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from core.models import (
    Ranking,
    User,
    PlayerTournamentResult,
)
from .serializers import RankingSerializer

from django.views.generic import TemplateView


class RankingViewSet(viewsets.ModelViewSet):
    """View for manage ranking APIs."""

    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve all historical rankings."""
        queryset = Ranking.objects.all()

        # Filtrowanie po dacie, jeśli podano
        date = self.request.query_params.get("date")
        gender = self.request.query_params.get("gender")

        if date:
            queryset = queryset.filter(date=date)

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def create(self, request, *args, **kwargs):
        current_date = timezone.now().date()
        one_year_ago = current_date - timedelta(days=365)

        # Zbieranie zawodników płci męskiej i będących zawodnikami
        male_players = User.objects.filter(gender="MALE", user_type="PL")

        male_rankings = {}

        for player in male_players:
            # Pobieranie wyników zawodnika w ciągu ostatniego roku
            results = PlayerTournamentResult.objects.filter(
                player=player, tournament_date__gte=one_year_ago
            ).order_by("-tournament_date")[
                :6
            ]  # Wybieramy 6 ostatnich turniejów

            # Sumowanie punktów
            total_points = sum(result.points_awarded for result in results)

            # Sprawdzanie miejsca w rankingu
            male_rankings[player.id] = total_points

        # Sortowanie zawodników na podstawie punktów
        sorted_male_rankings = sorted(
            male_rankings.items(), key=lambda x: x[1], reverse=True
        )

        # Tworzenie ostatecznego słownika rankingowego
        final_male_rankings = {
            position
            + 1: {
                "full_name": f"{User.objects.get(id=player_id).imie} {User.objects.get(id=player_id).nazwisko}",
                "points": points,
            }
            for position, (player_id, points) in enumerate(
                sorted_male_rankings
            )
        }

        female_players = User.objects.filter(gender="FEMALE", user_type="PL")

        female_rankings = {}

        for player in female_players:
            # Pobieranie wyników zawodnika w ciągu ostatniego roku
            results = PlayerTournamentResult.objects.filter(
                player=player, tournament_date__gte=one_year_ago
            ).order_by("-tournament_date")[
                :6
            ]  # Wybieramy 6 ostatnich turniejów

            # Sumowanie punktów
            total_points = sum(result.points_awarded for result in results)

            # Sprawdzanie miejsca w rankingu
            female_rankings[player.id] = total_points

        # Sortowanie zawodników na podstawie punktów
        sorted_female_rankings = sorted(
            female_rankings.items(), key=lambda x: x[1], reverse=True
        )

        # Tworzenie ostatecznego słownika rankingowego
        final_female_rankings = {
            position + 1: {"user_id": player_id, "points": points}
            for position, (player_id, points) in enumerate(
                sorted_female_rankings
            )
        }

        # Zapisanie rankingu do bazy danych
        Ranking.objects.update_or_create(
            date=current_date,
            gender="MALE",
            defaults={"rankings": final_male_rankings},
        )

        Ranking.objects.update_or_create(
            date=current_date,
            gender="FEMALE",
            defaults={"rankings": final_female_rankings},
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        url_path="last-ranking",
        permission_classes=[AllowAny],
    )
    def get_last_ranking(self, request):
        gender = request.query_params.get("gender")

        if gender not in ["MALE", "FEMALE"]:
            return Response(
                {"error": "Invalid gender parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Pobieranie ostatniego rekordu dla danej płci
        last_ranking = (
            Ranking.objects.filter(gender=gender).order_by("-date").first()
        )

        if not last_ranking:
            return Response(
                {"error": "No rankings found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serializacja ostatniego rankingu
        serializer = RankingSerializer(last_ranking)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RankingTemplateViewSet(TemplateView):
    template_name = "ranking/ranking.html"
