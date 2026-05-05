from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    re_path(
        r'^ws/wall/(?P<kind>user|group)/(?P<target_id>\d+)/$',
        consumers.WallConsumer.as_asgi(),
    ),
]
