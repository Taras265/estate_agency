from django.shortcuts import redirect
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.utils.translation import activate
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    View, ListView, CreateView, UpdateView, DeleteView,
    DetailView, TemplateView
)
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, UserPassesTestMixin,
)
import io

from accounts.models import CustomUser
from handbooks.forms import SelectionForm
from handbooks.models import Client, Street
from images.forms import RealEstateImageFormSet
from .models import Apartment, Commerce, House
from .services import (
    real_estate_form_save, has_any_perm_form_list,
    has_appropriate_change_perm,
)
from .choices import RealEstateType
from .mixins import (
    RealEstateCreateContextMixin, RealEstateUpdateContextMixin,
)
from .forms import (
    SearchForm, HandbooksSearchForm, 
    ApartmentForm, CommerceForm, HouseForm,
    ApartmentVerifyAddressForm, CommerceVerifyAddressForm,
    HouseVerifyAddressForm,
)
from utils.const import SALE_CHOICES
from utils.mixins.mixins import (
    HandbookHistoryListMixin,
    CustomLoginRequiredMixin, HandbookOwnPermissionListMixin, 
    HandbookWithFilterListMixin,
)
from utils.pdf import generate_pdf


@require_GET
def verify_real_estate_address(request, lang):
    """
    Перевіряє, чи існує обʼєкт нерухомості з типом type за введенною
    адресою (localityId, streetId, house, apartment/premises/housing).
    Дані про обʼєкт нерухомості передаються через query параметри.
    Список необхідних query параметрів:
    - type: int
    - locality: int
    - street: int
    - house: str
    - apartment/premises/housing: str (в залежності від типу обʼєкта)
    """
    try:
        real_estate_type = int(request.GET.get("type"))
    except ValueError:
        return JsonResponse({
            "success": False, 
            "errors": {"type": "Invalid real estate type."},
        })

    form = None

    if real_estate_type == RealEstateType.APARTMENT:
        form = ApartmentVerifyAddressForm(request.GET)
    elif real_estate_type == RealEstateType.COMMERCE:
        form = CommerceVerifyAddressForm(request.GET)
    elif real_estate_type == RealEstateType.HOUSE:
        form = HouseVerifyAddressForm(request.GET)
    
    if not form:
        return JsonResponse({
            "success": False, 
            "errors": {"type": "Invalid real estate type."},
        })

    if not form.is_valid():
        return JsonResponse({
            "success": False,
            "errors": form.errors.get_json_data(),
        })

    real_estate = None

    if real_estate_type == RealEstateType.APARTMENT:
        real_estate = Apartment.objects.filter(**form.cleaned_data).only("id").first()
    elif real_estate_type ==  RealEstateType.COMMERCE:
        real_estate = Commerce.objects.filter(**form.cleaned_data).only("id").first()
    elif real_estate_type ==  RealEstateType.HOUSE:
        real_estate = House.objects.filter(**form.cleaned_data).only("id").first()

    if not real_estate:
        return JsonResponse({
            "success": True,
            "message": f"{RealEstateType.labels[real_estate_type-1]} doesn't exist.",
        })
    return JsonResponse({
        "success": True,
        "message": f"{RealEstateType.labels[real_estate_type-1]} exists (id {real_estate.id}).",
    })


@require_GET
def fill_real_estate_address(request, lang):
    """
    Доповнює адресу обʼєкта нерухомості за вже введеними даними адреси.
    Наприклад, якщо користувач ввів вулицю, 
    то шукає відповідний район міста, місто, район області та область.
    Дані передаються через query параметри.
    Список необхідних query параметрів:
    - street: int
    """
    street_id = request.GET.get("street")
    if not street_id:
        return JsonResponse({"success": False, "locality": None})

    try:
        street = Street.objects\
                    .select_related("locality_district__locality")\
                    .get(pk=street_id, on_delete=False)
    except Street.DoesNotExist:
        return JsonResponse({"success": False, "locality": -1})

    return JsonResponse({
        "success": True,
        "locality": street.locality_district.locality.pk,
    })


class SelectionListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "objects/selection_list.html"
    context_object_name = "objects"
    permission_required = "objects.selection"

    def get_form(self, client):
        if len(self.request.GET) == 0:
            initial_data = {
                'rooms_number': client.rooms_number,
                'locality': client.locality.all(),
                'locality_district': client.locality_district.all(),
                'street': client.street.all(),
                'house': client.house,
                'floor_min': client.floor_min,
                'floor_max': client.floor_max,
                'not_first': client.not_first,
                'not_last': client.not_last,
                'price_from': client.price_from,
                'price_to': client.price_to,
                'square_meter_price_max': client.square_meter_price_max,
                'condition': client.condition.all()
            }
            return SelectionForm(initial_data)
        return SelectionForm(self.request.GET)

    def get_queryset(self):
        queryset = Apartment.objects.filter(on_delete=False)

        client_id = self.kwargs.get('client_id')
        client = Client.objects.filter(id=client_id).first()

        if client.status == 1:
            client.status = 2
            client.save()

        form = self.get_form(client)
        form.is_valid()

        if form.cleaned_data.get('rooms_number') is not None:
            queryset = queryset.filter(rooms_number=form.cleaned_data.get('rooms_number'))
        if form.cleaned_data.get('locality').exists():
            queryset = queryset.filter(locality__in=form.cleaned_data.get('locality'))
        if form.cleaned_data.get('locality_district').exists():
            queryset = queryset.filter(locality_district__in=form.cleaned_data.get('locality_district'))
        if form.cleaned_data.get('street').exists():
            queryset = queryset.filter(street__in=form.cleaned_data.get('street'))
        if form.cleaned_data.get('house') is not None and form.cleaned_data.get('house') != '':
            queryset = queryset.filter(house=form.cleaned_data.get('house'))
        if form.cleaned_data.get('floor_min') is not None:
            queryset = queryset.filter(floor__gte=form.cleaned_data.get('floor_min'))
        if form.cleaned_data.get('floor_max') is not None:
            queryset = queryset.filter(floor__lte=form.cleaned_data.get('floor_max'))
        if form.cleaned_data.get('not_first'):
            queryset = queryset.exclude(floor=1)
            queryset = queryset.filter(storeys_number__lte=form.cleaned_data.get('storeys_num_max'))
        if form.cleaned_data.get('price_from') is not None:
            queryset = queryset.filter(price__gte=form.cleaned_data.get('price_from'))
        if form.cleaned_data.get('price_to') is not None:
            queryset = queryset.filter(price__lte=form.cleaned_data.get('price_to'))
        if form.cleaned_data.get('square_meter_price_max') is not None:
            queryset = queryset.filter(
                square_meter_price__lte=form.cleaned_data.get('square_meter_price_max')
            )
        if form.cleaned_data.get('condition').exists():
            queryset = queryset.filter(condition__in=form.cleaned_data.get('condition'))

        if form.cleaned_data.get('key_word') is not None and form.cleaned_data.get('key_word') != '':
            key_word = form.cleaned_data.get('key_word')
            queryset = queryset.filter(Q(region__region__icontains=key_word) |
                                       Q(district__district__icontains=key_word) |
                                       Q(locality__locality__icontains=key_word) |
                                       Q(locality_district__district__icontains=key_word) |
                                       Q(street__street__icontains=key_word) |
                                       Q(house__icontains=key_word) |
                                       Q(comment__icontains=key_word))

        n_queryset = queryset
        for obj in n_queryset:
            if form.cleaned_data.get('not_last') and obj.storeys_number == obj.floor:
                n_queryset = n_queryset.exclude(id=obj.id)

        return n_queryset

    def get_context_data(self, **kwargs):
        activate(self.kwargs['lang'])  # Перекладаємо

        client_id = self.kwargs.get('client_id')
        client = Client.objects.filter(id=client_id).first()

        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']
        context['client'] = client

        context['form'] = self.get_form(client)

        objects = []
        for obj in context['objects']:
            # images = ApartmentImage.objects.filter(apartment=obj)
            images = Apartment.images.all()
            objects.append(
                {'image': images.first(), 'object': obj}
            )
        context['objects'] = objects

        return context


