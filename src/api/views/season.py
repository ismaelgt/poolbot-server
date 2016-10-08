from rest_framework import filters

from core.models import Season

from .base import TokenRequiredModelViewSet
from ..serializers import SeasonSerializer


class SeasonViewSet(TokenRequiredModelViewSet):

    serializer_class = SeasonSerializer
    queryset = Season.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('active', 'name')
