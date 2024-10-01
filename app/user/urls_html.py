'''
URL mapping for user HTML templates.
'''

from django.urls import (
    path,
)

from . import views

urlpatterns = [
    path('create-user/', views.CreateUserTemplate.as_view(),
         name='create-user'),
    path('organizer-zone/', views.OrganizerZoneTemplate.as_view(),
         name='organizer-zone'),
    path('player-zone/', views.PlayerZoneTemplate.as_view(),
         name='player-zone'),
]
