"""
Views for the tournament APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from core.models import Tournament
from tournament import serializers

from django.views.generic import TemplateView


class TournamentViewSet(viewsets.ModelViewSet):
    '''View for manage tournament APIs.'''

    serializer_class = serializers.TournamentDetailSerializer
    queryset = Tournament.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Retrieve tournaments for authoritated users.'''
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        '''Serializer for list of tournaments.'''
        if self.action == 'list':
            self.serializer_class = serializers.TournamentSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        '''Create a new tournament.'''
        serializer.save(user=self.request.user)


class TournamentListView(TemplateView):
    template_name = 'tournament/tournament_list.html'


class DetailedTournamentView(TemplateView):
    template_name = 'tournament/tournament_details.html'


class PublicViewOfTournamentsViewSet(viewsets.ReadOnlyModelViewSet):
    '''View for listing tournaments publicly.'''

    serializer_class = serializers.TournamentSerializer
    queryset = Tournament.objects.all()
    permission_classes = [AllowAny]  # Allow access to everyone

    def get_queryset(self):
        '''Retrieve tournaments publicly.'''
        return self.queryset.order_by('date_of_beginning')
