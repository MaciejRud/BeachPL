"""
Serializers for tournament APIs.
"""

from rest_framework import serializers

from core.models import Tournament

class TournamentSerializer(serializers.ModelSerializer):
    '''Serializer for Tournaments.'''

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'tour_type', 'city', 'money_prize', 'sex',
                  'date_of_beginning', 'date_of_finishing']
        read_only_fields = ['id']
