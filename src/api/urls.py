"""Poolbot API router"""

from rest_framework import routers

from .views import (
    EloHistoryViewSet,
    ChallengeViewSet,
    MatchViewSet,
    PlayerViewSet,
    SeasonViewSet,
    SeasonPlayerViewSet,
)

api_router = routers.SimpleRouter()
api_router.register(r'elo-history', EloHistoryViewSet)
api_router.register(r'match', MatchViewSet)
api_router.register(r'player', PlayerViewSet)
api_router.register(r'challenge', ChallengeViewSet)
api_router.register(r'season', SeasonViewSet)
