'''
Admin site customization.
'''

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models


class UserAdmin(BaseUserAdmin):
    '''Define the admin page for users.'''
    list_display = ('id', 'imie', 'email', 'is_staff',)
    ordering = ['id']
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
                    'data_urodzenia',
                    'user_type',
                    'pesel',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ]
            }
        ),
    ]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tournament)
