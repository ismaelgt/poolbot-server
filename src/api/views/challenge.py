from core.models import Challenge

from .base import TokenRequiredModelViewSet
from ..serializers import ChallengeSerializer


class ChallengeViewSet(TokenRequiredModelViewSet):

    serializer_class = ChallengeSerializer
    queryset = Challenge.objects.all()
    filter_fields = ('initiator', 'challenger', 'channel')

