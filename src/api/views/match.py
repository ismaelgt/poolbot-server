from rest_framework import filters, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from core.models import Match

from ..serializers import MatchSerializer


class MatchViewSet(viewsets.ModelViewSet):

    serializer_class = MatchSerializer
    queryset = Match.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('winner', 'loser')

    @list_route(methods=['get'])
    def head_to_head(self, request, pk=None):
        """Return the results of head to heads between two players."""
        player1 = request.query_params.get('player1')
        player2 = request.query_params.get('player2')

        if player1 is None or player2 is None:
            return None

        player1_wins = self.queryset.filter(winner=player1, loser=player2)
        player2_wins = self.queryset.filter(winner=player2, loser=player1)

        results = {
            player1: player1_wins.count(),
            player2: player2_wins.count(),
        }

        return Response(results)
