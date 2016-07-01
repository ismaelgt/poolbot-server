from google.appengine.api import memcache

from .models import (
    Challenge,
    Match,
    Player,
)
from .utils import form_cache_key

def recalculate_player_elo_ratings():
    """Iterate over each match, calculate winner and loser elo rating, and save
    these ratings"""

    players = {}

    matches = Match.objects.all()
    for match in matches:
        winner_elo = players[match.winner.slack_id] or 1000
        loser_elo = players[match.loser.slack_id] or 1000

        elos = utils.calculate_elo(match.winner.elo, match.loser.elo, 1)

        players[match.winner.slack_id] = elos[0]
        players[match.loser.slack_id] = elos[1]

    for slack_id, elo in players.iteritems():
        player = Player.objects.get(slack_id=slack_id)
        player.elo = elo
        player.save()

def resync_player_match_counts():
    """Iterate over each player, count their win and loss count, then save this
    denormalized data onto the respective player instance.
    """

    players = Player.objects.all()
    for player in players:
        player.total_win_count = Match.objects.filter(winner=player).count()
        player.total_loss_count = Match.objects.filter(loser=player).count()
        player.save()


def reset_challenges():
    """Set the initiator and challenge attributes to None on all challenge
    instances which have an initiator but were last modified more than fifteen
    minutes ago.
    """
    # we can't filter by a last_modified__lt filter as the datastore
    # only supports one inquality per query :(
    for challenge in Challenge.objects.filter(initiator__isnull=False):
        if challenge.out_of_time():
            challenge.reset(commit=True)


def update_player_form_cache(match_pk):
    match = Match.objects.get(pk=match_pk)
    for player in [match.winner, match.loser]:
        cache_key = form_cache_key(player)
        queryset = Match.objects.matches_involving_player(player)
        memcache.set(cache_key, queryset)
