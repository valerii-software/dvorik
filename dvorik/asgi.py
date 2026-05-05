"""ASGI config — handles HTTP via Django + WebSockets via Channels."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dvorik.settings')
django_asgi_app = get_asgi_application()  # initialise Django before any app imports

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

import messaging.routing  # noqa: E402
import wall.routing  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            messaging.routing.websocket_urlpatterns
            + wall.routing.websocket_urlpatterns
        ),
    ),
})
