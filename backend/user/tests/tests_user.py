from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user.models import User


class UserTests(APITestCase):
    fixtures = ['user/tests/fixtures.json']

    def setUp(self):
        self.admin_user = User.objects.get(pk=1)
        self.user_profile_url = reverse('user-profile')

    def test_get_current_user(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@gmail.com')
        self.assertEqual(response.data['first_name'], 'Admin')
        self.assertEqual(response.data['job_title'], 'System Administrator')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_patch(self):
        self.client.force_login(self.admin_user)
        response = self.client.patch(self.user_profile_url, {'first_name': 'NewName'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, 'NewName')

    def test_update_user_profile_put(self):
        self.client.force_login(self.admin_user)
        response = self.client.put(self.user_profile_url, {
            'username': 'admin@gmail.com',
            'first_name': 'NewName',
            'last_name': '',
            'is_staff': True,
            'is_active': True,
            'email': 'admin@gmail.com',
            'job_title': 'Updated Job',
            'profile_picture': ''
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'admin@gmail.com')
        self.assertEqual(self.admin_user.first_name, 'NewName')
        self.assertEqual(self.admin_user.last_name, '')
        self.assertEqual(self.admin_user.is_staff, True)
        self.assertEqual(self.admin_user.is_active, True)
        self.assertEqual(self.admin_user.job_title, 'Updated Job')
        self.assertEqual(self.admin_user.profile_picture, '')
