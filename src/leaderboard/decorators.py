import logging

from decorator import decorator
from django.http import HttpResponse
from django.conf import settings


@decorator
def ip_authorization(func, *args, **kwargs):
    """Limit requests to whitelised IP addresses if configured."""
    if not settings.AUTHORISED_LEADERBOARD_IPS:
        logging.warning(
            'No AUTHORISED_LEADERBOARD_IPS defined, board is publicly viewable')
        return

    request = args[0]
    request_ip = request.META['REMOTE_ADDR']
    if request_ip in settings.AUTHORISED_LEADERBOARD_IPS:
        return func(*args, **kwargs)
    else:
        logging.error(
            'Leaderboard request received from unrecognised IP {} not in {}'.format(
                request_ip,
                settings.AUTHORISED_LEADERBOARD_IPS,
            )
        )
        return HttpResponse(status=401)
