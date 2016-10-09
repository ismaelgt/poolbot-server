from rest_framework import filters

from core.models import EloHistory

from .base import TokenRequiredModelViewSet
from ..serializers import EloHistorySerializer


class EloHistoryViewSet(TokenRequiredModelViewSet):

    serializer_class = EloHistorySerializer
    queryset = EloHistory.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('player', 'season')