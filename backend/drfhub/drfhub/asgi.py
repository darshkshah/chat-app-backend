"""
ASGI config for drfhub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat_messages.middleware import DRFAuthMiddleware

import chat_messages.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drfhub.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': DRFAuthMiddleware(
        URLRouter(chat_messages.routing.websocket_urlpatterns),
    )
})
