from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView

from accounts.models import CustomUser
from images.forms import ApartmentImageForm
from images.models import RealEstateImage
from objects.models import Apartment
from utils.const import LIST_BY_USER
from utils.mixins.mixins import FormMixin, DeleteMixin, CustomLoginRequiredMixin
from django.utils.translation import activate


class ApartmentImageListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    paginate_by = 15
    template_name = 'images/list.html'
    context_object_name = 'images'

    def get_permission_required(self):
        user = CustomUser.objects.filter(email=self.request.user).first()

        if not user.has_perm(f'objects.view_apartment'):
            self.permission_required = f'objects.view_own_apartment'
        else:
            self.permission_required = f'objects.view_apartment'

        return super().get_permission_required()

    def get_queryset(self):
        queryset = Apartment.objects.filter(id=self.kwargs['pk'])
        if self.permission_required.find('own') != -1:
            user = CustomUser.objects.filter(email=self.request.user).first()
            new_queryset = None
            for field in LIST_BY_USER['apartment']:
                if new_queryset:
                    new_queryset = new_queryset | queryset.filter(**{field: user})
                else:
                    new_queryset = queryset.filter(**{field: user})
            queryset = new_queryset
        # return ApartmentImage.objects.filter(on_delete=False, apartment=queryset.first())
        return queryset.first().images

    def get_context_data(self, *, object_list=None, **kwargs):
        user = CustomUser.objects.filter(email=self.request.user).first()

        activate(self.kwargs['lang'])  # translation
        context = super().get_context_data(**kwargs)

        context['lang'] = self.kwargs['lang']
        can_update = user.has_perm(f'objects.change_apartment')
        if not can_update and context['images']:
            apartment = context['images'][0].apartment
            for field in LIST_BY_USER['apartment']:
                if getattr(apartment, field) == user:
                    can_update = user.has_perm(f'objects.change_own_apartment')
        context['can_update'] = can_update

        return context


class ApartmentImageCreateView(FormMixin, CreateView):
    form_class = ApartmentImageForm
    success_url = reverse_lazy("images:apartment_images_list")

    choice_name = 'apartment'

    def get_permission_required(self):
        user = CustomUser.objects.filter(email=self.request.user).first()

        if not user.has_perm(f'objects.change_apartment'):
            self.permission_required = f'objects.change_own_apartment'
        else:
            self.permission_required = f'objects.change_apartment'

        return super().get_permission_required()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        initial = kwargs.get('data', {}).copy()
        initial['apartment'] = Apartment.objects.filter(id=self.kwargs.get('pk')).first()
        kwargs['data'] = initial
        return kwargs

    def get_success_url(self):
        return reverse_lazy("images:apartment_images_list", kwargs={"lang": self.kwargs['lang'],
                                                                "pk": self.kwargs["pk"]})


class ApartmentImageDeleteView(DeleteMixin, DeleteView):
    queryset = RealEstateImage.objects.filter(on_delete=False)
    form_class = ApartmentImageForm
    success_url = reverse_lazy("images:apartment_images_list")

    choice_name = 'apartment'

    def get_permission_required(self):
        user = CustomUser.objects.filter(email=self.request.user).first()

        if not user.has_perm(f'objects.change_apartment'):
            self.permission_required = f'objects.change_own_apartment'
        else:
            self.permission_required = f'objects.change_apartment'

        return super().get_permission_required()

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang']})
