"""
Serializers for tournament APIs.
"""

from rest_framework import serializers

from core.models import (
    Tournament,
    Team,
)

class TeamSerializer(serializers.ModelSerializer):
    string = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'players', 'string']

    def get_string(self, obj):
        return str(obj)

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


class TeamCreationSerializer(serializers.Serializer):
    players = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=2
    )

class RemoveTeamSerializer(serializers.Serializer):
    team_id = serializers.IntegerField(required=True, help_text="ID of the team to be removed from the tournament.")


class TeamPositionSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    position = serializers.IntegerField()


class AwardPointsSerializer(serializers.Serializer):
    '''Serializer for awarding points to teams.'''
    team_results = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(required=True),
            required=True
        ),
        required=True
    )
