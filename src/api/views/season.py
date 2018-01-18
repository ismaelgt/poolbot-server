from core.models import Season

from .base import TokenRequiredModelViewSet
from ..serializers import SeasonSerializer


class SeasonViewSet(TokenRequiredModelViewSet):

    serializer_class = SeasonSerializer
    queryset = Season.objects.all()
    filter_fields = ('active', 'name')
