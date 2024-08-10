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


class ApartmentImageListView(CustomLoginRequiredMixin, ListView):
    paginate_by = 15
    template_name = 'images/list.html'
    context_object_name = 'images'

    def get_queryset(self):
        return ApartmentImage.objects.filter(on_delete=False).filter(apartment=Apartment.objects.filter(id=self.kwargs['pk']).first())

    def get_context_data(self, *, object_list=None, **kwargs):
        user = CustomUser.objects.filter(email=self.request.user).first()
        user_type = user.user_type
        choices = self.choices_by_user()

        activate(self.kwargs['lang'])  # translation
        if user_type in CHOICES.keys() and ('apartment', 'apartment') in choices:
            context = super().get_context_data(**kwargs)

            context['lang'] = self.kwargs['lang']

            return context
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}


class ApartmentImageCreateView(FormMixin, CreateView):
    form_class = ApartmentImageForm
    success_url = reverse_lazy("images:apartment_images_list")

    choice_name = 'apartment'

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

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang']})
