from rest_framework import serializers

from core.models import Match


class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = (
            'date',
            'season',
            'winner',
            'loser',
            'channel',
            'granny',
        )
        read_only_fields = (
            'date',
        )

