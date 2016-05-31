from rest_framework import serializers

from core.models import Challenge


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = (
            'id',
            'channel',
            'initiator',
            'challenger',
        )
        read_only_fields = (
            'id',
        )

    def validate(self, data):
        """Validates the data before it persists in the datastore."""
        initiator = data.get('initiator')
        challenger = data.get('challenger')

        # we only expect challenge instances to be set in the poolbot challenge
        # command setup method, which should never try and set the player fields
        if not self.instance:
            if initiator or challenger:
                raise serializers.ValidationError(
                    "Cannot set player field when creating new challenge."
                )

        # once created, we need validate who the players are
        else:
            if self.instance.initiator and self.instance.challenger and self.instance.challenger == challenger:
                raise serializers.ValidationError(
                    "Initiator and challenger cannot be set to the same player."
                )

            if challenger and not self.instance.initiator:
                raise serializers.ValidationError(
                    "Cannot set challenger before a initiator has been set."
                )

            if initiator and self.instance.initiator:
                raise serializers.ValidationError(
                    "Cannot set a new challenge before the old one has been accepted."
                )

            # waiting for the match result to be recorded
            if self.instance.challenger and self.instance.initiator and initiator:
                raise serializers.ValidationError(
                    "Cannot invoke a new challenge, current waiting for the match"
                    "between {initiator} and {challenger} to be recorded."
                    .format(
                        initiator=self.instance.initiator,
                        challenger=self.instance.challenger
                    )
                )

        return data
