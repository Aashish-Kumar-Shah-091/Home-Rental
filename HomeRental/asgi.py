import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HomeRental.settings")

from django.core.asgi import get_asgi_application

# Initialize Django ASGI app early so the app registry is fully loaded
# before importing modules that touch models.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(chat.routing.websocket_urlpatterns)
        ),
    }
)
