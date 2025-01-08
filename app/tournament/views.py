"""
Views for the tournament APIs.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from core.models import (
    Tournament,
    User,
    Team,
    PlayerTournamentResult,
)

from tournament import serializers

from django.views.generic import TemplateView


class TournamentViewSet(viewsets.ModelViewSet):
    """View for manage tournament APIs."""

    serializer_class = serializers.TournamentDetailSerializer
    queryset = Tournament.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tournaments for authenticated users."""
        user = self.request.user

        # If the user is an organizer, they only see their own tournaments
        if user.user_type == "OR":
            return self.queryset.filter(user=user).order_by("-id")

        # If the user is a player, they see tournaments in which their team participates
        elif user.user_type == "PL":
            # Check if the action is 'create_team'
            if self.action == "create_team":
                # Return all tournaments
                return self.queryset.all()
            else:
                # Return only tournaments in which their team participates
                return self.queryset.filter(teams__players=user).distinct()
            # Other users (e.g., referees, volunteers) may have additional rights in the future
        return Tournament.objects.none()

    def get_serializer_class(self):
        """Serializer for list of tournaments."""
        if self.action == "list":
            self.serializer_class = serializers.TournamentSerializer
        elif self.action == "create_team":
            return serializers.TeamCreationSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new tournament."""
        if self.request.user.user_type != "OR":
            raise PermissionDenied("Only organizers can create tournaments.")
        else:
            serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Allow only the organizer to delete the tournament."""
        tournament = self.get_object()

        # Check if the user is an organizer and the owner of this tournament
        if request.user.user_type != "OR" or tournament.user != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this tournament."
            )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Allow only the organizer to update the tournament."""
        tournament = self.get_object()

        # Check if the user is an organizer and the owner of this tournament
        if request.user.user_type != "OR" or tournament.user != request.user:
            raise PermissionDenied(
                "You do not have permission to update this tournament."
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Allow only the organizer to partially update the tournament."""
        tournament = self.get_object()

        # Check if the user is an organizer and the owner of this tournament
        if request.user.user_type != "OR" or tournament.user != request.user:
            raise PermissionDenied(
                "You do not have permission to update this tournament."
            )

        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def create_team(self, request, pk=None):
        """Add team to tournament."""
        tournament = self.get_object()
        serializer = serializers.TeamCreationSerializer(data=request.data)

        if serializer.is_valid():
            player_ids = serializer.validated_data["players"]

            # Check if the logged-in user is one of the players
            if request.user.id not in player_ids:
                return Response(
                    {"detail": "You must be part of the team."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            players = User.objects.filter(id__in=player_ids, user_type="PL")

            # Check if there are exactly two players and if they are 'players'
            if players.count() != 2:
                return Response(
                    {"detail": "All players must be players."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the gender of both players matches the gender of the tournament
            if players.filter(gender=tournament.sex).count() != 2:
                return Response(
                    {
                        "detail": "Both players must have the same gender as required by the tournament."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            team = Team.objects.create()
            team.players.set(player_ids)
            team.save()

            tournament.teams.add(team)

            team_serializer = serializers.TeamSerializer(team)

            return Response(
                {
                    "detail": "Team created successfully.",
                    "team": team_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="remove_team")
    def remove_team(self, request, pk=None):
        """Remove the team from the tournament if the user is an organizer or part of the team."""
        serializer = serializers.RemoveTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = self.get_object()
        team_id = serializer.validated_data.get("team_id")
        user = request.user

        if not team_id:
            return Response(
                {"detail": "Team ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            team = tournament.teams.get(id=team_id)
        except Team.DoesNotExist:
            return Response(
                {"detail": "Team not found in this tournament."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is an organizer
        if user.user_type == "OR":
            # The user is an organizer, they can remove any team
            tournament.teams.remove(team)

        # Check if the user is a player
        elif user.user_type == "PL":
            # Check if the user is a member of the team
            if not team.players.filter(id=user.id).exists():
                raise PermissionDenied(
                    "You are not a member of this team and cannot remove it."
                )

            tournament.teams.remove(team)
        else:
            return Response(
                {"detail": "You do not have permission to remove this team."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {"detail": "Team removed successfully from the tournament."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="award-points")
    def award_points(self, request, pk=None):
        """Award points to teams based on their positions in the tournament."""

        # Check if the user is an organizer
        if request.user.user_type != "OR":
            return Response(
                {"detail": "You do not have permission to award points."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tournament = self.get_object()
        # Expected input data format
        serializer = serializers.AwardPointsSerializer(data=request.data)
        if serializer.is_valid():
            # Process the data
            team_results = serializer.validated_data["team_results"]

            for result in team_results:
                team_id = result["team_id"]
                position = result["position"]
                # Logic for awarding points
                team = Team.objects.get(id=team_id)

                # Example logic for awarding points
                points_awarded = self.calculate_points(
                    position
                )  # Define this method according to your point system
                for i in team.players.all():
                    PlayerTournamentResult.objects.create(
                        player=i,
                        team=team,
                        tournament=tournament,
                        points_awarded=points_awarded,
                        position=position,
                        tournament_date=tournament.date_of_finishing,
                    )

            return Response(
                {"detail": "Points awarded successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def calculate_points(self, position):
        """Define your point system based on position."""
        # Example point logic
        if position == 1:
            return 100  # Points for first place
        elif position == 2:
            return 60  # Points for second place
        elif position == 3:
            return 30  # Points for third place
        return 0  # No points for other places


class PublicViewOfTournamentsViewSet(viewsets.ReadOnlyModelViewSet):
    """View for listing tournaments publicly."""

    serializer_class = serializers.TournamentSerializer
    queryset = Tournament.objects.all()
    permission_classes = [AllowAny]  # Allow access to everyone

    def get_queryset(self):
        """Retrieve tournaments publicly."""
        return self.queryset.order_by("date_of_beginning")


class TournamentListView(TemplateView):
    template_name = "tournament/tournament_list.html"


class DetailedTournamentView(TemplateView):
    template_name = "tournament/tournament_details.html"


class CreateTournamentTemplate(TemplateView):
    template_name = "tournament/create-tournament.html"


class CreateAndAddTeamTemplate(TemplateView):
    template_name = "tournament/add-team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_id = self.kwargs["id"]  # Get ID from URL
        context["tournament"] = Tournament.objects.get(
            id=tournament_id
        )  # Get tournament object
        return context
