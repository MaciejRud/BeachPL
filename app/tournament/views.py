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
    '''View for manage tournament APIs.'''

    serializer_class = serializers.TournamentDetailSerializer
    queryset = Tournament.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Retrieve tournaments for authenticated users.'''
        user = self.request.user

        # Jeśli użytkownik jest organizatorem, widzi tylko swoje turnieje
        if user.user_type == 'OR':
            return self.queryset.filter(user=user).order_by('-id')

        # Jeśli użytkownik jest graczem, widzi turnieje, w których bierze udział jego drużyna
        elif user.user_type == 'PL':
            # Sprawdź, czy akcja to 'create_team'
            if self.action == 'create_team':
                # Zwróć wszystkie turnieje
                return self.queryset.all()
            else:
                # Zwróć tylko turnieje, w których bierze udział jego drużyna
                return self.queryset.filter(teams__players=user).distinct()
            # Inni użytkownicy (np. sędziowie, wolontariusze) mogą mieć dodatkowe prawa w przyszłości
        return Tournament.objects.none()

    def get_serializer_class(self):
        '''Serializer for list of tournaments.'''
        if self.action == 'list':
            self.serializer_class = serializers.TournamentSerializer
        elif self.action == 'create_team':
            return serializers.TeamCreationSerializer
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

            # Sprawdź, czy zalogowany użytkownik jest jednym z graczy
            if request.user.id not in player_ids:
                return Response({"detail": "You must be part of the team."}, status=status.HTTP_400_BAD_REQUEST)

            players = User.objects.filter(id__in=player_ids, user_type='PL')

            # Sprawdź, czy jest dokładnie dwóch graczy i czy są 'players'
            if players.count() != 2:
                return Response({"detail": "All players must be players."}, status=status.HTTP_400_BAD_REQUEST)

            # Sprawdź, czy płeć obu graczy zgadza się z płcią turnieju
            if players.filter(gender=tournament.sex).count() != 2:
                return Response({"detail": "Both players must have the same gender as required by the tournament."}, status=status.HTTP_400_BAD_REQUEST)

            team = Team.objects.create()
            team.players.set(player_ids)
            team.save()

            tournament.teams.add(team)

            team_serializer = serializers.TeamSerializer(team)

            return Response({
                "detail": "Team created successfully.",
                'team':team_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove_team')
    def remove_team(self, request, pk=None):
        '''Remove the team from the tournament if the user is an organizer or part of the team.'''
        serializer = serializers.RemoveTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = self.get_object()
        team_id = serializer.validated_data.get('team_id')
        user = request.user

        if not team_id:
            return Response({"detail": "Team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            team = tournament.teams.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found in this tournament."}, status=status.HTTP_404_NOT_FOUND)

        # Sprawdź, czy użytkownik jest organizatorem
        if user.user_type == 'OR':
            # Użytkownik jest organizatorem, może usunąć każdą drużynę
            tournament.teams.remove(team)

        # Sprawdź, czy użytkownik jest graczem
        elif user.user_type == 'PL':
            # Sprawdź, czy użytkownik jest członkiem drużyny
            if not team.players.filter(id=user.id).exists():
                raise PermissionDenied("You are not a member of this team and cannot remove it.")

            tournament.teams.remove(team)
        else:
            return Response({"detail": "You do not have permission to remove this team."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": "Team removed successfully from the tournament."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='award-points')
    def award_points(self, request, pk=None):
        '''Award points to teams based on their positions in the tournament.'''


        # Sprawdzenie, czy użytkownik jest organizatorem
        if request.user.user_type != 'OR':
            return Response({"detail": "You do not have permission to award points."}, status=status.HTTP_403_FORBIDDEN)

        tournament = self.get_object()
        # Oczekiwany format danych wejściowych
        serializer = serializers.AwardPointsSerializer(data=request.data)
        if serializer.is_valid():
            # Przetwarzanie danych
            team_results = serializer.validated_data['team_results']

            for result in team_results:
                team_id = result['team_id']
                position = result['position']
                # Logika przyznawania punktów
                team = Team.objects.get(id=team_id)

                # Przykładowa logika przyznawania punktów
                points_awarded = self.calculate_points(position)  # Zdefiniuj tę metodę według swojego systemu punktowego
                for i in team.players.all():
                    PlayerTournamentResult.objects.create(
                        player=i,
                        team=team,
                        tournament=tournament,
                        points_awarded=points_awarded,
                        position=position,
                        tournament_date=tournament.date_of_finishing,
                    )

            return Response({"detail": "Points awarded successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def calculate_points(self, position):
        '''Define your point system based on position.'''
        # Przykładowa logika punktowa
        if position == 1:
            return 100  # Punkty za pierwsze miejsce
        elif position == 2:
            return 60   # Punkty za drugie miejsce
        elif position == 3:
            return 30   # Punkty za trzecie miejsce
        return 0  # Brak punktów za inne miejsca


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


class CreateTournamentTemplate(TemplateView):
    template_name = 'tournament/create-tournament.html'

class CreateAndAddTeamTemplate(TemplateView):
    template_name = 'tournament/add-team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_id = self.kwargs['id']  # Pobierz ID z URL
        context['tournament'] = Tournament.objects.get(id=tournament_id)  # Pobierz obiekt turnieju
        return context
