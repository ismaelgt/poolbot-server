from datetime import timedelta

from core.models import Match, Season
from core.tests.factories import MatchFactory, SeasonFactory

from djangae.test import TestCase


class MatchModelTestCase(TestCase):
    """Tests for the match model."""

    def test_correct_season_used(self):
        """
        Assert the logic which assigns a season FK based on the date values
        provided is correct.
        """
        today = timezone.now().date

        old_season = SeasonFactory(
            start_date=today - timedelta(months=3),
            end_date=today - timedelta(months=2),
            active=False,
        )
        current_season = SeasonFactory(
            start_date=today - timedelta(months=1),
            end_date=today + timedelta(months=2),
            active=True,
        )
        forthcoming_season = SeasonFactory(
            start_date=today + timedelta(months=3),
            end_date= today + timedelta(months=4),
            active=False,
        )

        # match uses auto_now_add for the date field
        match = MatchFactory()
        self.assertEqual(match.season, current_season)


class SeasonModelTestCase(TestCase):
    """Tests for the season model."""

    def test_end_date_must_be_greater_than_start_date(self):

