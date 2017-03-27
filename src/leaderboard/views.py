import datetime

from google.appengine.api import memcache
from django.shortcuts import render
from django.http import JsonResponse
from core.models import Player

from .decorators import ip_authorization

LEADERBOARD_CACHE_KEY = 'players'
PREVIOUS_LEADERBOARD_CACHE_KEY = 'players_previous'
PLAYERS_CACHE_TIMEOUT = 30


@ip_authorization
def index(request):
    """Main page which renders the leaderboard table."""
    return render(request, 'leaderboard/index.html', {})


@ip_authorization
def api(request):
    """Internal API hit by the leaderboard index."""
    LAST_UPDATED_CACHE_KEY = 'last_updated'
    leaderboard = memcache.get(LEADERBOARD_CACHE_KEY)
    previous_leaderboard = memcache.get(PREVIOUS_LEADERBOARD_CACHE_KEY) or leaderboard

    if leaderboard is None:
        leaderboard = get_leaderboard(previous_leaderboard)

        # provide a timeout for the current leaderboard
        memcache.add(key=LEADERBOARD_CACHE_KEY, value=leaderboard, time=PLAYERS_CACHE_TIMEOUT)
        memcache.add(key=PREVIOUS_LEADERBOARD_CACHE_KEY, value=leaderboard)
        memcache.add(key=LAST_UPDATED_CACHE_KEY, value=datetime.datetime.now(), time=PLAYERS_CACHE_TIMEOUT)

    last_updated = memcache.get(LAST_UPDATED_CACHE_KEY)
    if last_updated:
        cached_for = (datetime.datetime.now() - last_updated).seconds
    else:
        cached_for = 0

    return JsonResponse(
        dict(
            players=leaderboard,
            secondsLeft=PLAYERS_CACHE_TIMEOUT - cached_for,
            cacheLifetime=PLAYERS_CACHE_TIMEOUT
        )
    )


# Utility functions

def get_leaderboard(previous_leaderboard=None):
    """
    Format data ready for the leaderboard display, by filtering all active
    players in the current season who have played a match.
    """
    # TODO all this could probably go on the Player model manager
    players = Player.objects.filter(active=True).order_by('-season_elo')

    leaderboard = []
    for player in players:
        # exclude players who haven't played this season
        if (player.season_win_count + player.season_loss_count) == 0:
            continue

        leaderboard.append(
            dict(
                name=player.real_name,
                season_elo=player.season_elo,
                diff=get_diff(player, previous_leaderboard) if previous_leaderboard else 0,
                slack_id=player.slack_id,
            )
        )

    return add_leaderboard_positions(leaderboard)


def get_diff(player, previous_leaderboard):
    """Returns num season_elo points gained/lost since the previous state."""
    player_previous_state = get_previous_player_state(player, previous_leaderboard)
    if player_previous_state:
        return player.season_elo - player_previous_state['season_elo']
    return 0


def get_previous_player_state(player, previous_leaderboard):
    for player_previous_state in previous_leaderboard:
        if player_previous_state['slack_id'] == player.slack_id:
            return player_previous_state


def add_leaderboard_positions(players):
    """Calculates and adds the player positions for leaderboard table listing."""
    position = 1
    for idx, player in enumerate(players):
        player['id'] = idx
        if idx == 0:
            # first place - no previous player to compare
            player['position'] = position
        else:
            # keep track of the previous player, if the current player has the
            # same points then they are tied so we mark with a hyphen
            previous_player = players[idx - 1]
            if previous_player['season_elo'] == player['season_elo']:
                player['position'] = '-'
            else:
                player['position'] = position

        position += 1

    return players
