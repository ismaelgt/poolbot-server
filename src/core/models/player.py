import json
import logging
import urllib

from django.db import models
from django.utils import timezone

from google.appengine.api import urlfetch

from core.utils import form_cache_key


class Player(models.Model):
    """Pool players identified by their slack user ID."""

    SLACK_DETAIL_URL = 'https://slack.com/api/users.info'
    MUTABLE_SLACK_FIELDS = (
        'name',
        'real_name',
    )

    slack_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    real_name = models.CharField(max_length=100)
    joined = models.DateTimeField(default=timezone.now)

    # some meta data which we allow users to modify
    age = models.IntegerField(default=1, blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # TODO remove after we've run the season migration
    elo = models.IntegerField(default=1000)

    # denormalized counts which would be slow to fetch at runtime
    # these are updated in the post_save signal handler
    total_elo = models.IntegerField(default=1000)
    total_win_count = models.IntegerField(default=0)
    total_loss_count = models.IntegerField(default=0)
    total_grannies_given_count = models.IntegerField(default=0)
    total_grannies_taken_count = models.IntegerField(default=0)

    season_elo = models.IntegerField(default=1000)
    season_win_count = models.IntegerField(default=0)
    season_loss_count = models.IntegerField(default=0)
    season_grannies_given_count = models.IntegerField(default=0)
    season_grannies_taken_count = models.IntegerField(default=0)

    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    @property
    def form_cache_key(self):
        return form_cache_key(self)

    def reset_season_fields(self, commit=True):
        """Reset all related fields."""
        self.season_elo = 1000
        self.season_win_count = 0
        self.season_loss_count = 0
        self.season_grannies_given_count = 0
        self.season_grannies_taken_count = 0

        if commit:
            self.save()

    def increment_win_counts(self, commit=True):
        """Increment denormalized win counts."""
        self.total_win_count += 1
        self.season_win_count += 1
        if commit:
            self.save()

    def decrement_win_counts(self, commit=True):
        """Decrement denormalized win counts."""
        self.total_win_count -= 1
        self.season_win_count -= 1
        if commit:
            self.save()

    def increment_loss_counts(self, commit=True):
        """Increment denormalized loss counts."""
        self.total_loss_count += 1
        self.season_loss_count += 1
        if commit:
            self.save()

    def decrement_loss_counts(self, commit=True):
        """Decrement denormalized loss counts."""
        self.total_loss_count -= 1
        self.season_loss_count -= 1
        if commit:
            self.save()

    def increment_grannies_given_counts(self, commit=True):
        self.total_grannies_given_count += 1
        self.season_grannies_given_count += 1
        if commit:
            self.save()

    def increment_grannies_taken_counts(self, commit=True):
        self.total_grannies_taken_count += 1
        self.season_grannies_taken_count += 1
        if commit:
            self.save()

    def increment_elo_score(self, elo_points, commit=True):
        self.total_elo += elo_points
        self.season_elo += elo_points
        if commit:
            self.save()

    def decrement_elo_score(self, elo_points, commit=True):
        self.total_elo -= elo_points
        self.season_elo -= elo_points
        if commit:
            self.save()

    def update_slack_fields(self, auth_token, commit=True):
        """
        Update the mutable slack fields by fetching
        the latest values from the live slack API.
        """
        get_params = urllib.urlencode({
            'token': auth_token,
            'user': self.slack_id,
        })
        url = '{base_url}?{params}'.format(
            base_url=self.SLACK_DETAIL_URL,
            params=get_params
        )

        response = urlfetch.fetch(url, validate_certificate=True)
        data = json.loads(response.content)

        try:
            for field, value in data['user'].iteritems():
                if field in self.MUTABLE_SLACK_FIELDS:
                    setattr(self, field, value)
        except KeyError:
            logging.warn(
                "Unable to get slack info for {}".format(
                    self.pk
                )
            )
        else:
            if commit:
                self.save()

