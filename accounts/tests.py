from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse_lazy

from accounts.models import CustomUser


class AccountsTest(TestCase):
    def setUp(self):
        self.email = "testuser@gmail.com"
        self.password = "secretpassword"
        self.user = CustomUser.objects.create_user(email=self.email, password=self.password)

    def test_login_success(self):
        response = self.client.post(reverse_lazy('accounts:login', kwargs={'lang': 'en'}), {
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/'))

    def test_login_failure(self):
        response = self.client.post(reverse_lazy('accounts:login', kwargs={'lang': 'en'}), {
            'username': self.email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_failure(self):
        response = self.client.get(reverse_lazy('accounts:profile', kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('accounts:profile', kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 403)

    def test_profile_success(self):
        content_type = ContentType.objects.get_for_model(CustomUser)

        permission = Permission.objects.create(
            codename='profile',
            name='Profile',
            content_type=content_type
        )
        self.user.user_permissions.add(permission)
        self.user.save()

        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('accounts:profile', kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 200)
