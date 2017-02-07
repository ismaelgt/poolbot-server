from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

import session_csrf
session_csrf.monkeypatch()

from django.contrib import admin
admin.autodiscover()

from api.urls import api_router

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'app.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^_ah/', include('djangae.urls')),

    # Note that by default this is also locked down with login:admin in app.yaml
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(include(api_router.urls))),

    url(r'^csp/', include('cspreports.urls')),

    url(r'^auth/', include('djangae.contrib.gauth.urls')),

    url(r'^tasks/', include('core.urls')),

    url(r'^leaderboard/', include('leaderboard.urls')),

)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
