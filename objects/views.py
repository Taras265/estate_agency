from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import FileResponse
import io

from accounts.models import CustomUser
from images.models import ApartmentImage
from objects.forms import SearchForm
from objects.models import Apartment
from utils.mixins.mixins import (HandbookHistoryListMixin, DeleteHandbooksMixin, FormHandbooksMixin,
                                 CustomLoginRequiredMixin,
                                 HandbookOwnPermissionListMixin, HandbookWithFilterListMixin)
from django.utils.translation import activate
from utils.pdf import generate_pdf


class ApartmentListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    handbook_type = 'apartment'
    filters = ['apartments', 'commerce', 'houses', 'lands', 'rooms']
    queryset_filters = {'apartments': Apartment.objects.filter(object_type=1).filter(on_delete=False),
                        'commerce': Apartment.objects.filter(object_type=2).filter(on_delete=False),
                        'houses': Apartment.objects.filter(object_type=3).filter(on_delete=False),
                        'lands': Apartment.objects.filter(object_type=4).filter(on_delete=False),
                        'rooms': Apartment.objects.filter(object_type=5).filter(on_delete=False)}


class ReportListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    handbook_type = 'report'
    filters = ['new_apartments', 'new_commerce', 'new_houses',
               'new_lands', 'new_rooms', 'changes', 'all_apartments', 'my_apartments']
    queryset_filters = {'new_apartments': Apartment.objects.filter(object_type=1).filter(on_delete=False),
                        'new_commerce': Apartment.objects.filter(object_type=2).filter(on_delete=False),
                        'new_houses': Apartment.objects.filter(object_type=3).filter(on_delete=False),
                        'new_lands': Apartment.objects.filter(object_type=4).filter(on_delete=False),
                        'new_rooms': Apartment.objects.filter(object_type=5).filter(on_delete=False),
                        'all_apartments': Apartment.objects.filter(object_type=1).filter(on_delete=False),
                        'my_apartments': Apartment.objects.filter(object_type=1).filter(on_delete=False)}
    custom = True


class HistoryReportListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment.history.all().model
    handbook_type = 'report'
    filters = ['new_apartments', 'new_commerce', 'new_houses',
               'new_lands', 'new_rooms', 'changes', 'all_apartments', 'my_apartments']
    queryset_filters = {'changes': Apartment.history.all(), }
    custom = True

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # переклад

        user = CustomUser.objects.filter(email=self.request.user).first()

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']

        context['choice'] = self.handbook_type
        context.update({'choices': self.choices_by_user(user)})

        """
        Ми можемо бачити дату, але, наприклад, не можемо її додавати чи продивлятись історію змін.
        Тому ми тут робимо перевірку
        """

        """
        Страшний код, де ми обробляємо список з ДІЙСНО потрібними для клієнта даними 
        (районами, квартирами ітд). Бажано колись спростити, коли буде час.
        """
        if context['object_list']:  # Якщо нам взагалі є з чим працювати
            context['object_values'] = []
            context['object_columns'] = ['id', 'date', 'user', 'field',
                                         'old_value', 'new_value']  # Назва стовпців
            for record in context['object_list']:
                if record.prev_record:
                    prev_record = record.prev_record
                    for field in record._meta.fields:
                        field_name = field.name
                        old_value = getattr(prev_record, field_name)
                        new_value = getattr(record, field_name)
                        if old_value != new_value:
                            context['object_values'].append({
                                'id': record.id,
                                'date': record.history_date,
                                'user': record.history_user,
                                'field': field.verbose_name,
                                'old_value': old_value,
                                'new_value': new_value
                            })
        else:
            context['object_columns'] = None
        return context


class ApartmentCreateView(FormHandbooksMixin, CreateView):
    handbook_type = 'apartment'
    perm_type = 'add'


class ApartmentUpdateView(FormHandbooksMixin, UpdateView):
    handbook_type = 'apartment'
    perm_type = 'change'


class ApartmentDeleteView(DeleteHandbooksMixin, DeleteView):
    handbook_type = 'apartment'


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

        context['images'] = ApartmentImage.objects.filter(apartment=context['object'].id, on_delete=False)
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
