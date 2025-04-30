from itertools import chain
from urllib.parse import urlencode

from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import activate, gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    View, ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, UserPassesTestMixin,
)
import io

from accounts.models import CustomUser
from accounts.services import user_get
from handbooks.forms import SelectionForm
from handbooks.models import Client, Street
from handbooks.services import client_get
from images.forms import RealEstateImageFormSet
from utils.mixins.new_mixins import StandardContextDataMixin, GetQuerysetMixin
from utils.utils import get_office_context
from .models import Apartment, Commerce, House
from .services import (
    has_any_perm_from_list,
    user_can_view_apartment_list, user_can_view_commerce_list,
    user_can_view_house_list, user_can_view_real_estate_list,
    user_can_create_apartment, user_can_create_commerce,
    user_can_create_house, user_can_update_apartment,
    user_can_update_commerce, user_can_update_house,
    user_can_update_apartment_list, user_can_update_commerce_list,
    user_can_update_house_list, user_can_view_apartment_list_history,
    user_can_view_commerce_list_history, user_can_view_house_list_history,
    apartment_filter_for_user, commerce_filter_for_user, house_filter_for_user, estate_objects_filter_visible,
    selection_create, selection_filter, selection_all, selection_add_selected, get_all_apartment_history,
    get_all_commerce_history, get_all_houses_history, apartment_filter_by_user, apartment_filter_by_filial,
    commerce_filter_by_filial, house_filter_by_filial
)
from .utils import real_estate_form_save
from .choices import RealEstateType, RealEstateStatus
from .mixins import (
    RealEstateCreateContextMixin, RealEstateUpdateContextMixin, SaleListContextMixin
)
from .forms import (
    SearchForm, HandbooksSearchForm, ApartmentForm, CommerceForm, HouseForm,
    ApartmentVerifyAddressForm, CommerceVerifyAddressForm, HouseVerifyAddressForm,
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
    activate(lang)
    try:
        real_estate_type = int(request.GET.get("type"))
    except ValueError:
        return JsonResponse({
            "success": False, 
            "errors": {"type": _("Invalid real estate type")},
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
            "errors": {"type": _("Invalid real estate type")},
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
            "message": _("Doesn't exist"),
        })
    return JsonResponse({
        "success": True,
        "message": _("Exists (id {id})").format(id=real_estate.id),
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


@require_POST
def set_real_estate_status_sold(request, lang, id):
    """
    Встановлює статус ПРОДАНИЙ для об'єкта нерухомості.
    Список необхідних query параметрів:
    - type: int
    """
    try:
        real_estate_type = int(request.GET.get("type"))
    except ValueError:
        return JsonResponse({
            "success": False, 
            "errors": {"type": _("Invalid real estate type")},
        })

    model = None

    if real_estate_type == RealEstateType.APARTMENT:
        model = Apartment
    elif real_estate_type == RealEstateType.COMMERCE:
        model = Commerce
    elif real_estate_type == RealEstateType.HOUSE:
        model = House
    
    if not model:
        return JsonResponse({
            "success": False, 
            "errors": {"type": _("Invalid real estate type")},
        })

    real_estate = get_object_or_404(model.objects.only("status"), id=id)
    real_estate.status = RealEstateStatus.SOLD
    real_estate.save()
    return JsonResponse({"success": True})


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
                'condition': client.condition.all(),
                'object_type': client.object_type,
            }
            return SelectionForm(initial_data)
        return SelectionForm(self.request.GET)

    def get_queryset(self):

        client_id = self.kwargs.get('client_id')
        client = Client.objects.filter(id=client_id).first()

        if client.status == 1:
            client.status = 2
            client.save()

        form = self.get_form(client)
        form.is_valid()

        obj_type = int(form.cleaned_data.get('object_type'))
        if obj_type == RealEstateType.APARTMENT:
            queryset = Apartment.objects.filter(on_delete=False,
                                            status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT))
        elif obj_type == RealEstateType.COMMERCE:
            queryset = Commerce.objects.filter(on_delete=False,
                                            status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT))
        else:
            queryset = House.objects.filter(on_delete=False,
                                            status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT))

        # if form.cleaned_data.get('rooms_number') is not None:
        #     queryset = queryset.filter(rooms_number=form.cleaned_data.get('rooms_number'))
        if form.cleaned_data.get('locality').exists():
            queryset = queryset.filter(locality__in=form.cleaned_data.get('locality'))
        # if form.cleaned_data.get('locality_district').exists():
        #     queryset = queryset.filter(locality_district__in=form.cleaned_data.get('locality_district'))
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
        # if form.cleaned_data.get('square_meter_price_max') is not None:
        #     queryset = queryset.filter(
        #         square_meter_price__lte=form.cleaned_data.get('square_meter_price_max')
        #     )
        if form.cleaned_data.get('condition'):
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
            image = obj.images.first()
            objects.append(
                {'image': image, 'object': obj}
            )
        context['objects'] = objects
        context["client"] = client

        return context


class SelectionHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin,
                           StandardContextDataMixin, GetQuerysetMixin, ListView):
    object_list = selection_all()
    permission_required = "objects.selection"
    template_name = "objects/selection_history_list.html"
    context_object_name = "objects"


    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        context = self.get_context_data()
        context['selections'] = selection_filter(client_id=pk)
        return self.render_to_response(context)


def showing_act_redirect(request, lang):
    selected_ids = request.GET.getlist("objects")
    object_type = int(request.GET.get("object_type"))

    objects = estate_objects_filter_visible(
                object_type=object_type,
                id__in=selected_ids
        )

    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = client_get(id=client_id)
    user = user_get(email=request.user)

    selection = selection_create(client=client,
                     user=user,
                     )
    for obj in objects:
        selection_add_selected(object_type, selection, obj)
    selection.save()

    params = request.GET.copy()
    params['objects'] = selected_ids

    url = reverse_lazy("objects:showing_act", kwargs={"lang": "en"})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


def pdf_redirect(request, lang):
    selected_ids = request.GET.getlist("objects")
    object_type = int(request.GET.get("object_type"))

    objects = estate_objects_filter_visible(
                object_type=object_type,
                id__in=selected_ids
        )

    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = client_get(id=client_id)
    user = user_get(email=request.user)

    selection = selection_create(client=client,
                                 user=user,
                                 )
    for obj in objects:
        selection_add_selected(object_type, selection, obj)
    selection.save()

    params = request.GET.copy()
    params['objects'] = selected_ids

    url = reverse_lazy("objects:generate_pdf", kwargs={"lang": "en"})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


class PdfView(CustomLoginRequiredMixin, View):

    def get(self, request, lang):
        selected_ids = self.request.GET.getlist("objects")
        object_type = int(self.request.GET.get("object_type"))

        pdf = generate_pdf(estate_objects_filter_visible(
                object_type=object_type,
                id__in=selected_ids
        ), request.user.get_full_name()[0])

        return FileResponse(
            io.BytesIO(pdf.output()),
            as_attachment=True,
            filename='document.pdf',
            content_type='application/pdf'
        )


class ShowingActView(TemplateView):
    template_name = "objects/showing_act.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_ids = self.request.GET.getlist("objects")
        object_type = int(self.request.GET.get("object_type"))

        context['lang'] = self.kwargs['lang']
        objects = []
        for obj in estate_objects_filter_visible(
                object_type=object_type,
                id__in=selected_ids
        ):
            objects.append({
                'object': obj,
                'image': obj.images.first(),
            })
        context['objects'] = objects

        return context


class RealEstateListRedirect(CustomLoginRequiredMixin, View):
    """
    Перенаправляє користувача на певну сторінку зі списком обʼєктів 
    в залежності від його прав для перегляду обʼєктів.
    """
    def get(self, request, *args, **kwargs):
        kwargs = {"lang": self.kwargs["lang"]}

        if user_can_view_apartment_list(self.request.user):
            return redirect(reverse_lazy("objects:apartment_list", kwargs=kwargs))

        if user_can_view_commerce_list(self.request.user):
            return redirect(reverse_lazy("objects:commerce_list", kwargs=kwargs))
        
        if user_can_view_house_list(self.request.user):
            return redirect(reverse_lazy("objects:house_list", kwargs=kwargs))
        
        raise PermissionDenied()


