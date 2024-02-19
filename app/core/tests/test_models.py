'''
Tests for models.
'''
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    '''Class for testing models.'''

    def test_creating_new_user_with_email_succesfull(self):
        '''Test of creating new user with email succesfull.'''
        mail = 'test123@example.com'
        password = "Test123"
        user = get_user_model().objects.create_user(
            email = mail,
            password = password,
        )

        self.assertEqual(user.email, mail)
        self.assertTrue(user.check_password(password))
