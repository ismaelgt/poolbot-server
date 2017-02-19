from core.models import Player

from .cache import LeaderboardCache

SLACK_NAMES_CACHE_KEY = 'slack_name'
PREVIOUS_STATE_CACHE_KEY = 'players_previous'
PLAYERS_CACHE_KEY = 'players'

cache = LeaderboardCache()


def get_diff(player):
    """Returns num season_elo points gained/lost since the previous state."""
    for player_previous_state in cache.get(PREVIOUS_STATE_CACHE_KEY) or []:
        if player_previous_state['slack_id'] == player.slack_id:
            return player.season_elo - player_previous_state['season_elo']
    return 0


def get_leaderboard_data():
    """
    Format data ready for the leaderboard display, by filtering all active
    players in the current season who have played a match.
    """
    # TODO all this could probably go on the Player model manager
    qs = Player.objects.filter(active=True).order_by('-season_elo')

    players = [
        dict(
            name=player.real_name,
            season_elo=player.season_elo,
            diff=get_diff(player),
            slack_id=player.slack_id,
        )
        for player in qs
        if (player.season_win_count + player.season_loss_count) > 0
    ]

    return add_leaderboard_positions(players)


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
