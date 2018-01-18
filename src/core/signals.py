from google.appengine.api import memcache
from google.appengine.ext import deferred

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .models import Match, SeasonPlayer, EloHistory
from .tasks import update_player_form_cache
from .utils import calculate_elo


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token associated with a user instance."""
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Match)
def update_denormalized_player_fields(sender, instance=None, created=False, **kwargs):
    """Update the ELO ratings and win/loss counts on the related player instances."""
    if created:

        winner = instance.winner
        loser = instance.loser

        winner_total_elo, loser_total_elo = calculate_elo(winner.total_elo, loser.total_elo)
        winner_season_elo, loser_season_elo = calculate_elo(winner.season_elo, loser.season_elo)
        winner.total_elo = winner_total_elo
        winner.season_elo = winner_season_elo
        winner.increment_win_counts(commit=False)
        if instance.granny:
            winner.increment_grannies_given_counts(commit=False)
        winner.save()

        # update all denormalized fields on the loser
        loser = instance.loser
        loser.total_elo = loser_total_elo
        loser.season_elo = loser_season_elo
        loser.increment_loss_counts(commit=False)
        if instance.granny:
            loser.increment_grannies_taken_counts(commit=False)
        loser.save()

        # defer denormalization onto season player - this is safe
        # to defer as the serialized response from the API after
        # recording a game does not embed any data from this model
        deferred.defer(SeasonPlayer.objects.update_active, player=winner, elo=winner_season_elo, wins=winner.season_win_count, losses=winner.season_loss_count)
        deferred.defer(SeasonPlayer.objects.update_active, player=loser, elo=loser_season_elo, wins=loser.season_win_count, losses=loser.season_loss_count)

        # finally create an elo instance to track history of score
        EloHistory.objects.create(player=winner, match=instance, season=instance.season, elo_score=winner_season_elo)
        EloHistory.objects.create(player=loser, match=instance, season=instance.season, elo_score=loser_season_elo)


@receiver(post_save, sender=Match)
def update_player_form_post_save(sender, instance=None, created=False, **kwargs):
    """Update the cached form querysets for two players in a match."""
    if created and instance:
        # wipe the cache incase we try and fetch before the deferred task runs
        players = [instance.winner, instance.loser]
        for player in players:
            memcache.delete(player.form_cache_key)

        deferred.defer(update_player_form_cache, instance.winner, instance.loser)


@receiver(post_delete, sender=Match)
def update_player_form_post_save(sender, instance=None, created=False, **kwargs):
    """Update the cached form querysets for two players in a match."""
    # wipe the cache incase we try and fetch before the deferred task runs
    players = [instance.winner, instance.loser]
    for player in players:
        memcache.delete(player.form_cache_key)

    deferred.defer(update_player_form_cache, instance.winner, instance.loser)