class ApartmentListView(CustomLoginRequiredMixin,
                        UserPassesTestMixin,
                        SaleListContextMixin,
                        ListView):
    """Список квартир."""
    template_name = "objects/real_estate_list.html"
    model = Apartment
    paginate_by = 5
    form_class = HandbooksSearchForm

    def test_func(self):
        return user_can_view_apartment_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []
            
            filters = {field: value 
                       for field, value in form.cleaned_data.items() 
                       if value != None}
        
        return apartment_filter_for_user(self.request.user.id, **filters)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "can_view_apartment": True,
            "can_view_commerce": user_can_view_commerce_list(self.request.user),
            "can_view_house": user_can_view_house_list(self.request.user),
            "can_create": user_can_create_apartment(self.request.user),
            "can_update": user_can_update_apartment_list(
                self.request.user, context["object_list"],
            ),
            "can_view_history": user_can_view_apartment_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_apartment",
            "update_url_name": "objects:update_apartment",
            "delete_url_name": "objects:delete_apartment",
            "real_estate_type": RealEstateType.APARTMENT
        })
        return context


class CommerceListView(CustomLoginRequiredMixin,
                       UserPassesTestMixin,
                       SaleListContextMixin,
                       ListView):
    """Список комерцій."""
    template_name = "objects/real_estate_list.html"
    model = Commerce
    paginate_by = 5
    form_class = HandbooksSearchForm

    def test_func(self):
        return user_can_view_commerce_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []
            
            filters = {field: value 
                       for field, value in form.cleaned_data.items() 
                       if value != None}
        
        return commerce_filter_for_user(self.request.user.id, **filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "can_view_apartment": user_can_view_apartment_list(self.request.user),
            "can_view_commerce": True,
            "can_view_house": user_can_view_house_list(self.request.user),
            "can_create": user_can_create_commerce(self.request.user),
            "can_update": user_can_update_commerce_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_commerce_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_commerce",
            "update_url_name": "objects:update_commerce",
            "delete_url_name": "objects:delete_commerce",
            "real_estate_type": RealEstateType.COMMERCE
        })
        return context


class HouseListView(CustomLoginRequiredMixin,
                    UserPassesTestMixin,
                    SaleListContextMixin,
                    ListView):
    """Список будинків."""
    template_name = "objects/real_estate_list.html"
    model = House
    paginate_by = 5
    form_class = HandbooksSearchForm

    def test_func(self):
        return user_can_view_house_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []
            
            filters = {field: value 
                       for field, value in form.cleaned_data.items() 
                       if value != None}
        
        return house_filter_for_user(self.request.user.id, **filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "can_view_apartment": user_can_view_apartment_list(self.request.user),
            "can_view_commerce": user_can_view_commerce_list(self.request.user),
            "can_view_house": True,
            "can_create": user_can_create_house(self.request.user),
            "can_update": user_can_update_house_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_house_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_house",
            "update_url_name": "objects:update_house",
            "delete_url_name": "objects:delete_house",
            "real_estate_type": RealEstateType.HOUSE
        })
        return context


class MyApartmentListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список квартир."""
    template_name = "objects/office_real_estate_list.html"
    model = Apartment
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_own_office_objects"

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return apartment_filter_by_user(self.request.user.id, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "form": self.form_class(self.request.GET),
            "can_create": user_can_create_apartment(self.request.user),
            "can_update": user_can_update_apartment_list(
                self.request.user, context["object_list"],
            ),
            "can_view_history": user_can_view_apartment_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_apartment",
            "update_url_name": "objects:update_apartment",
            "delete_url_name": "objects:delete_apartment",
            "real_estate_type": RealEstateType.APARTMENT
        })
        return context


class MyCommerceListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список комерцій."""
    template_name = "objects/office_real_estate_list.html"
    model = Commerce
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_own_office_objects"

    def test_func(self):
        return user_can_view_commerce_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return commerce_filter_for_user(self.request.user.id, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "form": self.form_class(self.request.GET),
            "can_create": user_can_create_commerce(self.request.user),
            "can_update": user_can_update_commerce_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_commerce_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_commerce",
            "update_url_name": "objects:update_commerce",
            "delete_url_name": "objects:delete_commerce",
            "real_estate_type": RealEstateType.COMMERCE
        })
        return context


class MyHouseListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список будинків."""
    template_name = "objects/office_real_estate_list.html"
    model = House
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_own_office_objects"

    def test_func(self):
        return user_can_view_house_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return house_filter_for_user(self.request.user.id, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "can_create": user_can_create_house(self.request.user),
            "can_update": user_can_update_house_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_house_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_house",
            "update_url_name": "objects:update_house",
            "delete_url_name": "objects:delete_house",
            "real_estate_type": RealEstateType.HOUSE
        })
        return context


class FilialApartmentListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список квартир."""
    template_name = "objects/office_filial_real_estate_list.html"
    model = Apartment
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def get_queryset(self):
        user = user_get(email=self.request.user)
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return apartment_filter_by_filial(user, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "form": self.form_class(self.request.GET),
            "can_create": user_can_create_apartment(self.request.user),
            "can_update": user_can_update_apartment_list(
                self.request.user, context["object_list"],
            ),
            "can_view_history": user_can_view_apartment_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_apartment",
            "update_url_name": "objects:update_apartment",
            "delete_url_name": "objects:delete_apartment",
            "real_estate_type": RealEstateType.APARTMENT
        })
        return context


class FilialCommerceListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список комерцій."""
    template_name = "objects/office_filial_real_estate_list.html"
    model = Commerce
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def test_func(self):
        return user_can_view_commerce_list(self.request.user)

    def get_queryset(self):
        user = user_get(email=self.request.user)
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return commerce_filter_by_filial(user, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "form": self.form_class(self.request.GET),
            "can_create": user_can_create_commerce(self.request.user),
            "can_update": user_can_update_commerce_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_commerce_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_commerce",
            "update_url_name": "objects:update_commerce",
            "delete_url_name": "objects:delete_commerce",
            "real_estate_type": RealEstateType.COMMERCE
        })
        return context


class FilialHouseListView(CustomLoginRequiredMixin,
                        StandardContextDataMixin,
                        PermissionRequiredMixin,
                        ListView):
    """Список будинків."""
    template_name = "objects/office_filial_real_estate_list.html"
    model = House
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def test_func(self):
        return user_can_view_house_list(self.request.user)

    def get_queryset(self):
        user = user_get(email=self.request.user)
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {field: value
                       for field, value in form.cleaned_data.items()
                       if value != None}

        return house_filter_by_filial(user, **filters)

    def get_context_data(self, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "can_create": user_can_create_house(self.request.user),
            "can_update": user_can_update_house_list(
                self.request.user, context["object_list"]
            ),
            "can_view_history": user_can_view_house_list_history(
                self.request.user, context["object_list"]
            ),
            "create_url_name": "objects:create_house",
            "update_url_name": "objects:update_house",
            "delete_url_name": "objects:delete_house",
            "real_estate_type": RealEstateType.HOUSE
        })
        return context


class ReportListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    template_name = "objects/report_list.html"
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
        activate(self.kwargs["lang"])
        context = super().get_context_data()
        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client",
                f'handbooks.view_filial_client'
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
        })
        return context


class ReportOfficeListView(HandbookWithFilterListMixin, ListView):
    model = Apartment
    template_name = "objects/office_report_list.html"
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
    permission_required = "objects.view_office_report"

    def get_queryset(self):
        return HandbookWithFilterListMixin.get_queryset(self)

    def get_context_data(self, *, object_list=None, **kwargs):
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        return context


class ContractListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment
    template_name = "objects/contract_list.html"
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
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
        })
        return context


class HistoryReportListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Apartment.history.all().model
    template_name = "objects/changes_report_list.html"
    handbook_type = 'report'
    filters = ['new_apartments', 'new_commerce', 'new_houses',
               'new_lands', 'new_rooms', 'changes', 'all_apartments', 'my_apartments', 'changes']
    queryset_filters = {'changes': Apartment.history.all(), }
    custom = True

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # переклад

        user = CustomUser.objects.filter(email=self.request.user).first()

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']

        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
        })

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
        apartments = get_all_apartment_history(order_by="history_date")
        commerces = get_all_commerce_history(order_by="history_date")
        houses = get_all_houses_history(order_by="history_date")
        context['object_list'] = sorted(chain(apartments, commerces, houses),
                                        key=lambda x: x.history_date,
                                        reverse=True)

        if context['object_list']:  # Якщо нам взагалі є з чим працювати
            context['object_values'] = []
            context['object_columns'] = ['id', 'date', 'user', 'field',
                                         'old_value', 'new_value']  # Назва стовпців
            for record in context['object_list']:
                if record.prev_record:
                    prev_record = record.prev_record
                    for field in record._meta.fields:
                        if field.name.find("history") == -1:
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
                                    'new_value': new_value,
                                    'model': record._meta.model_name[10::],
                                })
        else:
            context['object_columns'] = None
        return context


class OfficeHistoryReportListView(HandbookWithFilterListMixin, ListView):
    model = Apartment.history.all().model
    template_name = "objects/office_changes_report_list.html"
    handbook_type = 'report'
    filters = ['new_apartments', 'new_commerce', 'new_houses',
               'new_lands', 'new_rooms', 'changes', 'all_apartments', 'my_apartments', 'changes']
    queryset_filters = {'changes': Apartment.history.all(), }
    custom = True

    def get_context_data(self, *, object_list=None, **kwargs):

        user = CustomUser.objects.filter(email=self.request.user).first()

        # підгружаємо частину готової дати і додаємо що потрібно
        context = get_office_context(user, super().get_context_data(**kwargs))
        context['lang'] = self.kwargs['lang']

        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
        })

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
        apartments = get_all_apartment_history(order_by="history_date")
        commerces = get_all_commerce_history(order_by="history_date")
        houses = get_all_houses_history(order_by="history_date")
        context['object_list'] = sorted(chain(apartments, commerces, houses),
                                        key=lambda x: x.history_date,
                                        reverse=True)

        if context['object_list']:  # Якщо нам взагалі є з чим працювати
            context['object_values'] = []
            context['object_columns'] = ['id', 'date', 'user', 'field',
                                         'old_value', 'new_value']  # Назва стовпців
            for record in context['object_list']:
                if record.prev_record:
                    prev_record = record.prev_record
                    for field in record._meta.fields:
                        if field.name.find("history") == -1:
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
                                    'new_value': new_value,
                                    'model': record._meta.model_name[10::],
                                })
        else:
            context['object_columns'] = None
        return context


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
        return user_can_create_apartment(self.request.user)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
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
        kwargs = {"lang": self.kwargs["lang"]}
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
        return user_can_create_commerce(self.request.user)

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
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:commerce_list", kwargs=kwargs)
    

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
        return user_can_create_house(self.request.user)

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
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:house_list", kwargs=kwargs)


class ApartmentUpdateView(CustomLoginRequiredMixin,
                          UserPassesTestMixin,
                          RealEstateUpdateContextMixin,
                          UpdateView):
    """Форма редагування квартири."""
    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_apartment(self.request.user, self.kwargs["pk"])

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
        kwargs = {"lang": self.kwargs["lang"]}
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
        return user_can_update_commerce(self.request.user, self.kwargs["pk"])

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
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:commerce_list", kwargs=kwargs)


class HouseUpdateView(CustomLoginRequiredMixin,
                      UserPassesTestMixin,
                      RealEstateUpdateContextMixin,
                      UpdateView):
    """Форма редагування будинку."""
    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_house(self.request.user, self.kwargs["pk"])

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
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:house_list", kwargs=kwargs)


class ApartmentDeleteView(CustomLoginRequiredMixin,
                          UserPassesTestMixin,
                          DeleteView):
    """Видалення квартири."""
    template_name = "delete_form.html"
    model = Apartment

    def test_func(self):
        return user_can_update_apartment(self.request.user, self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class CommerceDeleteView(CustomLoginRequiredMixin,
                         UserPassesTestMixin,
                         DeleteView):
    """Видалення комерції."""
    template_name = "delete_form.html"
    model = Commerce

    def test_func(self):
        return user_can_update_commerce(self.request.user, self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:commerce_list", kwargs=kwargs)


class HouseDeleteView(CustomLoginRequiredMixin,
                      UserPassesTestMixin,
                      DeleteView):
    """Видалення будинку."""
    template_name = "delete_form.html"
    model = House

    def test_func(self):
        return user_can_update_house(self.request.user, self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:house_list", kwargs=kwargs)


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
                'image': obj.images.first()
            })
        context['objects'] = objects
        return context


class ApartmentDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = estate_objects_filter_visible(RealEstateType.APARTMENT)
    form_class = ApartmentForm
    model = Apartment

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs['disabled'] = True
            field.widget.attrs['readonly'] = True

        context["disabled"] = True

        return context


class CommerceDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = estate_objects_filter_visible(RealEstateType.COMMERCE)
    form_class = CommerceForm
    model = Commerce

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs['disabled'] = True
            field.widget.attrs['readonly'] = True

        context["disabled"] = True

        return context


class HouseDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = estate_objects_filter_visible(RealEstateType.HOUSE)
    form_class = HouseForm
    model = House

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs['disabled'] = True
            field.widget.attrs['readonly'] = True

        context["disabled"] = True

        return context


class ObjectHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = 'apartment'
