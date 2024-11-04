"""
Database models.
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _

import re


def validate_pesel(value):
    """Validates a PESEL number."""
    if value == " " or not re.match(r"^\d{11}$", value):
        msg = _("Pesel must be an 11-digit number.")
        raise ValidationError(msg)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return an user."""
        if not email:
            raise ValueError("User must have an email adress.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create, save and return a superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=30)
    data_urodzenia = models.DateField(null=True, blank=True)

    class UserType(models.TextChoices):
        PLAYER = "PL", ("Zawodnik")
        ORGANIZER = "OR", ("Organizator")

    user_type = models.CharField(
        max_length=2,
        choices=UserType,
    )

    class Gender(models.TextChoices):
        MALE = "MALE", ("Męski")
        FEMALE = "FEMALE", ("Żeński")

    gender = models.CharField(
        max_length=6,
        choices=Gender.choices,
    )

    pesel = models.CharField(
        max_length=11, null=True, blank=True, validators=[validate_pesel]
    )
    tournament_points = models.JSONField(
        default=dict, blank=True
    )  # Przechowuj punkty za turnieje
    total_points = models.IntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def is_organizer(self):
        return self.user_type == self.UserType.ORGANIZER

    def is_player(self):
        return self.user_type == self.UserType.PLAYER

    def tournaments(self):
        if self.is_organizer():
            return Tournament.objects.filter(user=self)
        elif self.is_player():
            return Tournament.objects.filter(teams__in=self.teams.all())
        return []

    def __str__(self):
        if self.is_organizer():
            return f"Organizer {self.imie} {self.nazwisko}"
        elif self.is_player():
            return f"Player {self.imie} {self.nazwisko}"
        return "Unknown User Type"


class Team(models.Model):
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams")

    def clean(self):
        super().clean()
        if self.players.count() != 2:
            raise ValidationError("A team must have exactly 2 players.")

    def __str__(self):
        # Pobieramy listę zawodników przypisanych do drużyny, posortowaną po ID
        player_list = self.players.all().order_by("id")
        # Sprawdzamy, czy drużyna ma dokładnie dwóch zawodników
        if player_list.count() == 2:
            # Zakładamy, że zawodnicy mają atrybuty imie i nazwisko
            player1 = player_list[0]
            player2 = player_list[1]
            return (
                f"{player1.imie} {player1.nazwisko} & {player2.imie} {player2.nazwisko}"
            )
        return "Team with insufficient players"


class Tournament(models.Model):
    """Tournament object."""

    class TourType(models.TextChoices):
        SENIOR = "SR", ("Seniorski")
        JUNIOR = "JR", ("Juniorski")
        MASTER = "MA", ("Master")

    class Sex(models.TextChoices):
        MALE = "MALE", ("Męski")
        FEMALE = "FEMALE", ("Żeński")

    class RankingType(models.TextChoices):
        NONRANKING = "NoneRank", ("Bezrankingowy")
        ONESTAR = "OneStar", ("1 gwiazdka")
        TWOSTARS = "TwoStars", ("2 gwiazdki")
        TRHEESTARS = "ThreeStars", ("3 gwiazdki")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tournaments",
    )
    name = models.CharField(max_length=50)
    tour_type = models.CharField(
        max_length=2,
        choices=TourType,
    )
    city = models.CharField(max_length=30)
    money_prize = models.IntegerField()
    sex = models.CharField(
        choices=Sex,
    )
    ranking_type = models.CharField(
        choices=RankingType,
        default=RankingType.NONRANKING,
    )
    date_of_beginning = models.DateField()
    date_of_finishing = models.DateField()

    teams = models.ManyToManyField(
        Team,
        related_name="tournaments",
    )

    def __str__(self):
        return self.name


class PlayerTournamentResult(models.Model):
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tournament_results"
    )
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="player_results"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="player_results"
    )
    points_awarded = models.PositiveIntegerField()  # Punkty za dany turniej
    position = models.PositiveIntegerField()  # Miejsce w turnieju
    tournament_date = models.DateField()  # Data zakończenia turnieju
    created_at = models.DateTimeField(auto_now_add=True)


class Ranking(models.Model):
    date = models.DateField()  # Data generacji rankingu
    gender = models.CharField(max_length=6, choices=User.Gender.choices)  # Płeć
    rankings = models.JSONField()  # Słownik przechowujący ranking (np. {1: {'user_id': user_id, 'points': points}, ...})
