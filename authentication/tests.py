from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.logout_all_url = reverse('logout_all')
        self.me_url = reverse('me')

        # create a test user
        self.user_email = 'test@example.com'
        self.user_password = 'testpass123'
        self.user = User.objects.create_user(username=self.user_email, email=self.user_email, password=self.user_password)

    def test_register_success_json(self):
        resp = self.client.post(self.register_url, data={'email': 'new@example.com', 'password': 'newpass'}, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['email'], 'new@example.com')

    def test_register_existing_email(self):
        resp = self.client.post(self.register_url, data={'email': self.user_email, 'password': 'x'}, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    def test_login_success_json(self):
        resp = self.client.post(self.login_url, data={'email': self.user_email, 'password': self.user_password}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(int(data['id']), self.user.pk)

    def test_login_invalid_credentials(self):
        resp = self.client.post(self.login_url, data={'email': self.user_email, 'password': 'wrong'}, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_logout_with_valid_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        resp = self.client.post(self.logout_url, data={'refresh': str(refresh)}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('detail', resp.json())

    def test_logout_with_invalid_refresh(self):
        resp = self.client.post(self.logout_url, data={'refresh': 'invalidtoken'}, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_logout_all_requires_authentication(self):
        resp = self.client.post(self.logout_all_url, content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_logout_all_authenticated(self):
        # create two refresh tokens for the user
        r1 = RefreshToken.for_user(self.user)
        r2 = RefreshToken.for_user(self.user)
        # authenticate client by forcing user on requests (Client.login won't set JWT on request.user)
        self.client.force_login(self.user)
        resp = self.client.post(self.logout_all_url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('detail', resp.json())

    def test_me_requires_authentication(self):
        resp = self.client.get(self.me_url)
        self.assertEqual(resp.status_code, 401)

    def test_me_authenticated(self):
        # use JWT to authenticate via DRF authentication class
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        auth_header = f'Bearer {access}'
        resp = self.client.get(self.me_url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['email'], self.user_email)
        self.assertEqual(data['id'], self.user.pk)

