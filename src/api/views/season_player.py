from core.models import SeasonPlayer

from .base import TokenRequiredModelViewSet
from ..serializers import SeasonPlayerSerializer


class SeasonPlayerViewSet(TokenRequiredModelViewSet):

    serializer_class = SeasonPlayerSerializer
    queryset = SeasonPlayer.objects.all()
    filter_fields = ('player', 'season')