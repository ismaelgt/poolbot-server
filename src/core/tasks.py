import logging
from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from djangae.db.transaction import atomic

from google.appengine.api import memcache

from .models import (
    Challenge,
    EloHistory,
    Match,
    Player,
    Season,
)

from .utils import form_cache_key, calculate_elo


def recalculate_player_elo_ratings():
    """Iterate over each match, calculate winner and loser elo rating, and save
    these ratings"""
    # we need to make sure all players have an initial elo score as its a migration
    for player in Player.objects.all():
        player.total_elo = 1000
        player.save()

    players = {}

    matches = Match.objects.all().order_by('date')
    for match in matches:
        elos = calculate_elo(match.winner.total_elo, match.loser.total_elo, 1)
        match.winner.total_elo = elos[0]
        match.winner.save()

        match.loser.total_elo = elos[1]
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


def season_migration():
    """
    Migration for the introduction of season related fields.

    This allows for retrospecitve assoication between games, elo
    points and a new season instance.
    """
    first_match = Match.objects.all().order_by('date').first()
    season = Season.objects.create(
        start_date=first_match.date.date(),
        end_date=timezone.now().date() + timedelta(days=7),
        active=True
    )

    for match in Match.objects.all():
        match.season = season
        match.save()

    for player in Player.objects.all():
        player.total_elo = player.elo
        player.season_elo = player.elo
        player.season_win_count = player.total_win_count
        player.season_loss_count = player.total_loss_count
        player.season_grannies_given_count = player.total_grannies_given_count
        player.season_grannies_taken_count = player.total_grannies_taken_count
        player.save()


def set_active_season():
    """Make sure the correct season is set as `active`."""
    today = timezone.now().date()

    try:
        season = Season.objects.get(active=True)
    except Season.DoesNotExist:
        season = None
    else:
        # lets check the current active season hasn't expired
        if season.end_date < today:
            season.deactivate()
            season = None

    # if season is None we try to activate the new season
    if season is None:
        try:
            new_season = Season.objects.get(start_date=today)
        except Season.DoesNotExist:
            # now we have a problem.... there is season to activate
            # so we log a message for the administator
            logging.error('No season set for {}'.format(today))
        else:
            # this sets the active=True flag and resets all
            # denormalized season fields on the player objects
            new_season.activate()

def elo_history_migration():
    """Retrospectively generate all Elo History instances."""

    seasons = Season.objects.all().order_by('start_date')
    for season in seasons:
        player_season_elos = defaultdict(lambda: 1000)
        for match in Match.objects.filter(season=season).order_by('date'):

            winner_season_elo = player_season_elos[match.winner.pk]
            loser_season_elo = player_season_elos[match.loser.pk]
            winner_season_elo, loser_season_elo = calculate_elo(winner_season_elo, loser_season_elo)

            # finally create an elo instance to track history of score
            common_fields = {
                'match': match,
                'season': match.season,
                'date': match.date,
            }
            EloHistory.objects.create(player=match.winner, elo_score=winner_season_elo, **common_fields)
            EloHistory.objects.create(player=match.loser, elo_score=loser_season_elo, **common_fields)

            # update the elo dictionary values
            player_season_elos[match.winner.pk] = winner_season_elo
            player_season_elos[match.loser.pk] = loser_season_elo