class ShowingActView(TemplateView):
    template_name = "objects/showing_act.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_ids = self.request.GET.getlist("apartments")

        context['lang'] = self.kwargs['lang']
        objects = []
        for obj in Apartment.objects.filter(id__in=selected_ids):
            # objects.append({
            #     'object': obj,
            #     'image': ApartmentImage.objects.filter(apartment=obj.id).filter(on_delete=False).first()
            # })
            objects.append({
                'object': obj,
                'image': Apartment.images.filter(on_delete=False).first(),
            })
        context['objects'] = objects

        return context


class ApartmentListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    handbook_type = 'apartment'
    filters = ['apartments', 'commerce', 'houses', 'lands', 'rooms']
    queryset_filters = {'apartments': Apartment.objects.filter(on_delete=False),
                        'commerce': Commerce.objects.filter(on_delete=False),
                        'houses': House.objects.filter(on_delete=False),
                        'lands': Apartment.objects.none(),
                        'rooms': Apartment.objects.none()}
    form = HandbooksSearchForm
    choices = SALE_CHOICES

    def get_queryset(self):
        return HandbookWithFilterListMixin.get_queryset(self).intersection(HandbookOwnPermissionListMixin.get_queryset(self))


class ReportListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    handbook_type = 'report'
    filters = ['new_apartments', 'new_commerce', 'new_houses',
               'new_lands', 'new_rooms', 'changes', 'all_apartments', 'my_apartments']
    queryset_filters = {'new_apartments': Apartment.objects.filter(on_delete=False),
                        'new_commerce': Commerce.objects.filter(on_delete=False),
                        'new_houses': House.objects.filter(on_delete=False),
                        'new_lands': Apartment.objects.none(),
                        'new_rooms': Apartment.objects.none(),
                        'all_apartments': Apartment.objects.filter(on_delete=False),
                        'my_apartments': Apartment.objects.filter(on_delete=False)}
    custom = True
    form = HandbooksSearchForm
    choices = SALE_CHOICES

    def get_queryset(self):
        q1 = HandbookWithFilterListMixin.get_queryset(self)
        q2 = HandbookOwnPermissionListMixin.get_queryset(self)
        return q1.intersection(q2)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context['object_list']:
            return context

        # у полі status замінюємо число на відповідний йому текст
        for index, obj in enumerate(context['object_values']):
            apartment: Apartment = context['object_list'][index]
            obj['status'] = apartment.get_status_display()

        return context


class ContractListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    handbook_type = 'contract'
    filters = ['apartments', 'commerce', 'houses',
               'lands', 'rooms']
    queryset_filters = {'apartments': Apartment.objects.filter(status__gte=4).filter(on_delete=False),
                        'commerce': Commerce.objects.filter(status__gte=4).filter(on_delete=False),
                        'houses': House.objects.filter(status__gte=4).filter(on_delete=False),
                        'lands': Apartment.objects.none(),
                        'rooms': Apartment.objects.none()}
    custom = True
    form = HandbooksSearchForm
    choices = SALE_CHOICES

    def get_queryset(self):
        q1 = HandbookWithFilterListMixin.get_queryset(self)
        q2 = HandbookOwnPermissionListMixin.get_queryset(self)
        return q1.intersection(q2)


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


class RealEstateCreateRedirectView(CustomLoginRequiredMixin, View):
    """
    Перенаправляє користувача на відповідну форму створення 
    обʼєкта нерухомості в залежності від наявних в нього прав.
    """
    def get(self, request):
        can_add_apartment = request.user.has_perm("objects.add_apartment")
        can_add_own_apartment = request.user.has_perm("objects.add_own_apartment")
        if (can_add_apartment or can_add_own_apartment):
            return redirect(reverse_lazy("objects:create_apartment"))
        
        can_add_commerce = request.user.has_perm("objects.add_commerce")
        can_add_own_commerce = request.user.has_perm("objects.add_own_commerce")
        if (can_add_commerce or can_add_own_commerce):
            return redirect(reverse_lazy("objects:create_commerce"))

        can_add_house = request.user.has_perm("objects.add_house")
        can_add_own_house = request.user.has_perm("objects.add_own_house")
        if (can_add_house or can_add_own_house):
            return redirect(reverse_lazy("objects:create_house"))

        raise PermissionDenied()


