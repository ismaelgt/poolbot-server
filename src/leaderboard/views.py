from django.shortcuts import render
from django.http import JsonResponse

from .utils import (
    cache,
    PLAYERS_CACHE_KEY,
    PREVIOUS_STATE_CACHE_KEY,
    PLAYERS_CACHE_TIMEOUT,
    get_players,
)
from .decorators import ip_authorization


@ip_authorization
def index(request):
    return render(request, 'leaderboard/index.html', {})


@ip_authorization
def api(request):
    current_state = cache.get(PLAYERS_CACHE_KEY)
    previous_state = cache.get(PREVIOUS_STATE_CACHE_KEY)

    if not current_state and not previous_state:
        # intialise
        players = get_players()
        cache.set(PLAYERS_CACHE_KEY, players, timeout=PLAYERS_CACHE_TIMEOUT)
        cache.set(PREVIOUS_STATE_CACHE_KEY, players)
    elif current_state is None:
        # cache has expired, refresh the players list
        players = get_players()

        no_change = set([p['diff'] for p in players]) == set([0])
        if no_change:
            # elo hasn't changed meaning no one has played
            cache.set(PLAYERS_CACHE_KEY, previous_state, timeout=PLAYERS_CACHE_TIMEOUT)
        else:
            # someone's played, update the table
            cache.set(PLAYERS_CACHE_KEY, players, timeout=PLAYERS_CACHE_TIMEOUT)
            cache.set(PREVIOUS_STATE_CACHE_KEY, players)

    return JsonResponse(
        dict(
            players=cache.get(PLAYERS_CACHE_KEY),
            secondsLeft=cache.time_remaining(PLAYERS_CACHE_KEY),
            cacheLifetime=PLAYERS_CACHE_TIMEOUT
        )
    )
