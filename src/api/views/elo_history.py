from core.models import EloHistory

from .base import TokenRequiredModelViewSet
from ..serializers import EloHistorySerializer


class EloHistoryViewSet(TokenRequiredModelViewSet):

    serializer_class = EloHistorySerializer
    queryset = EloHistory.objects.all()
    filter_fields = ('player', 'season')