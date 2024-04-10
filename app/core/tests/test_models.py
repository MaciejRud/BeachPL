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
            email=mail,
            password=password,
        )

        self.assertEqual(user.email, mail)
        self.assertTrue(user.check_password(password))

    def test_normalizing_email_using_to_create_user(self):
        '''Test of normalizing email used to create user.'''
        sample_mails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]

        for email, expected in sample_mails:
            user = get_user_model().objects.create_user(email, 'Test123')
            self.assertEqual(user.email, expected)

    def test_creating_new_user_without_email(self):
        '''Test creating new user without providing email.'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'Test123')

    def test_creatin_a_superuser(self):
        '''Test creating a superuser.'''

        user = get_user_model().objects.create_superuser(
            'test1@example.com',
            'Test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
