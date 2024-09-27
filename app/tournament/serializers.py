"""
Serializers for tournament APIs.
"""

from rest_framework import serializers

from core.models import Tournament, Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'players']

class TournamentSerializer(serializers.ModelSerializer):
    '''Serializer for Tournaments.'''
    sex_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    ranking_display = serializers.SerializerMethodField()
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'tour_type', 'type_display', 'city',
                  'money_prize', 'sex', 'sex_display',
                  'ranking_type', 'ranking_display',
                  'date_of_beginning', 'date_of_finishing',
                  'teams',]
        read_only_fields = ['id']

    def get_sex_display(self, obj):
        return obj.get_sex_display()

    def get_type_display(self, obj):
        return obj.get_tour_type_display()

    def get_ranking_display(self, obj):
        return obj.get_ranking_type_display()


class TournamentDetailSerializer(TournamentSerializer):
    '''Serializer of manager of Tournament API.'''

    class Meta(TournamentSerializer.Meta):
        fields = TournamentSerializer.Meta.fields


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'players', 'tournament']

class TeamCreationSerializer(serializers.Serializer):
    players = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=2
    )

class RemoveTeamSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
