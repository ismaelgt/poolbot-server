from rest_framework import serializers

from core.models import Season


class SeasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Season
        fields = (
            'start_date',
            'end_date',
            'active',

            'first_place',
            'second_place',
            'third_place',
            'forth_place',
            'fifth_place'
        )
        read_only_fields = (
            'start_date',
            'end_date',
            'active',

            'first_place',
            'second_place',
            'third_place',
            'forth_place',
            'fifth_place'
        )
