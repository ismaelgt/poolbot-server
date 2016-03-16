from django.db import models
from django.utils import timezone


class Match(models.Model):
    """Documents the result of a pool match between two players."""

    date = models.DateTimeField(default=timezone.now)
    winner = models.ForeignKey('core.Player', related_name='wins')
    loser = models.ForeignKey('core.Player', related_name='loses')
    channel = models.CharField(max_length=10)
    granny = models.BooleanField(default=False)

    def __unicode__(self):
        return 'worked'
