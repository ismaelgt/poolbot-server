from rest_framework import serializers

from core.models import EloHistory


class EloHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = EloHistory
        fields = (
            'player',
            'season',
            'match',
            'date',
            'elo_score',
        )
        read_only_fields = (
            'player',
            'season',
            'match',
            'date',
            'elo_score',
        )

