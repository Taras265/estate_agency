from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView

from accounts.models import CustomUser
from images.forms import ApartmentImageForm
from images.models import ApartmentImage
from objects.models import Apartment
from utils.const import CHOICES
from utils.mixins.mixins import FormMixin, DeleteMixin, CustomLoginRequiredMixin
from django.utils.translation import gettext as _
from django.utils.translation import activate


class ApartmentImageListView(PermissionRequiredMixin, CustomLoginRequiredMixin, ListView):
    paginate_by = 15
    template_name = 'images/list.html'
    context_object_name = 'images'

    permission_required = 'images.change_apartmentimage'

    def get_queryset(self):
        return ApartmentImage.objects.filter(on_delete=False).filter(apartment=Apartment.objects.filter(id=self.kwargs['pk']).first())

    def get_context_data(self, *, object_list=None, **kwargs):
        user = CustomUser.objects.filter(email=self.request.user).first()

        activate(self.kwargs['lang'])  # translation
        context = super().get_context_data(**kwargs)

        context['lang'] = self.kwargs['lang']
        context['can_update'] = user.has_perm(f'images.change_apartmentimage')

        return context


class ApartmentImageCreateView(FormMixin, CreateView):
    form_class = ApartmentImageForm
    success_url = reverse_lazy("images:apartment_images_list")

    choice_name = 'apartment'
    permission_required = 'images.add_apartmentimage'

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
    queryset = ApartmentImage.objects.filter(on_delete=False)
    form_class = ApartmentImageForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'
    permission_required = 'images.change_apartmentimage'

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang']})
