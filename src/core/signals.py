from google.appengine.api import memcache
from google.appengine.ext import deferred

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .models import Match
from .tasks import update_player_form_cache
from .utils import form_cache_key


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token associated with a user instance."""
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=Match)
def update_elo_ratings(sender, instance=None, created=False, **kwargs):
    """Update the ELO ratings on the related player instances."""
    if created:
        elos = utils.calculate_elo(instance.winner.elo, instance.loser.elo, 1)

        instance.winner.elo = elos[0]
        instance.winner.save()

        instance.winner.elo = elos[1]
        instance.loser.save()

@receiver(post_save, sender=Match)
def increment_player_counts(sender, instance=None, created=False, **kwargs):
    """Increment the denormalized counts on the related player instances."""
    if created:
        instance.winner.total_win_count += 1
        instance.winner.save()

        instance.loser.total_loss_count += 1
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
