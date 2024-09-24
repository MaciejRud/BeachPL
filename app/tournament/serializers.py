"""
Serializers for tournament APIs.
"""

from rest_framework import serializers

from core.models import Tournament


class TournamentSerializer(serializers.ModelSerializer):
    '''Serializer for Tournaments.'''
    sex_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'tour_type', 'type_display', 'city',
                  'money_prize', 'sex', 'sex_display',
                  'date_of_beginning', 'date_of_finishing']
        read_only_fields = ['id']

    def get_sex_display(self, obj):
        return obj.get_sex_display()

    def get_type_display(self, obj):
        return obj.get_tour_type_display()


class TournamentDetailSerializer(TournamentSerializer):
    '''Serializer of manager of Tournament API.'''

    class Meta(TournamentSerializer.Meta):
        fields = TournamentSerializer.Meta.fields
