from django.conf.urls import patterns, url


urlpatterns = patterns(
    "leaderboard.views",
    url(
        r'api/$',
        'api',
        name="leaderboard-api"
    ),
    url(
        r'',
        LeaderboardIndex.as_view(),
        name="leaderboard-index"
    ),
)
