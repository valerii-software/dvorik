from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
