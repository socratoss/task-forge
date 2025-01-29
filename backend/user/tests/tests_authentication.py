import re
from django.contrib.auth import authenticate
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from django.core import mail
from user.models import User


def extract_reset_tokens(url):
    regex_pattern = r'/password/reset/confirm/(?P<uidb64>[a-zA-Z0-9_-]+)/(?P<token>[a-zA-Z0-9_-]+)'
    match = re.search(regex_pattern, url)
    if match:
        return match.group('uidb64'), match.group('token')
    return None, None


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

    def test_login_success(self):
        response = self.client.post(self.login_url, {'username': 'fbetter777@gmail.com', 'password': 'Spoon78Fw_'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {'username': 'fbetter777@gmail.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {'username': 'invalid@gmail.com', 'password': 'Spoon78Fw_'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    def test_password_reset(self):
        response = self.client.post(self.password_reset_url, {'email': 'fbetter777@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response.data['detail'], 'Password reset e-mail has been sent.')

    def test_password_reset_confirm(self):
        old_password = 'Spoon78Fw_'
        new_password = 'NewSecurePass123!'

        self.client.post(self.password_reset_url, {'email': 'fbetter777@gmail.com'})
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        print(msg.body)  # Логирование для отладки

        uidb64, token = extract_reset_tokens(msg.body)
        self.assertIsNotNone(uidb64)
        self.assertIsNotNone(token)

        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = self.client.post(url, {
            'uid': uidb64,
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNone(authenticate(username='fbetter777@gmail.com', password=old_password))
        self.assertIsNotNone(authenticate(username='fbetter777@gmail.com', password=new_password))

    def test_password_change(self):
        self.client.login(username='fbetter777@gmail.com', password='Spoon78Fw_')  # Исправлено

        response = self.client.post(self.password_change_url, {
            'old_password': 'Spoon78Fw_',
            'new_password1': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'New password has been saved.')

        login_response = self.client.post(self.login_url,
                                          {'username': 'fbetter777@gmail.com', 'password': 'NewStrongPass123!'})
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('key', login_response.data)

    def test_signup_with_confirmation(self):
        email = 'new_user@gmail.com'
        password = 'StrongPass123!'
        response = self.client.post(self.signup_url, {
            'username': email,
            'email': email,
            'password1': password,
            'password2': password
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

        confirmation_url = re.findall(r'http.*account-confirm-email.*\B', mail.outbox[0].body)[0]
        response = self.client.get(confirmation_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
