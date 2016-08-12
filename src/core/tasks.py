from google.appengine.api import memcache

from .models import (
    Challenge,
    Match,
    Player,
)
from .utils import form_cache_key, calculate_elo


def recalculate_player_elo_ratings():
    """Iterate over each match, calculate winner and loser elo rating, and save
    these ratings"""
    # we need to make sure all players have an initial elo score as its a migration
    for player in Player.objects.all():
        player.elo = 1000
        player.save()

    players = {}

    matches = Match.objects.all().order_by('date')
    for match in matches:
        elos = calculate_elo(match.winner.elo, match.loser.elo, 1)
        match.winner.elo = elos[0]
        match.winner.save()

        match.loser.elo = elos[1]
        match.loser.save()

def resync_player_match_counts():
    """Iterate over each player, count their win and loss count, then save this
    denormalized data onto the respective player instance.
    """

    players = Player.objects.all()
    for player in players:
        player.total_win_count = Match.objects.filter(winner=player).count()
        player.total_loss_count = Match.objects.filter(loser=player).count()
        player.save()


def resync_player_granny_counts():
    """Iterate over each player and store the grannies they have given/taken."""
    players = Player.objects.all()
    for player in players:
        player.total_grannies_given_count = Match.objects.filter(
            winner=player,
            granny=True
        ).count()
        player.total_grannies_taken_count = Match.objects.filter(
            loser=player,
            granny=True
        ).count()
        player.save()


def add_active_player_flag():
    """Iterate over each player and set their active flag to True."""
    for player in Player.objects.all():
        player.active = True
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
