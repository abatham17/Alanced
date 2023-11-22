# middleware.py
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

@database_sync_to_async
def get_user(scope):
    # Get the user from the scope, e.g., from a session or token
    user = None  # Implement your authentication logic here
    return user

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope['user'] = await get_user(scope)
        print("scope ========== > ",scope['user'])
        return await super().__call__(scope, receive, send)
