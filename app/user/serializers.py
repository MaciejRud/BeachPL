'''
Serializers for the User API View.
'''
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializers(serializers.ModelSerializer):
    '''Serializers for the user objects.'''

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'imie']
        extra_kwargs = {'password' : {'write_only' : True, 'min_length' : 5}}

    def create(self, validated_data):
        '''Creating a new user.'''
        return get_user_model().objects.create_user(**validated_data)

