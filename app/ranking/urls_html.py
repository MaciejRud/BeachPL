'''
URL mapping for ranking templates.
'''

from django.urls import (
    path,
)

from ranking import views

urlpatterns = [
    path('ranking/', views.RankingTemplateViewSet.as_view(),
         name='ranking'),
]
