from django.db import models
from django.utils import timezone

from . import Season


class SeasonPlayerManager(models.Manager):

    def update_active(self, player, elo, wins, losses):
        """Update or create the season player instance for the active season."""
        active_season = Season.objects.get_active()

        updated_values = {
            'player': player,
            'season': active_season,
            'elo_score': elo,
            'win_count': wins,
            'loss_count': losses
        }
        SeasonPlayer.objects.update_or_create(player=player, season=active_season, defaults=updated_values)

    def get_winner(self, season):
        """Returns the player with the most elo points for the given season."""
        return (
            self.get_queryset()
                .filter(season=season)
                .order_by('-elo_score')
                .first()
        )


class SeasonPlayer(models.Model):
    """Denormalized representation of a player for a particular season."""

    # FK relationships to other models
    player = models.ForeignKey('core.Player')
    season = models.ForeignKey('core.Season')

    # denormalized counts and elo score
    elo_score = models.IntegerField(blank=True)
    win_count = models.IntegerField(blank=True)
    loss_count = models.IntegerField(blank=True)

    objects = SeasonPlayerManager()

    def __unicode__(self):
        return "{player} during {season} season".format(
            player=self.player,
            season=self.season
        )

    def undo_win(self, elo_points, commit=True):
        self.elo_score -= elo_points
        self.win_count -= 1
        if commit:
            self.save()

    def undo_loss(self, elo_points, commit=True):
        self.elo_score += elo_points
        self.loss_count -= 1
        if commit:
            self.save()
