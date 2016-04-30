from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .models import Match


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token associated with a user instance."""
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Match)
def increment_player_counts(sender, instance=None, created=False, **kwargs):
    """Increment the denormalized counts on the related player instances."""
    if created:
        instance.winner.total_win_count += 1
        instance.winner.save()

        instance.loser.total_loss_count += 1
        instance.loser.save()
