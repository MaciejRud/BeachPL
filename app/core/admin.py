'''
Admin site customization.
'''

from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.request import HttpRequest

from core import models


class UserAdmin(BaseUserAdmin):
    '''Define the admin page for users.'''
    list_display = ('id', 'imie', 'email', 'is_staff',)
    ordering = ['id']

    def get_fieldsets(self, request, obj=None):
        '''Customize fieldsets dynamically based on user_type.'''
        fieldsets = [
            (
                None,
                {
                    'fields': ['imie', 'nazwisko', 'password',]
                },
            ),
            (
                'Permissions',
                {
                    'fields': ['is_active', 'is_staff', 'is_superuser',]
                }
            ),
            (
                'Additional informations',
                {
                    'fields': ['user_type', 'data_urodzenia',
                            'pesel', 'last_login',]
                }
            ),
        ]
        if obj and obj.user_type == 'player':
                # Additional fields for players
                fieldsets.append(
                    (
                        None,
                        {
                            'fields': ['data_urodzenia']
                        },
                        'Punkty',
                        {
                            'fields': ['points']
                        },
                    )
                )

        return fieldsets

    readonly_fields = ['last_login']
    add_fieldsets = [
        (
            None,
            {
                'classes': ["wide", 'cascade',],
                'fields': [
                    'email',
                    'password1',
                    'password2',
                    'imie',
                    'nazwisko',
                    'user_type',
                    'pesel',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ]
            }
        ),
    ]

    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_active']

class TournamentAdmin(admin.ModelAdmin):
    '''Define the admin page for tournaments.'''
    list_display = ('name', 'user', 'tour_type',
                    'city', 'money_prize', 'sex',
                    'date_of_beginning', 'date_of_finishing')
    ordering = ['date_of_beginning']
    search_fields = ['name', 'city', 'user__email']
    list_filter = ['tour_type', 'sex']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tournament, TournamentAdmin)
