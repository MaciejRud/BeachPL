"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.views.generic import TemplateView

from core.models import User

from user.serializers import (
    UserSerializers,
    AuthTokenSerializer,
    UserListSerializer
)


class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system.'''
    serializer_class = UserSerializers

class PlayerListView(generics.ListAPIView):
    '''View to list users being players.'''
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only users with user_type 'PL'
        return User.objects.filter(user_type='PL')


class CreateTokenView(ObtainAuthToken):
    '''Create a auth token for user.'''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage the authenticated user.'''
    serializer_class = UserSerializers
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Retrieve and return the authenticated user.'''
        return self.request.user


class CreateUserTemplate(TemplateView):
    template_name = 'user/register.html'
