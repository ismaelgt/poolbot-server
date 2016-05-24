import django_filters


from core.models import Challenge


class ChallengeFilter(django_filters.FilterSet):

    class Meta:
        model = Challenge
        fields = ['initiator', 'match', 'challenger', 'active']
