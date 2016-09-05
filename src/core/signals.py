from google.appengine.api import memcache
from google.appengine.ext import deferred

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .models import Match
from .tasks import update_player_form_cache
from .utils import form_cache_key, calculate_elo


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token associated with a user instance."""
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Match)
def update_elo_ratings(sender, instance=None, created=False, **kwargs):
    """Update the ELO ratings on the related player instances."""
    if created:
        total_elos = calculate_elo(instance.winner.total_elo, instance.loser.total_elo, 1)
        season_elos = calculate_elo(instance.winner.season_elo, instance.loser.season_elo, 1)

        instance.winner.total_elo = total_elos[0]
        instance.winner.season_elo = season_elos[0]
        instance.winner.save()

        instance.loser.total_elo = total_elos[1]
        instance.loser.season_elo = season_elos[1]
        instance.loser.save()

        # with the update elo scores we update the season top five
        # we do this here rather than a seperate listener as order is not gaurenteed
        instance.season.set_top_five_players(commit=True)


@receiver(post_save, sender=Match)
def increment_player_counts(sender, instance=None, created=False, **kwargs):
    """Increment the denormalized counts on the related player instances."""
    if created:
        instance.winner.total_win_count += 1
        instance.winner.season_win_count += 1
        instance.winner.save()

        instance.loser.total_loss_count += 1
        instance.loser.season_loss_count += 1
        instance.loser.save()


@receiver(post_save, sender=Match)
def update_player_form(sender, instance=None, created=False, **kwargs):
    """Update the cached form querysets for two players in a match."""
    if created and instance:
        # wipe the cache incase we try and fetch before the deferred task runs
        players = [instance.winner, instance.loser]
        cache_keys = [form_cache_key(player) for player in players]
        for key in cache_keys:
            memcache.delete(key)

        deferred.defer(update_player_form_cache, instance.pk)


@receiver(post_save, sender=Match)
def increment_granny_count(sender, instance=None, created=False, **kwargs):
    """Increment the denormalized granny counts on the player instances."""
    if created and instance.granny:
        instance.winner.total_grannies_given_count += 1
        instance.winner.season_grannies_given_count += 1
        instance.winner.save()

        instance.loser.total_grannies_taken_count += 1
        instance.loser.season_grannies_taken_count += 1
        instance.loser.save()
