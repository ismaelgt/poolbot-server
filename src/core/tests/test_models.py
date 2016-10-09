from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from djangae.test import TestCase

from core.models import Match, Season
from core.tests.factories import MatchFactory, SeasonFactory, PlayerFactory


class MatchModelTestCase(TestCase):
    """Tests for the match model."""

    def test_correct_season_used(self):
        """
        Assert the logic which assigns a season FK based on the date values
        provided is correct.
        """
        today = timezone.now().date()

        old_season = SeasonFactory(
            start_date=today - timedelta(days=3),
            end_date=today - timedelta(days=2),
            active=False,
        )
        current_season = SeasonFactory(
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=2),
            active=True,
        )
        forthcoming_season = SeasonFactory(
            start_date=today + timedelta(days=3),
            end_date= today + timedelta(days=4),
            active=False,
        )

        # match uses timezone.now for the date field default
        with self.assertRaises(ValidationError):
            match = MatchFactory(season=old_season)

        with self.assertRaises(ValidationError):
            match = MatchFactory(season=forthcoming_season)

        match = MatchFactory(season=current_season)
        self.assertEqual(match.season, current_season)

class SeasonModelTestCase(TestCase):
    """Tests for the season model."""

    def test_end_date_must_be_greater_than_start_date(self):
        today = timezone.now().date()

        with self.assertRaises(ValidationError):
            season = SeasonFactory(
                start_date=today,
                end_date=today - timedelta(days=1)
            )

    def test_only_one_active_season_permitted(self):
        season_one = SeasonFactory(active=True)
        self.assertTrue(season_one.active)

        # trying to create a second season with active=True is not allowed
        with self.assertRaises(ValidationError):
            season_two = SeasonFactory(active=True)

        # sanity check you can modify other values when the active flag is
        # set, and the validation does not mistakenly think another active 
        # season exists
        season_one.start_date = season_one.start_date + timedelta(days=1)
        season_one.save()

    def test_activate(self):
        season = SeasonFactory(active=False)
        self.assertFalse(season.active)

        player = PlayerFactory(
            season_elo = 2000,
            season_win_count = 50,
            season_loss_count = 10,
            season_grannies_given_count = 5,
            season_grannies_taken_count = 2,
        )

        season.activate()

        season.refresh_from_db()
        self.assertTrue(season.active)
        
        player.refresh_from_db()
        self.assertEqual(player.season_elo, 1000)
        self.assertFalse(player.season_win_count)
        self.assertFalse(player.season_loss_count)
        self.assertFalse(player.season_grannies_given_count)
        self.assertFalse(player.season_grannies_taken_count)

    def test_deactivate(self):
        season = SeasonFactory(active=True)
        self.assertTrue(season.active)

        season.deactivate()

        season.refresh_from_db()
        self.assertFalse(season.active)


