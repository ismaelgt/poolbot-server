import logging

from decorator import decorator
from django.http import HttpResponse
from django.conf import settings


@decorator
def ip_authorization(func, *args, **kwargs):
    request = args[0]
    request_ip = request.META['REMOTE_ADDR']
    if request_ip in settings.AUTHORISED_LEADERBOARD_IPS:
        return func(*args, **kwargs)
    else:
        logging.info('Leaderboard request received form unrecognised IP {}'.format(request_ip))
        return HttpResponse(status=401)
