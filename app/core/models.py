

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)

# from django.localflavor.pl.forms import PLPostalCodeField


class UserManager(BaseUserManager):
    '''Manager for users.'''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email adress.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''User in the system.'''
    email = models.EmailField(max_length=255, unique=True)
    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=30)
    data_urodzenia = models.DateField(null=True)
    # kod_poczt = PLPostalCodeField()

    class UserType(models.TextChoices):
        PLAYER = "PL", ("Zawodnik")
        REFEREE = "RE", ("Sędzia")
        VOLUNTEER = "VO", ("Wolontariusz")
        ORGANIZER = "OR", ("Organizator")

    user_type = models.CharField(
        max_length=2,
        choices=UserType,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # REQUIRED_FIELDS = [
    #     'email',
    #     'imie',
    #     'nazwisko',
    #     "data_urodzenia",
    #     'user_type',
    # ]

    objects = UserManager()

    USERNAME_FIELD = 'email'
