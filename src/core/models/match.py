from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .elo_history import EloHistory
from .season import Season


class MatchManager(models.Manager):
    """Custom manager for the Match model."""

    def matches_involving_player(self, player):
        """Return all match instances where the given player was involved."""
        return self.get_queryset().filter(
            Q(winner=player) | Q(loser=player)
        ).order_by('-date')


class Match(models.Model):
    """Documents the result of a pool match between two players."""
    date = models.DateTimeField(default=timezone.now)
    season = models.ForeignKey('core.Season', related_name='matches')
    winner = models.ForeignKey('core.Player', related_name='wins')
    loser = models.ForeignKey('core.Player', related_name='loses')
    channel = models.CharField(max_length=10)
    granny = models.BooleanField(default=False)

    objects = MatchManager()

    def clean(self):
        """Validate the date and season match up."""
        # we could determine the season from the date rather than expect
        # it to be passed in, but this would require we do a query with
        # two ineqaulity filters which the datestore doesn't support...
        # so instead we just validate the two
        if (
            self.date.date() < self.season.start_date or
            self.date.date() > self.season.end_date
        ):
            raise ValidationError('The season does not correspond with date provided.')

    def delete(self):
        # """A match will only be deleted when it was created by mistake.
        # When this happens, due to the high level of denormalization across
        # different models, we need to carefully reset these fields to remove
        # any notion of this match existing."""
        from .season_player import SeasonPlayer

        for player in (self.winner, self.loser):

            # first we need to see how many elo points were won and loss
            # TODO this should be simpler...
            # Maybe the elo points won and lost could be stored on the match?
            match_elo_history = self.elohistory_set.get(player=player)
            previous_elo_history = EloHistory.objects.filter(
                player=player,
                date__lt=match_elo_history.date
            ).order_by('-date').first()

            # this might be their first game of the season...
            previous_elo_history_score = (
                1000 if
                previous_elo_history is None else
                previous_elo_history.elo_score
            )

            # update the denormalized points and counts on player and season player
            if player is self.winner:
                elo_diff = match_elo_history.elo_score - previous_elo_history_score

                # update the denormalized player fields - one less win and less points
                player.decrement_win_counts(commit=False)
                player.decrement_elo_score(elo_diff)

                # update the season player denormalized value
                season_player = SeasonPlayer.objects.get(player=player, season=self.season)
                season_player.undo_win(elo_diff)
            else:
                elo_diff = previous_elo_history_score - match_elo_history.elo_score

                # update the denormalized player fields - one less loss and more points
                player.decrement_loss_counts(commit=False)
                player.increment_elo_score(elo_diff)

                # update the season player denormalized value
                season_player = SeasonPlayer.objects.get(player=player, season=self.season)
                season_player.undo_loss(elo_diff)

            # delete the elo history instance associated with the match
            match_elo_history.delete()

        # delete this instance once out of the loop
        super(Match, self).delete()

    def save(self, *args, **kwargs):
        """Find which season the match should be associated with."""
        # we can only query by one inequality on the datastore...
        self.full_clean()
        return super(Match, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{winner} beat {loser}'.format(
            winner=self.winner,
            loser=self.loser
        )
