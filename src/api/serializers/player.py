from rest_framework import serializers

from core.models import Player


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = (
            'slack_id',
            'name',
            'active',
            'joined',
            'age',
            'nickname',
            'country',

            'total_win_count',
            'total_loss_count',
            'total_match_count',
            'total_grannies_given_count',
            'total_grannies_taken_count',
            'total_elo',

            'season_win_count',
            'season_loss_count',
            'season_match_count',
            'season_grannies_given_count',
            'season_grannies_taken_count',
            'season_elo',
        )
        read_only_fields = (
            'active',
            'joined',

            'total_win_count',
            'total_loss_count',
            'total_match_count',
            'total_grannies_given_count',
            'total_grannies_taken_count',
            'total_elo',

            'season_win_count',
            'season_loss_count',
            'season_match_count',
            'season_grannies_given_count',
            'season_grannies_taken_count',
            'season_elo',
        )

    total_match_count = serializers.SerializerMethodField()
    season_match_count = serializers.SerializerMethodField()

    def get_total_match_count(self, obj):
        """Return the sum of the win and loss count."""
        return obj.total_win_count + obj.total_loss_count

    def get_season_match_count(self, obj):
        """Return the sum of the win and loss count."""
        return obj.season_win_count + obj.season_loss_count


class PatchPlayerSerializer(PlayerSerializer):

    class Meta(PlayerSerializer.Meta):

        read_only_fields = PlayerSerializer.Meta.read_only_fields + (
            'slack_id',
            'name',
        )
