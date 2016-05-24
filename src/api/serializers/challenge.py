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


        # validation!

        # custom things..
        # cannot set challenger to the same as initiator

        # when updating, can only ever set challenger if inititator exists
        # when updating, cannot set challenger to initiator
        # when updating, allow setting initiator and challenger to none only if initiator is not null but last modified >15min or initaitor and challenge not null and last modified > 15min

