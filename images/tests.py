from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse_lazy

from accounts.models import CustomUser
from objects.models import Apartment


class ImagesTest(TestCase):
    def setUp(self):
        self.email = "testuser@gmail.com"
        self.password = "secretpassword"
        self.user = CustomUser.objects.create_user(
            email=self.email, password=self.password
        )

        self.client.get(reverse_lazy("fill_db", kwargs={"lang": "en"}))
        self.apartment = Apartment.objects.first()

    def test_apartment_list_failure(self):
        response = self.client.get(
            reverse_lazy(
                "images:apartment_images_list",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(
            reverse_lazy(
                "images:apartment_images_list",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_apartment_list_success(self):
        self.get_perm("view")

        self.client.force_login(self.user)

        response = self.client.get(
            reverse_lazy(
                "images:apartment_images_list",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_create_apartment_failure(self):
        response = self.client.get(
            reverse_lazy(
                "images:apartment_image_add",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        response = self.client.get(
            reverse_lazy(
                "images:apartment_image_add",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_create_apartment_success(self):
        self.get_perm("change")

        self.client.force_login(self.user)

        response = self.client.get(
            reverse_lazy(
                "images:apartment_image_add",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_handbook_failure(self):
        response = self.client.get(
            reverse_lazy(
                "images:apartment_image_delete",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        response = self.client.get(
            reverse_lazy(
                "images:apartment_image_delete",
                kwargs={"lang": "en", "pk": self.apartment.id},
            )
        )
        self.assertEqual(response.status_code, 403)

    def get_perm(self, perm_type):
        content_type = ContentType.objects.get_for_model(Apartment)
        permission = Permission.objects.get(
            content_type=content_type, codename=f"{perm_type}_apartment"
        )
        self.user.user_permissions.add(permission)
        self.user.save()
        self.user.refresh_from_db()
