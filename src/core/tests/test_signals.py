from djangae.test import TestCase

from core.models import Match, Season
from core.tests.factories import MatchFactory, SeasonFactory, PlayerFactory


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

        # the top five should also be updated
        season.refresh_from_db()
        self.assertEqual(season.first_place, player_1)
        self.assertEqual(season.second_place, player_2)
