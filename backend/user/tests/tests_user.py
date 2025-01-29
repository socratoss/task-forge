from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user.models import User


class UserTests(APITestCase):
    fixtures = ['user/tests/fixtures.json']

    def setUp(self):
        self.admin_user = User.objects.get(pk=1)
        self.user_profile_url = reverse('user-profile')

    def test_get_user_profile(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@gmail.com')
        self.assertEqual(response.data['first_name'], 'Admin')
        self.assertEqual(response.data['job_title'], 'System Administrator')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        self.client.force_login(self.admin_user)
        response = self.client.patch(self.user_profile_url, {'first_name': 'NewName'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'NewName')
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, 'NewName')
