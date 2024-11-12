from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse_lazy

from accounts.models import CustomUser
from handbooks.models import Handbook
from utils.const import MODEL, HANDBOOKS_QUERYSET


class HandbooksTest(TestCase):
    def setUp(self):
        self.email = "testuser@gmail.com"
        self.password = "secretpassword"
        self.user = CustomUser.objects.create_user(email=self.email, password=self.password)
        self.handbooks = ['region', 'district', 'locality', 'localitydistrict',
                          'street', 'client', 'withdrawalreason', 'condition',
                          'material', 'separation', 'agency', 'agencysales', 'newbuildingname',
                          'stair', 'heating', 'layout', 'housetype', 'filialagency', 'filialreport']

        self.client.get(reverse_lazy('fill_db',
                                     kwargs={'lang': 'en'}))

    def test_handbook_list_failure(self):
        response = self.client.get(reverse_lazy('handbooks:handbook_redirect',
                                                kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 302)
        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy(f'handbooks:{handbook}_list',
                                                    kwargs={'lang': 'en'}))
            self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy(f'handbooks:{handbook}_list',
                                                    kwargs={'lang': 'en'}))
            self.assertEqual(response.status_code, 403)

    def test_handbook_list_success(self):
        self.get_perm('view')
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy('handbooks:handbook_redirect',
                                                kwargs={'lang': 'en'}))
        self.assertEqual(response.status_code, 302)
        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy(f'handbooks:{handbook}_list',
                                                    kwargs={'lang': 'en'}))
            self.assertEqual(response.status_code, 200)

    def test_create_handbook_failure(self):
        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy('handbooks:create_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook}))
            self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy('handbooks:create_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook}))
            self.assertEqual(response.status_code, 403)

    def test_create_handbook_success(self):
        self.get_perm('add')

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            response = self.client.get(reverse_lazy('handbooks:create_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook}))
            self.assertEqual(response.status_code, 200)

    def test_update_handbook_failure(self):
        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:update_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:update_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 403)

    def test_update_handbook_success(self):
        self.get_perm('change')

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:update_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 200)

    def test_delete_handbook_failure(self):
        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:delete_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:delete_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 403)

    def test_delete_handbook_success(self):
        self.get_perm('change')

        self.client.force_login(self.user)

        for handbook in self.handbooks:
            obj = self.get_obj(handbook)
            response = self.client.get(reverse_lazy('handbooks:delete_handbook',
                                                    kwargs={'lang': 'en',
                                                            'handbook_type': handbook,
                                                            'pk': obj.id}))
            self.assertEqual(response.status_code, 200)

    def get_perm(self, perm_type, handbook_list=None):
        if not handbook_list:
            handbook_list = self.handbooks
        for p in handbook_list:
            if p in MODEL.keys():
                model = MODEL[p]
                content_type = ContentType.objects.get_for_model(model)
            else:
                model = Handbook
                content_type = ContentType.objects.get_for_model(model)
                Permission.objects.create(
                    codename=f'{perm_type}_{p}',
                    name=f'{p}',
                    content_type=content_type
                )
            if not Permission.objects.filter(content_type=content_type, codename=f'{perm_type}_{p}'):
                Permission.objects.create(
                    codename=f'{perm_type}_{p}',
                    name=f'{p}',
                    content_type=content_type
                )
            permission = Permission.objects.get(content_type=content_type, codename=f'{perm_type}_{p}')
            self.user.user_permissions.add(permission)
            self.user.save()
            self.user.refresh_from_db()

    @staticmethod
    def get_obj(handbook):
        if handbook in MODEL.keys():
            return MODEL[handbook].objects.first()
        return Handbook.objects.filter(type=HANDBOOKS_QUERYSET[handbook]).first()
