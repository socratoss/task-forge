from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user.models import User


class AuthenticationTests(APITestCase):
    fixtures = ['user/tests/fixtures.json']

    def setUp(self):
        self.admin_user = User.objects.get(pk=1)
        self.user_profile_url = reverse('user-profile')

        self.login_url = reverse('rest_login')
        self.logout_url = reverse('rest_logout')
        self.password_reset_url = reverse('rest_password_reset')
        self.password_change_url = reverse('rest_password_change')
        self.signup_url = reverse('rest_register')

    def test_login(self):
        response = self.client.post(self.login_url, {'username': 'admin@gmail.com', 'password': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_logout(self):
        self.client.login(username='admin@gmail.com', password='admin')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        response = self.client.post(self.password_reset_url, {'email': 'admin@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change(self):
        self.client.login(username='admin@gmail.com', password='admin')
        response = self.client.post(self.password_change_url, {
            'old_password': 'admin',
            'new_password1': 'admin12345',
            'new_password2': 'admin12345',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signup(self):
        response = self.client.post(self.signup_url, {
            'username': 'example@gmail.com',
            'email': 'example@gmail.com',
            'password1': 'admin12345',
            'password2': 'admin12345'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

