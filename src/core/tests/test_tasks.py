from datetime import timedelta
from mock import patch

from django.core.exceptions import ValidationError
from django.utils import timezone

from djangae.test import TestCase

from core.models import Match, Season
from core.tests.factories import MatchFactory, SeasonFactory, PlayerFactory
from core.tasks import set_active_season


class SetActiveSeasonTestCase(TestCase):
    """Tests for the task which sets a season as active."""

    def test_expired_active_season_marked_inactive(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        earlier = yesterday - timedelta(days=10)
        season = SeasonFactory(
            start_date=earlier, end_date=yesterday, active=True
        )

        set_active_season()

        season.refresh_from_db()
        self.assertFalse(season.active)

    def test_ongoing_season_remains_active(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        season = SeasonFactory(start_date=yesterday, active=True)

        set_active_season()

        season.refresh_from_db()
        self.assertTrue(season.active)

    def test_new_season_activated(self):
        today = timezone.now().date()
        season = SeasonFactory(start_date=today)
        self.assertFalse(season.active)

        player = PlayerFactory(
            season_elo = 2000,
            season_win_count = 50,
            season_loss_count = 10,
            season_grannies_given_count = 5,
            season_grannies_taken_count = 2,
        )

        set_active_season()

        season.refresh_from_db()
        self.assertTrue(season.active)

        # as a bi-product of marking a new season as active
        # all season fields on the player instances are reset
        player.refresh_from_db()
        self.assertEqual(player.season_elo, 1000)
        self.assertFalse(player.season_win_count)
        self.assertFalse(player.season_loss_count)
        self.assertFalse(player.season_grannies_given_count)
        self.assertFalse(player.season_grannies_taken_count)
