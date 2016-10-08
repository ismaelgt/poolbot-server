from rest_framework import serializers

from core.models import Season


class SeasonSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(format="%d %b %Y")
    end_date = serializers.DateField(format="%d %b %Y")

    class Meta:
        model = Season
        fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'active',
        )
        read_only_fields = (
            'pk',
            'name',
            'start_date',
            'end_date',
            'active',
        )