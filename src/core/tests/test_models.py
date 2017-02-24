from datetime import timedelta

from google.appengine.api import memcache

from django.core.exceptions import ValidationError
from django.utils import timezone

from djangae.test import TestCase

from core.models import EloHistory, Match, Season, SeasonPlayer
from core.tests.factories import MatchFactory, SeasonFactory, PlayerFactory
from core.utils import form_cache_key


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

    def test_delete(self):
        """Assert that all of the denormalized fields are reset correctly."""
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        match_one = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season,
            granny=False
        )

        self.process_task_queues()

        # elo points at this point were...
        player_1.refresh_from_db()
        player_2.refresh_from_db()
        winner_elo_original = player_1.total_elo
        loser_elo_original = player_2.total_elo

        # now lets record an incorrect game
        match_two = MatchFactory(
            date=season.start_date + timedelta(days=1),
            winner=player_1,
            loser=player_2,
            season=season,
            granny=False
        )

        self.process_task_queues()

        # find out how many elo points were wrongly won/lost
        player_1.refresh_from_db()
        player_2.refresh_from_db()

        winner_elo_diff = player_1.total_elo - winner_elo_original
        loser_elo_diff = loser_elo_original - player_2.total_elo

        match_two.delete()

        player_1.refresh_from_db()
        player_2.refresh_from_db()

        # check all Player denormalized fields reset
        self.assertEqual(player_1.total_elo, winner_elo_original)
        self.assertEqual(player_1.season_elo, winner_elo_original)
        self.assertEqual(player_1.total_win_count, 1)
        self.assertEqual(player_1.season_win_count, 1)

        self.assertEqual(player_2.total_elo, loser_elo_original)
        self.assertEqual(player_2.season_elo, loser_elo_original)
        self.assertEqual(player_2.total_loss_count, 1)
        self.assertEqual(player_2.season_loss_count, 1)

        # check the season player is updated
        player_1_season_player = SeasonPlayer.objects.get(player=player_1, season=season)
        self.assertEqual(player_1_season_player.elo_score, winner_elo_original)
        self.assertEqual(player_1_season_player.win_count, 1)

        player_2_season_player = SeasonPlayer.objects.get(player=player_2, season=season)
        self.assertEqual(player_2_season_player.elo_score, loser_elo_original)
        self.assertEqual(player_2_season_player.loss_count, 1)

        # the elo history should not longer exist
        with self.assertRaises(EloHistory.DoesNotExist):
            EloHistory.objects.get(match=match_two)

        self.process_task_queues()

        # and the cached form should be destroyed
        for player in (player_1, player_2):
            self.assertEquals(len(memcache.get(player_1.form_cache_key)), 1)


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

        # setting the active season will also put it into memcache
        self.assertEqual(
            season_one,
            memcache.get(Season.ACTIVE_SEASON_CACHE_KEY)
        )

        # trying to create a second season with active=True is not allowed
        with self.assertRaises(ValidationError):
            season_two = SeasonFactory(active=True)

        # and the original season stays in memcache
        self.assertEqual(
            season_one,
            memcache.get(Season.ACTIVE_SEASON_CACHE_KEY)
        )

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

        # setting the active season will also put it into memcache
        self.assertEqual(
            season,
            memcache.get(Season.ACTIVE_SEASON_CACHE_KEY)
        )

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

        # setting the active season will also put it into memcache
        self.assertEqual(
            season,
            memcache.get(Season.ACTIVE_SEASON_CACHE_KEY)
        )

        season.deactivate()

        season.refresh_from_db()
        self.assertFalse(season.active)

        # setting the deactivated season is deleted from the cache
        self.assertIsNone(memcache.get(Season.ACTIVE_SEASON_CACHE_KEY))

    def test_get_active_helper(self):
        # should raise DoesNotExist if no active season
        with self.assertRaises(Season.DoesNotExist):
            Season.objects.get_active()

        # and the correct season if one is active
        active_season = SeasonFactory(active=True)
        inactive_season = SeasonFactory(active=False)

        self.assertEqual(
            active_season,
            Season.objects.get_active()
        )


