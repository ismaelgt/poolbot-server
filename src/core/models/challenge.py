from django.db import models
from django.utils import timezone


class Challenge(models.Model):
    """Records the intermediate step between two players agreeing to play,
    and recording the result.
    """
    initiator = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    challenger = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    channel = models.CharField(max_length=10, blank=False, unique=True)

    def __unicode__(self):
        return '{} challenged {}'.format(self.challenger, self.initiator)
