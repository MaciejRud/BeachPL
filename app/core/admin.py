"""
Admin site customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin page for users."""

    list_display = (
        "id",
        "imie",
        "email",
        "is_staff",
        "user_type",
        "gender",
        "data_urodzenia",
    )
    ordering = ["id"]

    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets dynamically based on user_type."""
        # Sprawdzamy, czy edytujemy istniejącego użytkownika (obj != None)
        if not obj:
            # Użyj add_fieldsets jeśli nie ma użytkownika.
            return self.add_fieldsets
        # Dla edycji użytkownika (obj != None) używamy fieldsets
        fieldsets = [
            (
                None,
                {
                    "fields": [
                        "imie",
                        "nazwisko",
                        "password",
                    ]
                },
            ),
            (
                "Permissions",
                {
                    "fields": [
                        "is_active",
                        "is_staff",
                        "is_superuser",
                    ]
                },
            ),
            (
                "Additional informations",
                {
                    "fields": [
                        "user_type",
                        "data_urodzenia",
                        "pesel",
                        "last_login",
                    ]
                },
            ),
        ]
        if obj.user_type == "PL":
            # Dodanie dodatkowych pól dla graczy
            fieldsets.append(
                (
                    "Additional information",
                    {
                        "fields": [
                            "data_urodzenia",
                            "points",
                            "gender",
                        ]
                    },
                )
            )

        return fieldsets

    readonly_fields = ["last_login"]
    add_fieldsets = [
        (
            None,
            {
                "classes": [
                    "wide",
                    "cascade",
                ],
                "fields": [
                    "email",
                    "password1",
                    "password2",
                    "imie",
                    "nazwisko",
                    "user_type",
                    "pesel",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ],
            },
        ),
    ]

    list_filter = ["user_type", "is_staff", "is_superuser", "is_active"]


class TournamentAdmin(admin.ModelAdmin):
    """Define the admin page for tournaments."""

    list_display = (
        "name",
        "user",
        "tour_type",
        "city",
        "money_prize",
        "sex",
        "date_of_beginning",
        "date_of_finishing",
    )
    ordering = ["date_of_beginning"]
    search_fields = ["name", "city", "user__email"]
    list_filter = ["tour_type", "sex"]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tournament, TournamentAdmin)
