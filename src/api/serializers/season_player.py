from rest_framework import serializers

from core.models import SeasonPlayer


class SeasonPlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SeasonPlayer
        fields = (
            'player',
            'season',
            'elo_score',
            'win_count',
            'loss_count',
            'match_count',
        )
        read_only_fields = (
            'player',
            'season',
            'elo_score',
            'win_count',
            'loss_count',
            'match_count',
        )

    match_count = serializers.SerializerMethodField()

    def get_match_count(self, obj):
        """Return the sum of the win and loss count."""
        return obj.win_count + obj.loss_count
