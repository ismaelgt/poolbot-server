from django.db import models
from django.db.models import Q
from django.utils import timezone


class MatchManager(models.Manager):
    """Custom manager for the Match model."""

    def matches_involving_player(self, player):
        """Return all match instances where the given player was involved."""
        return self.get_queryset().filter(
            Q(winner=player) | Q(loser=player)
        ).order_by('-date')


class Match(models.Model):
    """Documents the result of a pool match between two players."""

    date = models.DateTimeField(default=timezone.now)
    winner = models.ForeignKey('core.Player', related_name='wins')
    loser = models.ForeignKey('core.Player', related_name='loses')
    channel = models.CharField(max_length=10)
    granny = models.BooleanField(default=False)

    objects = MatchManager()

    def __unicode__(self):
        return '{winner} beat {loser}'.format(
            winner=self.winner,
            loser=self.loser
        )
