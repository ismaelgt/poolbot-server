from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .season import Season


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
    season = models.ForeignKey('core.Season', related_name='matches')
    winner = models.ForeignKey('core.Player', related_name='wins')
    loser = models.ForeignKey('core.Player', related_name='loses')
    channel = models.CharField(max_length=10)
    granny = models.BooleanField(default=False)

    objects = MatchManager()

    def clean(self):
        """Validate the date and season match up."""
        # we could determine the season from the date rather than expect
        # it to be passed in, but this would require we do a query with
        # two ineqaulity filters which the datestore doesn't support...
        # so instead we just validate the two
        if (
            self.date.date() < self.season.start_date or
            self.date.date() > self.season.end_date
        ):
            raise ValidationError('The season does not correspond with date provided.')

    def save(self, *args, **kwargs):
        """Find which season the match should be associated with."""
        # we can only query by one inequality on the datastore...
        self.full_clean()
        return super(Match, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{winner} beat {loser}'.format(
            winner=self.winner,
            loser=self.loser
        )
