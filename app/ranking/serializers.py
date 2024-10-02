'''
Serializers for ranking API.
'''

from rest_framework import serializers
from core.models import Ranking


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ['date', 'gender', 'rankings']
