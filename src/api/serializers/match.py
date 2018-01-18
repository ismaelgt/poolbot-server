from rest_framework import serializers

from core.models import Match


class MatchSerializer(serializers.ModelSerializer):
    """
    The `season` field is read only for the external API, because we force it to
    use the currently active season inside the MatchViewSet.perform_create()
    method.

    This means that you can ONLY record matches for the currently active
    season, as this is the poolbot centric use case to record match results
    after they have just finished via a client (slack, NFC etc.)
    """

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
            'season',
        )

