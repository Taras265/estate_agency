from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from images.models import ApartmentImage
from objects.forms import ApartmentForm, SearchForm
from objects.models import Apartment
from utils.const import CHOICES, LIST_BY_USER, MODEL
from utils.mixins.mixins import FormMixin, DeleteMixin, \
    HandbookHistoryListMixin, HandbookListPermissionMixin
from django.utils.translation import gettext as _
from django.utils.translation import activate


class HandbookListView(HandbookListPermissionMixin, ListView):
    handbook_type = 'apartment'


class ApartmentCreateView(FormMixin, CreateView):
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'
    permission_required = 'objects.add_apartment'

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang'], })


class ApartmentUpdateView(FormMixin, UpdateView):
    queryset = Apartment.objects.filter(on_delete=False)
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'
    permission_required = 'objects.change_apartment'

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang'], })


class ApartmentDeleteView(DeleteMixin, DeleteView):
    queryset = Apartment.objects.filter(on_delete=False)
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'
    permission_required = 'objects.change_apartment'

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang'], })


class CatalogListView(ListView):
    paginate_by = 15
    template_name = 'objects/catalog.html'
    queryset = Apartment.objects.filter(on_delete=False)
    context_object_name = 'objects'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data.get('locality'):
                queryset = queryset.filter(locality__locality__icontains=form.cleaned_data['locality'])
            if form.cleaned_data.get('street'):
                queryset = queryset.filter(street__street__icontains=form.cleaned_data['street'])
            if form.cleaned_data.get('price_min'):
                queryset = queryset.filter(price__gte=form.cleaned_data['price_min'])
            if form.cleaned_data.get('price_max'):
                queryset = queryset.filter(price__lte=form.cleaned_data['price_max'])

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])
        context = super().get_context_data(**kwargs)

        context['lang'] = self.kwargs['lang']
        context['form'] = SearchForm(self.request.GET)

        objects = []
        for obj in context['objects']:
            objects.append({'object': obj, 'image': ApartmentImage.objects.filter(apartment=obj.id).first()})
        context['objects'] = objects
        return context


class ApartmentDetailView(DetailView):
    queryset = Apartment.objects.filter(on_delete=False)
    context_object_name = 'object'
    template_name = 'objects/details.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])
        context = super().get_context_data(**kwargs)

        context['lang'] = self.kwargs['lang']

        context['images'] = ApartmentImage.objects.filter(apartment=context['object'].id)
        return context


class ObjectHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = 'apartment'


"""
class ApartmentCreateView(FormMixin, FormView):
    form_class = FlatForm
    success_url = reverse_lazy("objects:handbooks_list")

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)

        obj = ObjectCreateForm(self.request.POST)
        apartment = ApartmentCreateForm(self.request.POST)

        apartment.object = 1

        if obj.is_valid():
            print(apartment.initial)
            print(apartment.is_valid())

        if form.is_valid():
            return self.success_url
"""