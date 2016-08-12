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
    url(
        '^set-active-flag/',
        'set_active_player_flag',
        name="set_active_player_flag"
    ),
    url(
        '^resync-player-granny-count/',
        'resync_player_granny_counts',
        name="resync_player_granny_count"
    ),
)


urlpatterns = patterns('',
    url(r"^", include(task_patterns)),
)
