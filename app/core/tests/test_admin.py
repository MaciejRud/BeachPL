'''
Test for the Django admin modifications.
'''
from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Tournament


class AdminSiteTest(TestCase):
    '''Class for Django admin tests.'''

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="Test123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='TestPass123',
            imie="Test user",
            user_type='OR',
        )
        defaults = {
            'name': 'World Cup',
            'tour_type': 'MA',
            'city': 'Warszawa',
            'money_prize': 15000,
            'sex': "Female",
            'date_of_beginning': "2024-09-10",
            'date_of_finishing': '2024-09-12',
        }
        self.tournament = Tournament.objects.create(user=self.user, **defaults)

    def test_users_list(self):
        '''Test that users are listed on admin site.'''
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.imie)

    def test_edit_user_page(self):
        '''Test of page with editing of user.'''
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        '''Test of page to add new user.'''
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_tournament_list(self):
        '''Test that tournaments are listed on admin site.'''
        url = reverse('admin:core_tournament_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.tournament.user)
        self.assertContains(res, self.tournament.name)

    def test_edit_tournament_page(self):
        '''Test of page with editing of user.'''
        url = reverse('admin:core_tournament_change', args=[self.tournament.id])
        res = self.client.get(url)
        print(Tournament.objects.all())

        self.assertEqual(res.status_code, 200)

    def test_add_tournament_page(self):
        '''Test of page to add new user.'''
        url = reverse('admin:core_tournament_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
