from django.http import HttpResponse

from google.appengine.ext import deferred

from . import tasks


def resync_player_match_counts(request):
    """Recount all wins and losses for each player and save the denormalized
    values on the player instance.
    """
    deferred.defer(tasks.resync_player_match_counts)
    return HttpResponse('Ok')
