"""
URL mapping for the user API.
"""
from django.urls import path
from user.views import PlayerListView
from django.contrib.auth import views as auth_views

from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('players/', PlayerListView.as_view(), name='player-list'),
    path('login/', views.CustomLoginView.as_view(), name='custom-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
