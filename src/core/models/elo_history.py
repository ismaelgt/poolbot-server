from django.db import models
from django.utils import timezone


class EloHistory(models.Model):
    """Documents the history of elo points awarded to a player."""

    # FK relationships to other models
    player = models.ForeignKey('core.Player')
    match = models.ForeignKey('core.Match')
    season = models.ForeignKey('core.Season')

    # meta fields 
    date = models.DateTimeField(default=timezone.now)

    # denormalized fields
    elo_score = models.IntegerField(blank=True)

    def __unicode__(self):
        return "{player} had {elo} points on {date}".format(
            player=self.player,
            elo=self.elo_score,
            date=self.date
        )