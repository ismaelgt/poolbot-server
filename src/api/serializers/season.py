from rest_framework import serializers

from core.models import Season, SeasonPlayer


class SeasonSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(format="%d %b %Y")
    end_date = serializers.DateField(format="%d %b %Y")
    winner = serializers.SerializerMethodField()

    class Meta:
        model = Season
        fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'active',
            'winner'
        )
        read_only_fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'active',
            'winner',
        )

    def get_winner(self, obj):
        """Includes the PK for the season winner in the serializer."""
        season_player = SeasonPlayer.objects.get_winner(obj)
        return (season_player.player.pk if season_player else None)