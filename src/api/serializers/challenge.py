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
        new_initiator = data.get('initiator')
        new_challenger = data.get('challenger')

        # we only expect challenge instances to be set in the poolbot challenge
        # command setup method, which should never try and set the player fields
        if not self.instance:
            if new_initiator or new_challenger:
                raise serializers.ValidationError(
                    "Cannot set player field when creating new challenge."
                )

        else:
            existing_initiator = self.instance.initiator
            existing_challenger = self.instance.challenger

            # when trying to set the initiator to a new player...
            if new_initiator and not new_challenger:

                # waiting for last challenge to be accepted
                if existing_initiator and not existing_challenger:
                    raise serializers.ValidationError(
                        "Cannot create a new challenge before the old one "
                        "created by {challenger} has been accepted."
                        .format(challenger=existing_initiator)
                    )

                # waiting for the match result to be recorded
                if existing_initiator and existing_challenger:
                    raise serializers.ValidationError(
                        "Cannot invoke a new challenge until the result between"
                        "{initiator} and {challenger} has been recorded."
                        .format(
                            initiator=self.instance.initiator,
                            challenger=self.instance.challenger
                        )
                    )

            # when trying to set the challenger to a player
            if new_challenger and not new_initiator:

                # make sure the challenger is not the same player as initiator
                if existing_initiator and (existing_initiator == new_challenger):
                    raise serializers.ValidationError(
                        "You cannot accept your own challenge!"
                    )

                # trying to accept a challenge before one has been created
                if not existing_initiator:
                    raise serializers.ValidationError(
                        "Cannot set challenger before a initiator has been set."
                    )

                # waiting for the match result to be recorded
                if existing_initiator and existing_challenger:
                    raise serializers.ValidationError(
                        "The existing challenge has already been accepted by {}!"
                        "We're waiting for the result to be recorded."
                        .format(self.instance.challenger)
                    )

        return data
