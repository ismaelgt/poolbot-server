from google.appengine.api import memcache

from rest_framework import filters

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from core.models import Player, Match
from core.utils import format_matches_to_show_form, form_cache_key

from .base import TokenRequiredModelViewSet
from ..serializers import MatchSerializer, PlayerSerializer, PatchPlayerSerializer


class PlayerViewSet(TokenRequiredModelViewSet):

    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    permissions = []
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('active', 'total_grannies_given_count')

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

        # try and get the queryset of results from memcache
        cache_key = form_cache_key(user)
        queryset = memcache.get(cache_key)
        if queryset is None:
            # this might be pretty inefficent on the datastore...
            queryset = Match.objects.matches_involving_player(user)
            memcache.set(cache_key, queryset)

        # we support a limit param which reduces the number of results
        limit = int(request.query_params.get('limit', 10))
        limited_queryset = queryset[:limit]

        form = format_matches_to_show_form(limited_queryset, user)

        return Response(form)

    @detail_route(methods=['get'])
    def grannies(self, request, pk=None):
        """Return the games with a granny involving the specified player."""
        player = self.get_object()

        grannies_given = Match.objects.filter(winner=player, granny=True)
        grannies_taken = Match.objects.filter(loser=player, granny=True)
        all_granny_games = grannies_given | grannies_taken

        all_granny_games = all_granny_games.order_by('-date')
        serializer = MatchSerializer(all_granny_games, many=True)
        return Response(serializer.data)
