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
    fixtures = ['user/fixtures/fixtures.json']

    def setUp(self):
        self.admin_user = User.objects.get(pk=1)
        self.user = User.objects.get(email='user@gmail.com')
        self.user_profile_url = reverse('user-profile')
        self.login_url = reverse('rest_login')
        self.logout_url = reverse('rest_logout')
        self.password_reset_url = reverse('rest_password_reset')
        self.password_change_url = reverse('rest_password_change')
        self.signup_url = reverse('rest_register')
        self.resend_email_verification_url = reverse('rest_resend_email')

    def test_login_success(self):
        response = self.client.post(self.login_url, {'email': 'user@gmail.com', 'password': 'BnD5Fafg21f'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {'email': 'user@gmail.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {'email': 'invalid@gmail.com', 'password': 'BnD5Fafg21f'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')

    def test_logout(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    def test_logout_on_get(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

    def test_password_reset(self):
        response = self.client.post(self.password_reset_url, {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response.data['detail'], 'Password reset e-mail has been sent.')

    def test_password_reset_confirm(self):
        old_password = 'BnD5Fafg21f'
        new_password = 'NewSecurePass123!'

        self.client.post(self.password_reset_url, {'email': 'user@gmail.com'})
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        uidb64, token = extract_reset_tokens(msg.body)
        self.assertIsNotNone(uidb64)
        self.assertIsNotNone(token)

        response = self.client.post(reverse('password_reset_confirm'), {
            'uid': uidb64,
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password has been reset with the new password.')

        self.assertIsNone(authenticate(email='user@gmail.com', password=old_password))
        self.assertIsNotNone(authenticate(email='user@gmail.com', password=new_password))

    def test_password_change(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.password_change_url, {
            'old_password': 'BnD5Fafg21f',
            'new_password1': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'New password has been saved.')

        login_response = self.client.post(self.login_url,
                                         {'email': 'user@gmail.com', 'password': 'NewStrongPass123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_signup_with_confirmation(self):
        email = 'new_user@gmail.com'
        password = 'StrongPass123!'
        response = self.client.post(self.signup_url, {
            'email': email,
            'password1': password,
            'password2': password
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(User.objects.filter(email=email, is_active=False).exists())
