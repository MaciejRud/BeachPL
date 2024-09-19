"""
Views for the tournament APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tournament
from tournament import serializers


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
