from django.conf.urls import patterns, include, url


task_patterns = patterns("core.views",
    url(
        '^resync-player-match-counts/',
        'resync_player_match_counts',
        name="resync_player_match_counts"
    ),
    url(
        '^reset-challenges/',
        'reset_challenge_instances',
        name="reset_challenge_instances"
    ),
    url(
        '^recalculate-elo/',
        'recalculate_player_elo_ratings',
        name="recalculate_player_elo_ratings"
    ),
)


urlpatterns = patterns('',
    url(r"^", include(task_patterns)),
)
