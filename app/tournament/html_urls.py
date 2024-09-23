'''
URL mapping for tournament HTML templates.
'''

from django.urls import (
    path,
)

from tournament import views

urlpatterns = [
    path('list/', views.TournamentListView.as_view(),
         name='tournament-list'),
    path('details/<int:id>/', views.DetailedTournamentView.as_view(),
         name='public-tournament-detail')
]
