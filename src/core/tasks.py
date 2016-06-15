from google.appengine.api import memcache

from .models import (
    Challenge,
    Match,
    Player,
)
from .utils import form_cache_key


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
