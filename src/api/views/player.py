from rest_framework import filters

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from django.db.models import Q

from core.models import Player, Match

from .base import TokenRequiredModelViewSet
from ..serializers import PlayerSerializer, PatchPlayerSerializer


class PlayerViewSet(TokenRequiredModelViewSet):

    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)

    def get_serializer_class(self):
        """Use a different serializer when handling PATCH requests, which
        makes more fields read_only."""
        serializer_class = self.serializer_class

        if self.request.method == 'PATCH':
            serializer_class = PatchPlayerSerializer

        return serializer_class

    @detail_route(methods=['get'])
    def form(self, request, pk=None):
        """Return the results of recent games involving the specified player."""
        user = self.get_object()

        # we support a limit param which reduces the number of results
        limit = request.query_params.get('limit', 10)

        # this might be pretty inefficent on the datastore...
        recent_games = Match.objects.filter(
            Q(winner=user) | Q(loser=user)
        ).order_by('-date')[:limit]

        # parse the reslts into a easy to digest results string - like `W L L W`
        results = ' '.join([
            'W' if game.winner == user else 'L'
            for game in recent_games
        ])

        return Response(results)
