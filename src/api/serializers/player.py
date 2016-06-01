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

        )
        read_only_fields = (
            'joined',
            'total_win_count',
            'total_loss_count',
        )


class PatchPlayerSerializer(PlayerSerializer):

    class Meta(PlayerSerializer.Meta):

        read_only_fields = PlayerSerializer.Meta.read_only_fields + (
            'slack_id',
            'name',
        )
