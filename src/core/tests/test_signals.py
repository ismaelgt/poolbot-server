from djangae.test import TestCase

from core.models import Match, Season, SeasonPlayer, EloHistory
from core.tests.factories import (
    MatchFactory,
    SeasonFactory,
    PlayerFactory,
    SeasonPlayerFactory,
)


class MatchPostSaveSignalTestCase(TestCase):
    """
    Tests associated with any reciever linked to the Match model
    post save signal.
    """

    def test_update_elo_ratings(self):
        """Tests for the `update_elo_ratings` reciever."""
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        p1_cached_total_elo = player_1.total_elo
        p1_cached_season_elo = player_1.season_elo
        p2_cached_total_elo = player_2.total_elo
        p2_cached_season_elo = player_2.season_elo

        match = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season
        )

        player_1.refresh_from_db()
        player_2.refresh_from_db()

        self.assertNotEqual(player_1.total_elo, p1_cached_total_elo)
        self.assertNotEqual(player_1.season_elo, p1_cached_season_elo)
        self.assertEqual(player_1.total_elo, player_1.season_elo)

        self.assertNotEqual(player_2.total_elo, p2_cached_total_elo)
        self.assertNotEqual(player_2.season_elo, p2_cached_season_elo)
        self.assertEqual(player_2.total_elo, player_2.season_elo)

    def test_grannies_recorded(self):
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        match = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season,
            granny=True
        )

        player_1.refresh_from_db()
        self.assertEqual(player_1.total_grannies_given_count, 1)
        self.assertEqual(player_1.season_grannies_given_count, 1)

        player_2.refresh_from_db()
        self.assertEqual(player_2.total_grannies_taken_count, 1)
        self.assertEqual(player_2.season_grannies_taken_count, 1)

    def test_season_player_updated(self):
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        player_season_1 = SeasonPlayerFactory(player=player_1, season=season)
        player_season_2 = SeasonPlayerFactory(player=player_2, season=season)

        match = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season,
            granny=True
        )

        self.process_task_queues()

        player_1.refresh_from_db()
        player_season_1.refresh_from_db()
        self.assertEqual(player_1.season_elo, player_season_1.elo_score)
        self.assertEqual(player_1.season_win_count, player_season_1.win_count)
        self.assertEqual(player_1.season_loss_count, player_season_1.loss_count)

        player_2.refresh_from_db()
        player_season_2.refresh_from_db()
        self.assertEqual(player_2.season_elo, player_season_2.elo_score)
        self.assertEqual(player_2.season_win_count, player_season_2.win_count)
        self.assertEqual(player_2.season_loss_count, player_season_2.loss_count)

    def test_season_player_created(self):
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        match = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season,
            granny=True
        )

        self.process_task_queues()

        player_1.refresh_from_db()
        player_season_1 = SeasonPlayer.objects.get(player=player_1)

        self.assertEqual(player_season_1.season, season)
        self.assertEqual(player_1.season_elo, player_season_1.elo_score)
        self.assertEqual(player_1.season_win_count, player_season_1.win_count)
        self.assertEqual(player_1.season_loss_count, player_season_1.loss_count)

        player_2.refresh_from_db()
        player_season_2 = SeasonPlayer.objects.get(player=player_2)

        self.assertEqual(player_season_2.season, season)
        self.assertEqual(player_2.season_elo, player_season_2.elo_score)
        self.assertEqual(player_2.season_win_count, player_season_2.win_count)
        self.assertEqual(player_2.season_loss_count, player_season_2.loss_count)

    def test_elo_history_created(self):
        season = SeasonFactory(active=True)

        player_1 = PlayerFactory(active=True)
        player_2 = PlayerFactory(active=True)

        match = MatchFactory(
            date=season.start_date,
            winner=player_1,
            loser=player_2,
            season=season,
            granny=True
        )

        player_1.refresh_from_db()
        player1_elo_history = EloHistory.objects.get(player=player_1)
        self.assertEqual(match, player1_elo_history.match)
        self.assertEqual(season, player1_elo_history.season)
        self.assertEqual(player_1.season_elo, player1_elo_history.elo_score)

        player_1.refresh_from_db()
        player2_elo_history = EloHistory.objects.get(player=player_2)
        self.assertEqual(match, player2_elo_history.match)
        self.assertEqual(season, player2_elo_history.season)
        self.assertEqual(player_2.season_elo, player2_elo_history.elo_score)
