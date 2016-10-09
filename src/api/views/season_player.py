from rest_framework import filters

from core.models import SeasonPlayer

from .base import TokenRequiredModelViewSet
from ..serializers import SeasonPlayerSerializer


class SeasonPlayerViewSet(TokenRequiredModelViewSet):

    serializer_class = SeasonPlayerSerializer
    queryset = SeasonPlayer.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('player', 'season')