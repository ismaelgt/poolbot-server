from rest_framework import serializers

from core.models import Player


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = (
            'slack_id',
            'name',
            'joined',
            'total_win_count',
            'total_loss_count',
        )
        read_only_fields = (
            'joined',
        )
