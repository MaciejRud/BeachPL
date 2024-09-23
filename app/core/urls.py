"""
URLs for home page.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Inne ścieżki URL
]
