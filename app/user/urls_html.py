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
]
