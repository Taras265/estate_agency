from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import FileResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.utils.translation import activate
import io

from accounts.models import CustomUser
from images.models import ApartmentImage
from objects.forms import ApartmentForm, SearchForm
from objects.models import Apartment
from utils.const import CHOICES, LIST_BY_USER, QUERYSET
from utils.mixins.mixins import FormMixin, HandbookListMixin, SpecialRightFormMixin, \
    SpecialRightDeleteMixin, HandbookHistoryListMixin, CustomLoginRequiredMixin
from utils.pdf import generate_pdf


class HandbookListView(HandbookListMixin, ListView):
    handbook_type = 'apartment'
    object_columns = ["id", "region_id", "district_id", "locality_id",
                      "locality_district_id", "street_id"]

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]


class ApartmentCreateView(FormMixin, CreateView):
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang'], })


class ApartmentUpdateView(SpecialRightFormMixin, UpdateView):
    queryset = Apartment.objects.filter(on_delete=False)
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'
    user_field = []

    def get_success_url(self):
        return reverse_lazy("objects:handbooks_list", kwargs={"lang": self.kwargs['lang'], })


class ApartmentDeleteView(SpecialRightDeleteMixin, DeleteView):
    queryset = Apartment.objects.filter(on_delete=False)
    form_class = ApartmentForm
    success_url = reverse_lazy("objects:handbooks_list")

    choice_name = 'apartment'

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
    

class PdfView(CustomLoginRequiredMixin, View):

    def get(self, request, lang):
        queryset = Apartment.objects.filter(on_delete=False)

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

        pdf = generate_pdf(queryset, request.user.get_full_name()[0])

        return FileResponse(
            io.BytesIO(pdf.output()), 
            as_attachment=True, 
            filename='document.pdf', 
            content_type='application/pdf'
        )


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
