from datetime import timedelta

from django.db import models
from django.utils import timezone


class Challenge(models.Model):
    """Records the intermediate step between two players agreeing to play,
    and recording the result.
    """
    initiator = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    challenger = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    channel = models.CharField(max_length=10, blank=False, unique=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{} challenged {}'.format(self.challenger, self.initiator)

    def out_of_time(self):
        """Return a boolean to indicate if the last modified timestamp was
        more than ten minutes in the past."""
        return self.last_modified < timezone.now() - timedelta(minutes=10)

    def reset(self, commit=True):
        """Set the initiator and challenger attributes to None."""
        self.initiator = None
        self.challenger = None
        if commit:
            self.save()
