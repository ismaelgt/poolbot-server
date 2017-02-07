from django.conf.urls import patterns, url


urlpatterns = patterns(
    "leaderboard.views",
    url(
        r'api/$',
        'api',
        name="leaderboard"
    ),
    url(
        r'',
        'index',
        name="leaderboard"
    ),
)
