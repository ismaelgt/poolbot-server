from django.db import models
from django.utils import timezone


class Player(models.Model):
    """Pool players identified by their slack user ID."""

    slack_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    joined = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.name
