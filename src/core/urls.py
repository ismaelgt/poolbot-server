from django.conf.urls import patterns, include, url


task_patterns = patterns("core.views",
    url(
        '^resync-player-match-counts/',
        'resync_player_match_counts',
        name="resync_player_match_counts"
    ),
)


urlpatterns = patterns('',
    url(r"^", include(task_patterns)),
)
