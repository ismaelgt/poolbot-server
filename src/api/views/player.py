from rest_framework import filters, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from django.db.models import Q

from core.models import Player, Match

from ..serializers import PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):

    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend,)

    @detail_route(methods=['get'])
    def form(self, request, pk=None):
        """Return the results of recent games involving the specified player."""
        user = self.get_object()

        # this might be pretty inefficent on the datastore...
        recent_games = Match.objects.filter(
            Q(winner=user) | Q(loser=user)
        ).order_by('-date')

        # parse the reslts into a easy to digest results string - like `W L L W`
        results = ' '.join([
            'W' if game.winner == user else 'L'
            for game in recent_games
        ])

        return Response(results)
