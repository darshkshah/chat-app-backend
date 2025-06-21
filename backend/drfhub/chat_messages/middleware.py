from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import 
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

class DRFAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that uses DRF's JWT Authentication for WebSocket connections.
    """
    def __init__(self, inner):
        super().__init__(inner)
        self.jwt_authenticator = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        if token:
            scope['user'] = await self.get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()


        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            class MockRequest:
                def __init__(self, token):
                    self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
            mock_request = MockRequest(token)
            self.jwt_authenticator.authenticate(mock_request)
            user_auth_tuple = self.jwt_authenticator.authenticate(mock_request)
            if user_auth_tuple is not None:
                user, _ = user_auth_tuple
                return user
        # Add a valid exception from rest_framework.exceptions
        except Exception as e:
            print(e)
            pass

        return AnonymousUser()

