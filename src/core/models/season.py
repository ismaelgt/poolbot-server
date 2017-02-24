from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from google.appengine.api import memcache

from player import Player


ACTIVE_SEASON_CACHE_KEY = 'season__active'


class SeasonManager(models.Manager):
    """Custom manager for the Season model."""

    def get_active(self):
        """
        Find the currently active season, first by looking in memcache
        and then performing a DB query. If no active instance is found,
        raise a DoesNotExist exception like a vanilla `get` query would.
        """
        active_season = memcache.get(ACTIVE_SEASON_CACHE_KEY)
        if active_season is None:
            # this will raise a Season.DoesNotExist exception if no result
            active_season = self.get_queryset().get(active=True)
            memcache.set(ACTIVE_SEASON_CACHE_KEY, active_season)

        return active_season


class Season(models.Model):
    """Defines a duration of time during which players play pool matches."""
    ACTIVE_SEASON_CACHE_KEY = ACTIVE_SEASON_CACHE_KEY

    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

    objects = SeasonManager()

    def clean(self):
        """Perform some field level validation on the two date fields."""

        # validate date_must is before end_date
        if self.start_date > self.end_date:
            raise ValidationError('The end date must be greater than the start date.')

        # validate only one active season at a time is permitted
        if self.active:
            try:
                active_season = Season.objects.get(active=True)
            except Season.DoesNotExist:
                # when we're all good - this active=True is unique
                pass
            else:
                if self != active_season:
                    raise ValidationError(
                        '{} is already set as the active season.'.format(active_season.pk)
                    )

        # TODO make sure no other season overlaps this one

    def activate(self, commit=True):
        """
        Mark the instance as active and as a bi-product reset all denormalized season
        fields on player objects.
        """
        self.active = True
        if commit:
            self.save()

        # now we have a new season, we need to reset all the previous counts
        for player in Player.objects.all():
            player.reset_season_fields()

    def deactivate(self, commit=True):
        """Mark the instance as inactive and make sure the top five are set."""
        self.active = False

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        """Always perform date field validation."""
        self.full_clean()
        super(Season, self).save(*args, **kwargs)

        # if the season is active at this point we know it must be the only
        # instance which satisfies this criteria, so we can create/update cache
        if self.active:
            memcache.set(ACTIVE_SEASON_CACHE_KEY, self)
        else:
            # double check the inactive season is not in the cache
            cached_active_season = memcache.get(ACTIVE_SEASON_CACHE_KEY)
            if cached_active_season == self:
                memcache.delete(ACTIVE_SEASON_CACHE_KEY)
