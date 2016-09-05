from rest_framework import serializers

from core.models import Match


class MatchSerializer(serializers.ModelSerializer):

    # season is pre-populated before save in perform_create()
    season = serializers.CharField(required=False)

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

