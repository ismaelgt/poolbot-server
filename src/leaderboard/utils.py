import json
import logging

from django.conf import settings

import requests
import requests_toolbelt.adapters.appengine

from core.models import Player

from .cache import Cache

requests_toolbelt.adapters.appengine.monkeypatch()

SLACK_NAMES_CACHE_KEY = 'slack_name'
PREVIOUS_STATE_CACHE_KEY = 'players_previous'
PLAYERS_CACHE_KEY = 'players'
PLAYERS_CACHE_TIMEOUT = 30

cache = Cache()



        logging.error(content['error'])


def get_diff(player):
    """returns num season_elo points gained/lost since the previous state"""
    for player_previous_state in cache.get(PREVIOUS_STATE_CACHE_KEY) or []:
        if player_previous_state['slack_id'] == player.slack_id:
            return player.season_elo - player_previous_state['season_elo']
    return 0


def get_players():
    qs = Player.objects.filter(active=True).order_by('-season_elo')
    slack_names = get_slack_names()

    players = [
        dict(
            name=slack_names.get(player.slack_id, player.name),
            season_elo=player.season_elo,
            diff=get_diff(player),
            slack_id=player.slack_id,
        )
        for player in qs
        if player.active and (player.season_win_count + player.season_loss_count) > 0
    ]

    players_with_positions = add_positions(players)
    return players_with_positions


def add_positions(players):
    """calculates and adds the player positions for table listing"""
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
