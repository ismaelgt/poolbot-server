from django.db import models


class LeaderboardConfig(models.Model):
    slack_api_token = models.CharField(null=True, max_length=255)
