'''
Database models.
'''

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from django.core.exceptions import ValidationError

from django.utils.translation import gettext as _

import re

# from django.localflavor.pl.forms import PLPostalCodeField


def validate_pesel(value):
    '''Validates a PESEL number.'''
    if value == " " or not re.match(r'^\d{11}$', value):
        msg = _("Pesel must be an 11-digit number.")
        raise ValidationError(msg)


class UserManager(BaseUserManager):
    '''Manager for users.'''
    def create_user(self, email, password=None, **extra_fields):
        '''Create, save and return an user.'''
        if not email:
            raise ValueError("User must have an email adress.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        '''Create, save and return a superuser.'''
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
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

    pesel = models.CharField(max_length=11, null=True, blank=True,
                             validators=[validate_pesel])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tournament(models.Model):
    '''Tournament object.'''

    class TourType(models.TextChoices):
        SENIOR = "SR", ("Seniorski")
        JUNIOR = "JR", ("Juniorski")
        MASTER = "MA", ("Master")

    class Sex(models.TextChoices):
        MALE = "MALE", ("Męski")
        FEMALE = "FEMALE", ("Żeński")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
    date_of_beginning = models.DateField()
    date_of_finishing = models.DateField()

    def __str__(self):
        return self.name