class ApartmentCreateView(CustomLoginRequiredMixin,
                          UserPassesTestMixin,
                          RealEstateCreateContextMixin,
                          CreateView):
    """
    Форма створення нової квартири.
    Для доступу до цієї сторінки потрібно мати право
    objects.add_apartment або objects.add_own_apartment.
    """
    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_create_form.html"

    def test_func(self):
        return has_any_perm_form_list(
            self.request.user,
            "objects.add_apartment",
            "objects.add_own_apartment"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.APARTMENT
        return context
    
    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())
    
    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "apartments"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)
    

class CommerceCreateView(CustomLoginRequiredMixin,
                         UserPassesTestMixin,
                         RealEstateCreateContextMixin,
                         CreateView):
    """
    Форма створення нової комерції.
    Для доступу до цієї сторінки потрібно мати право
    objects.add_commerce або objects.add_own_commerce.
    """
    model = Commerce
    form_class = CommerceForm
    template_name = "objects/real_estate_create_form.html"

    def test_func(self):
        return has_any_perm_form_list(
            self.request.user,
            "objects.add_commerce",
            "objects.add_own_commerce"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.COMMERCE
        return context
    
    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "commerce"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)
    

class HouseCreateView(CustomLoginRequiredMixin,
                      UserPassesTestMixin,
                      RealEstateCreateContextMixin,
                      CreateView):
    """
    Форма створення нового будинку.
    Для доступу до цієї сторінки потрібно мати право
    objects.add_house або objects.add_own_house.
    """
    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_create_form.html"

    def test_func(self):
        return has_any_perm_form_list(
            self.request.user,
            "objects.add_house",
            "objects.add_own_house"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.HOUSE
        return context
    
    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())
    
    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "houses"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class ApartmentUpdateView(CustomLoginRequiredMixin,
                          UserPassesTestMixin,
                          RealEstateUpdateContextMixin,
                          UpdateView):
    """Форма редагування квартири."""
    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_apartment",
            "objects.change_own_apartment"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.APARTMENT
        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "apartments"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)
    

class CommerceUpdateView(CustomLoginRequiredMixin,
                         UserPassesTestMixin,
                         RealEstateUpdateContextMixin,
                         UpdateView):
    """Форма редагування комерції."""
    model = Commerce
    form_class = CommerceForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_commerce",
            "objects.change_own_commerce",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.COMMERCE
        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "commerce"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class HouseUpdateView(CustomLoginRequiredMixin,
                      UserPassesTestMixin,
                      RealEstateUpdateContextMixin,
                      UpdateView):
    """Форма редагування будинку."""
    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_house",
            "objects.change_own_house",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.HOUSE
        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )
        if not is_saved:
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "houses"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class ApartmentDeleteView(CustomLoginRequiredMixin,
                          UserPassesTestMixin,
                          DeleteView):
    """Видалення квартири."""
    template_name = "delete_form.html"
    model = Apartment

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_apartment",
            "objects.change_own_apartment"
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "apartments"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class CommerceDeleteView(CustomLoginRequiredMixin,
                         UserPassesTestMixin,
                         DeleteView):
    """Видалення комерції."""
    template_name = "delete_form.html"
    model = Commerce

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_commerce",
            "objects.change_own_commerce"
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "commerce"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class HouseDeleteView(CustomLoginRequiredMixin,
                      UserPassesTestMixin,
                      DeleteView):
    """Видалення будинку."""
    template_name = "delete_form.html"
    model = House

    def test_func(self):
        return has_appropriate_change_perm(
            self.request.user,
            self.model,
            self.kwargs["pk"],
            "objects.change_house",
            "objects.change_own_house"
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"], "filter": "houses"}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


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
            objects.append({
                'object': obj,
                'image': obj.images.filter(on_delete=False).first()
            })
        context['objects'] = objects
        return context


class PdfView(CustomLoginRequiredMixin, View):

    def get(self, request, lang):
        queryset = Apartment.objects.filter(on_delete=False)

        selected_ids = self.request.GET.getlist("apartments")

        pdf = generate_pdf(Apartment.objects.filter(id__in=selected_ids), request.user.get_full_name()[0])

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

        # context['images'] = ApartmentImage.objects.filter(apartment=context['object'].id, on_delete=False)
        apartment = Apartment.objects.get(id=context['object'].id)
        context['images'] = apartment.images.filter(on_delete=False)
        return context


class ObjectHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = 'apartment'
