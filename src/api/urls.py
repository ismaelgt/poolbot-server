"""Poolbot API router"""

from rest_framework import routers

from .views import MatchViewSet, PlayerViewSet

api_router = routers.SimpleRouter()
api_router.register(r'match', MatchViewSet)
api_router.register(r'player', PlayerViewSet)
