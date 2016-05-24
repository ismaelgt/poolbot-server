"""Poolbot API router"""

from rest_framework import routers

from .views import ChallengeViewSet, MatchViewSet, PlayerViewSet

api_router = routers.SimpleRouter()
api_router.register(r'match', MatchViewSet)
api_router.register(r'player', PlayerViewSet)
api_router.register(r'challenge', ChallengeViewSet)
