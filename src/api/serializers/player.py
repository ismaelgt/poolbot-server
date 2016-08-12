from rest_framework import serializers

from core.models import Player


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = (
            'slack_id',
            'name',
            'joined',
            'age',
            'nickname',
            'country',
            'total_win_count',
            'total_loss_count',
            'total_match_count',
            'elo',
        )
        read_only_fields = (
            'joined',
            'total_win_count',
            'total_loss_count',
            'total_match_count',
            'elo',
        )

    total_match_count = serializers.SerializerMethodField()

    def get_total_match_count(self, obj):
        """Return the sum of the win and loss count."""
        return obj.total_win_count + obj.total_loss_count


class PatchPlayerSerializer(PlayerSerializer):

    class Meta(PlayerSerializer.Meta):

        read_only_fields = PlayerSerializer.Meta.read_only_fields + (
            'slack_id',
            'name',
        )
