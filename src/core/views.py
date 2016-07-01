from django.http import HttpResponse

from google.appengine.ext import deferred

from . import tasks


def resync_player_match_counts(request):
    """Recount all wins and losses for each player and save the denormalized
    values on the player instance.
    """
    deferred.defer(tasks.resync_player_match_counts)
    return HttpResponse('Ok')


def reset_challenge_instances(request):
    """Find all challenger instances which have an initiator or challenger
    set, which were last updated more than ten minutes ago, and set these
    fields to None (we assume the result has not been recorded, or the
    challenge was never accepted by another player.)
    """
    deferred.defer(tasks.reset_challenges)
    return HttpResponse('Ok')

def recalculate_player_elo_ratings(request):
    """Iterate over each match, calculate winner and loser elo rating, and save
    these ratings
    """
    deferred.defer(tasks.recalculate_player_elo_ratings)
    return HttpResponse('Ok')
