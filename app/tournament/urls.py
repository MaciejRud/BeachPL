"""
URL mapping for tournament APIs.
"""
from django.urls import (
    include,
    path,
)

from rest_framework.routers import DefaultRouter

from tournament import views

router = DefaultRouter()
router.register('tournament', views.TournamentViewSet)

app_name = 'tournament'

urlpatterns = [
    path('', include(router.urls)),
]
