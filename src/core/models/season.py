from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from player import Player


class Season(models.Model):
    """Defines a duration of time during which players play pool matches."""

    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)

    first_place = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    second_place = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    third_place = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    forth_place = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')
    fifth_place = models.ForeignKey('core.Player', blank=True, null=True, related_name='+')

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
        self.set_top_five_players(commit=False)
        self.active = False

        if commit:
            self.save()

    def set_top_five_players(self, commit=True):
        """
        Based on their elo points, get the top five from the leaderboard. To
        try and prevent this using the wrong seasons denormalized scores, the
        season must be active at the time this is called.
        """
        if not self.active:
            # TODO have a fallback that does not rely on the denormalized counts
            raise Exception('Cannot set top five if season not active.')

        top_five = Player.objects.filter(active=True).order_by('-season_elo')[:5]
        top_five_fields = [
            'first_place',
            'second_place',
            'third_place',
            'forth_place',
            'fifth_place',
        ]
        for player, field in zip(top_five, top_five_fields):
            setattr(self, field, player)

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        """Always perform date field validation."""
        self.full_clean()
        return super(Season, self).save(*args, **kwargs)
