from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from player import Player


class Season(models.Model):
    """Defines a duration of time during which players play pool matches."""

    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

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
                pass # when we're all good - this active=True is unique
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
        return super(Season, self).save(*args, **kwargs)
