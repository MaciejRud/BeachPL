"""
Views for the tournament APIs.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from core.models import (
    Tournament,
    User,
    Team,
)

from tournament import serializers

from django.views.generic import TemplateView


class TournamentViewSet(viewsets.ModelViewSet):
    '''View for manage tournament APIs.'''

    serializer_class = serializers.TournamentDetailSerializer
    queryset = Tournament.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Retrieve tournaments for authenticated users.'''
        user = self.request.user

        # Jeśli użytkownik jest organizatorem, widzi tylko swoje turnieje
        if user.user_type == 'OR':
            return self.queryset.filter(user=user).order_by('-id')

        # Jeśli użytkownik jest graczem, widzi turnieje, w których bierze udział jego drużyna
        elif user.user_type == 'PL':
            return self.queryset.filter(teams__players=user).distinct()

        # Inni użytkownicy (np. sędziowie, wolontariusze) mogą mieć dodatkowe prawa w przyszłości
        return Tournament.objects.none()

    def get_serializer_class(self):
        '''Serializer for list of tournaments.'''
        if self.action == 'list':
            self.serializer_class = serializers.TournamentSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        '''Create a new tournament.'''
        if self.request.user.user_type != 'OR':
            raise PermissionDenied("Only organizers can create tournaments.")
        else:
            serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        '''Allow only the organizer to delete the tournament.'''
        tournament = self.get_object()

        # Sprawdzamy, czy użytkownik jest organizatorem i właścicielem tego turnieju
        if request.user.user_type != 'OR' or tournament.user != request.user:
            raise PermissionDenied("You do not have permission to delete this tournament.")

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        '''Allow only the organizer to update the tournament.'''
        tournament = self.get_object()

        # Sprawdź, czy użytkownik jest organizatorem i właścicielem tego turnieju
        if request.user.user_type != 'OR' or tournament.user != request.user:
            raise PermissionDenied("You do not have permission to update this tournament.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        '''Allow only the organizer to partially update the tournament.'''
        tournament = self.get_object()

        # Sprawdź, czy użytkownik jest organizatorem i właścicielem tego turnieju
        if request.user.user_type != 'OR' or tournament.user != request.user:
            raise PermissionDenied("You do not have permission to update this tournament.")

        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def create_team(self, request, pk=None):
        '''Add team to tournament.'''
        tournament = self.get_object()
        serializer = serializers.TeamCreationSerializer(data=request.data)

        if serializer.is_valid():
            player_ids = serializer.validated_data['players']

            if User.objects.filter(id__in=player_ids, user_type='PL').count() != 2:
                return Response({"detail": "All players must be players."}, status=status.HTTP_400_BAD_REQUEST)

            team = Team.objects.create()
            team.players.set(player_ids)
            team.save()

            tournament.teams.add(team)

            return Response({"detail": "Team created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'],  url_path='remove_team')
    def remove_team(self, request, pk=None):
        '''Remove the team from tournament if the user is part of the team.'''
        serializer = serializers.RemoveTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = self.get_object()
        team_id = request.data.get('team_id')
        user = request.user

        if not team_id:
            return Response({"detail": "Team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        if not team.players.filter(id=user.id).exists():
            raise PermissionDenied("You are not a member of this team and cannot remove it.")

        tournament.teams.remove(team)

        if team.tournaments.count() == 0:
            team.delete()

        return Response({"detail": "Team removed successfully."}, status=status.HTTP_200_OK)


class PublicViewOfTournamentsViewSet(viewsets.ReadOnlyModelViewSet):
    '''View for listing tournaments publicly.'''

    serializer_class = serializers.TournamentSerializer
    queryset = Tournament.objects.all()
    permission_classes = [AllowAny]  # Allow access to everyone

    def get_queryset(self):
        '''Retrieve tournaments publicly.'''
        return self.queryset.order_by('date_of_beginning')


class TournamentListView(TemplateView):
    template_name = 'tournament/tournament_list.html'


class DetailedTournamentView(TemplateView):
    template_name = 'tournament/tournament_details.html'
