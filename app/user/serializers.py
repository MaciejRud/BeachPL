"""
Serializers for the User API View.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializers(serializers.ModelSerializer):
    """Serializers for the user objects."""

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "imie",
            "nazwisko",
            "pesel",
            "user_type",
            "gender",
        ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Creating a new user."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Updating data of user."""
        new_password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if new_password:
            user.set_password(new_password)
            user.save()

        return user


class UserListSerializer(serializers.ModelSerializer):
    """Serializers for the listing users."""

    class Meta:
        model = get_user_model()
        fields = ["id", "imie", "nazwisko", "user_type"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


# class AuthTokenSerializer(serializers.Serializer):
#     '''Serializer for the user auth token.'''
#     email = serializers.EmailField()
#     password = serializers.CharField(
#         style={'input_type': 'password'},
#         trim_whitespace=False,
#     )

#     def validate(self, data):
#         '''Validate and authenticate the user.'''
#         email = data.get('email')
#         password = data.get('password')
#         user = authenticate(
#             username=email,
#             password=password,
#         )

#         if user is None:
#             msg = _('Unable to authenticate with provided credentials.')
#             raise serializers.ValidationError(msg, code='authentication')

#         data['user'] = user
#         return data
