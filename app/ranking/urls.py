"""
URLs for ranking API.
"""

from django.urls import (
    include,
    path,
)

from rest_framework.routers import DefaultRouter

from ranking import views

router = DefaultRouter()
router.register("ranking", views.RankingViewSet, basename="ranking")

app_name = "ranking"

urlpatterns = [
    path("", include(router.urls)),
]
