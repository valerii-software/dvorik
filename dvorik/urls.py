from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path

from . import media_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('profiles:my_page') if r.user.is_authenticated
         else redirect('accounts:login')),
    path('accounts/', include('accounts.urls')),
    path('id/', include('profiles.urls')),
    path('friends/', include('friends.urls')),
    path('wall/', include('wall.urls')),
    path('messages/', include('messaging.urls')),
    path('photos/', include('photos.urls')),
    path('audio/', include('audio.urls')),
    path('video/', include('video.urls')),
    path('groups/', include('groups.urls')),
    path('feed/', include('feed.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.+)$', media_views.serve_media),
    ]

handler404 = 'dvorik.views.handler404'
handler500 = 'dvorik.views.handler500'
handler403 = 'dvorik.views.handler403'
