from rest_framework import filters

from core.models import Challenge

from .base import TokenRequiredModelViewSet
from ..serializers import ChallengeSerializer


class ChallengeViewSet(TokenRequiredModelViewSet):

    serializer_class = ChallengeSerializer
    queryset = Challenge.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('initiator', 'challenger', 'channel')

