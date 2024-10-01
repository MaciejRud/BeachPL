"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)

from core.models import User

from user.serializers import (
    UserSerializers,
    UserListSerializer,
    LoginSerializer,
)


class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system.'''
    serializer_class = UserSerializers
    permission_classes = [permissions.AllowAny]

class PlayerListView(generics.ListAPIView):
    '''View to list users being players.'''
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the current logged-in user
        current_user = self.request.user

        # Return players excluding the current user
        return User.objects.filter(user_type='PL').exclude(id=current_user.id)


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage the authenticated user.'''
    serializer_class = UserSerializers
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Retrieve and return the authenticated user.'''
        if not self.request.user.is_authenticated:
            logger.warning("Unauthorized access attempt.")
        return self.request.user


class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        logger.debug(f'Email: {email}, Password: {password}')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Logged in successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)



class CreateUserTemplate(TemplateView):
    template_name = 'user/register.html'


class OrganizerZoneTemplate(TemplateView):
    template_name = 'user/organizer-zone.html'


class PlayerZoneTemplate(TemplateView):
    template_name = 'user/player-zone.html'
