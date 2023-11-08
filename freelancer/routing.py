from django.urls import path
from chat.consumers import ChatConsumer
from chat.middleware import WebSocketAuthMiddleware

websocket_urlpatterns = [
    path("<conversation_name>",ChatConsumer.as_asgi())
]
