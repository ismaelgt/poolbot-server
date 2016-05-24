from django.db import models
from django.utils import timezone


class Player(models.Model):
    """Pool players identified by their slack user ID."""

    slack_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    joined = models.DateTimeField(default=timezone.now)

    # denormalized counts which would be slow to fetch at runtime
    # these are updated in the increment_player_counts signal handler
    total_win_count = models.IntegerField(default=0)
    total_loss_count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name
