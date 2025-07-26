import io
import datetime
from itertools import chain
from urllib.parse import urlencode

from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import redirect, get_object_or_404

from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from handbooks.forms import SelectionForm
from handbooks.models import Client, Street
from images.forms import RealEstateImageFormSet

from utils.utils import get_office_context
from .models import Apartment, Commerce, House, Land, Selection
from .utils import (
    real_estate_form_save,
    get_sale_report_list_context,
    get_sale_contract_list_context,
    real_estate_form_filter
)
from utils.mixins.mixins import (
    CustomLoginRequiredMixin,
)
from utils.pdf import showing_act_pdf
from utils.views import HistoryView

from .choices import RealEstateStatus, RealEstateType, ShowingActType
from .forms import (
    ApartmentForm,
    ApartmentVerifyAddressForm,
    CommerceForm,
    CommerceVerifyAddressForm,
    HandbooksSearchForm,
    HouseForm,
    HouseVerifyAddressForm,
    SearchForm,
    LandForm,
    RealEstateFilteringForm
)
from .mixins import (
    DefaultUserInCreateViewMixin,
    RealEstateCreateContextMixin,
    RealEstateUpdateContextMixin,
    SaleListContextMixin,
)

from .services import (
    apartment_accessible_for_user,
    commerce_accessible_for_user,
    house_accessible_for_user,
    land_accessible_for_user,
    reports_accessible_for_user,
    reports_accessible_for_user_in_office,
    contracts_accessible_for_user,
    real_estate_model_from_type,
    has_any_perm_from_list,
    selection_add_selected_objects,
    user_can_create_apartment,
    user_can_create_commerce,
    user_can_create_house,
    user_can_update_apartment,
    user_can_update_commerce,
    user_can_update_house,
    user_can_update_land,
    user_can_update_apartment_list,
    user_can_update_commerce_list,
    user_can_update_house_list,
    user_can_update_land_list,
    user_can_update_full_apartment,
    user_can_update_full_commerce,
    user_can_update_full_house,
    user_can_update_full_land,
    user_can_view_apartment_list,
    user_can_view_commerce_list,
    user_can_view_house_list,
    user_can_view_land_list,
    user_can_view_apartment_list_history,
    user_can_view_commerce_list_history,
    user_can_view_house_list_history,
    user_can_view_land_list_history,
    user_can_view_real_estate_list,
    user_can_view_report,
    user_can_view_office_report
)


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
        return JsonResponse(
            {
                "success": False,
                "errors": {"type": _("Invalid real estate type")},
            }
        )

    form = None

    if real_estate_type == RealEstateType.APARTMENT:
        form = ApartmentVerifyAddressForm(request.GET)
    elif real_estate_type == RealEstateType.COMMERCE:
        form = CommerceVerifyAddressForm(request.GET)
    elif real_estate_type == RealEstateType.HOUSE:
        form = HouseVerifyAddressForm(request.GET)

    if not form:
        return JsonResponse(
            {
                "success": False,
                "errors": {"type": _("Invalid real estate type")},
            }
        )

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            }
        )

    model_class = real_estate_model_from_type(real_estate_type)
    real_estate = model_class.objects.filter(**form.cleaned_data).only("id").first()
    if not real_estate:
        return JsonResponse(
            {
                "success": True,
                "message": _("Doesn't exist"),
            }
        )

    return JsonResponse(
        {
            "success": True,
            "message": _("Exists (id {id})").format(id=real_estate.id),
        }
    )


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
        street = Street.objects.select_related("locality_district__locality").get(
            pk=street_id, on_delete=False
        )
    except Street.DoesNotExist:
        return JsonResponse({"success": False, "locality": -1})

    return JsonResponse(
        {
            "success": True,
            "locality": street.locality_district.locality.pk,
        }
    )


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
        return JsonResponse(
            {
                "success": False,
                "errors": {"type": _("Invalid real estate type")},
            }
        )

    model_class = real_estate_model_from_type(real_estate_type)
    if not model_class:
        return JsonResponse(
            {
                "success": False,
                "errors": {"type": _("Invalid real estate type")},
            }
        )

    real_estate = get_object_or_404(model_class.objects.only("status"), id=id)
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
                "rooms_number": client.rooms_number,
                "locality": client.locality.all(),
                "locality_district": client.locality_district.all(),
                "street": client.street.all(),
                "house": client.house,
                "floor_min": client.floor_min,
                "floor_max": client.floor_max,
                "not_first": client.not_first,
                "not_last": client.not_last,
                "price_from": client.price_from,
                "price_to": client.price_to,
                "square_meter_price_max": client.square_meter_price_max,
                "condition": client.condition.all(),
                "object_type": client.object_type,
            }
            return SelectionForm(initial_data)
        return SelectionForm(self.request.GET)

    def get_queryset(self):
        client_id = self.kwargs.get("client_id")
        client = Client.objects.filter(id=client_id).first()

        if client.status == 1:
            client.status = 2
            client.save()

        form = self.get_form(client)
        form.is_valid()

        obj_type = int(form.cleaned_data.get("object_type"))
        model_class = real_estate_model_from_type(obj_type)
        if not model_class:
            raise BadRequest()
        
        queryset = model_class.objects.filter(
            on_delete=False, status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT)
        )

        # if form.cleaned_data.get('rooms_number') is not None:
        #     queryset = queryset.filter(rooms_number=form.cleaned_data.get('rooms_number'))
        if form.cleaned_data.get("locality").exists():
            queryset = queryset.filter(locality__in=form.cleaned_data.get("locality"))
        # if form.cleaned_data.get('locality_district').exists():
        #     queryset = queryset.filter(locality_district__in=form.cleaned_data.get('locality_district'))
        if form.cleaned_data.get("street").exists():
            queryset = queryset.filter(street__in=form.cleaned_data.get("street"))
        if (
            form.cleaned_data.get("house") is not None
            and form.cleaned_data.get("house") != ""
        ):
            queryset = queryset.filter(house=form.cleaned_data.get("house"))
        if form.cleaned_data.get("floor_min") is not None:
            queryset = queryset.filter(floor__gte=form.cleaned_data.get("floor_min"))
        if form.cleaned_data.get("floor_max") is not None:
            queryset = queryset.filter(floor__lte=form.cleaned_data.get("floor_max"))
        if form.cleaned_data.get("not_first"):
            queryset = queryset.exclude(floor=1)
            queryset = queryset.filter(
                storeys_number__lte=form.cleaned_data.get("storeys_num_max")
            )
        if form.cleaned_data.get("price_from") is not None:
            queryset = queryset.filter(price__gte=form.cleaned_data.get("price_from"))
        if form.cleaned_data.get("price_to") is not None:
            queryset = queryset.filter(price__lte=form.cleaned_data.get("price_to"))
        # if form.cleaned_data.get('square_meter_price_max') is not None:
        #     queryset = queryset.filter(
        #         square_meter_price__lte=form.cleaned_data.get('square_meter_price_max')
        #     )
        if form.cleaned_data.get("condition"):
            queryset = queryset.filter(condition__in=form.cleaned_data.get("condition"))

        if (
            form.cleaned_data.get("key_word") is not None
            and form.cleaned_data.get("key_word") != ""
        ):
            key_word = form.cleaned_data.get("key_word")
            queryset = queryset.filter(
                Q(region__region__icontains=key_word)
                | Q(district__district__icontains=key_word)
                | Q(locality__locality__icontains=key_word)
                | Q(locality_district__district__icontains=key_word)
                | Q(street__street__icontains=key_word)
                | Q(house__icontains=key_word)
                | Q(comment__icontains=key_word)
            )

        n_queryset = queryset
        for obj in n_queryset:
            if form.cleaned_data.get("not_last") and obj.storeys_number == obj.floor:
                n_queryset = n_queryset.exclude(id=obj.id)

        return n_queryset

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        client_id = self.kwargs.get("client_id")
        client = Client.objects.filter(id=client_id).first()

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["client"] = client

        context["form"] = self.get_form(client)

        objects = []
        for obj in context["objects"]:
            image = obj.images.first()
            objects.append({"image": image, "object": obj})
        context["objects"] = objects
        context["client"] = client

        return context


class SelectionHistoryView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    object_list = Selection.objects.all()
    permission_required = "objects.selection"
    template_name = "objects/selection_history_list.html"
    context_object_name = "objects"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        context = self.get_context_data()
        context["selections"] = Selection.objects.filter(client_id=pk)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context


def showing_act_redirect(request, lang):
    """
    Створення вибірки для клієнта та переадресація на сторінку з актом показу.
    Необхідні query параметри:
    - object_type: int # тип об'єкта нерухомості
    - objects: list[int] # список з id об'єктів
    - client: int # id клієнта
    """
    if request.user.is_anonymous:
        return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))

    object_type = int(request.GET.get("object_type"))
    model_class = real_estate_model_from_type(object_type)
    if not model_class:
        raise BadRequest()

    selected_ids = request.GET.getlist("objects")
    objects = model_class.objects.filter(on_delete=False, id__in=selected_ids)
    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = Client.objects.filter(on_delete=False, id=client_id).first()
    if not client:
        raise BadRequest()

    selection = Selection.objects.create(
        client=client,
        user=request.user,
    )
    selection_add_selected_objects(selection, object_type, *objects)
    selection.save()

    params = request.GET.copy()
    params["objects"] = selected_ids
    url = reverse_lazy("objects:showing_act", kwargs={"lang": lang})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


class ShowingActView(TemplateView):
    template_name = "objects/showing_act.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        object_type = int(self.request.GET.get("object_type"))
        model_class = real_estate_model_from_type(object_type)
        if not model_class:
            raise BadRequest()
        
        selected_ids = self.request.GET.getlist("objects")
        qs = model_class.objects.filter(on_delete=False, id__in=selected_ids)
        objects = []
        for obj in qs:
            objects.append(
                {
                    "object": obj,
                    "image": obj.images.first(),
                }
            )
        context["objects"] = objects
        return context


def pdf_redirect(request, lang):
    """
    Створення вибірки для клієнта та переадресація на сторінку
    зі створенням pdf-файлу з актом показу.
    Необхідні query параметри:
    - object_type: int # тип об'єкта нерухомості
    - objects: list[int] # список з id об'єктів
    - client: int # id клієнта
    """
    if request.user.is_anonymous:
        return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))

    object_type = int(request.GET.get("object_type"))
    model_class = real_estate_model_from_type(object_type)
    if not model_class:
        raise BadRequest()
    
    selected_ids = request.GET.getlist("objects")
    objects = model_class.objects.filter(on_delete=False, id__in=selected_ids)
    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = Client.objects.filter(on_delete=False, id=client_id).first()
    if not client:
        raise BadRequest()

    selection = Selection.objects.create(
        client=client,
        user=request.user,
    )
    selection_add_selected_objects(selection, object_type, *objects)
    selection.save()

    params = request.GET.copy()
    params["objects"] = selected_ids
    url = reverse_lazy("objects:generate_pdf", kwargs={"lang": lang})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


class ShowingActPdfView(CustomLoginRequiredMixin, View):
    def get(self, request, lang):
        activate(lang)
        client_id = int(request.GET.get("client"))
        client = Client.objects.filter(on_delete=False, id=client_id).first()
        if not client:
            raise BadRequest()

        object_type = int(self.request.GET.get("object_type"))
        model_class = real_estate_model_from_type(object_type)
        if not model_class:
            raise BadRequest()

        selected_ids = self.request.GET.getlist("objects")
        objects = model_class.objects.filter(on_delete=False, id__in=selected_ids).select_related()
        pdf = showing_act_pdf(request.user, client, objects, ShowingActType.WITH_USER_INFO)
        return FileResponse(
            io.BytesIO(pdf.output()),
            as_attachment=True,
            filename="document.pdf",
            content_type="application/pdf",
        )


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

        if user_can_view_land_list(self.request.user):
            return redirect(reverse_lazy("objects:land_list", kwargs=kwargs))

        raise PermissionDenied()


class AccessibleApartmentListView(
    CustomLoginRequiredMixin, UserPassesTestMixin, SaleListContextMixin, ListView
):
    """Список лише тих квартир, які доступні поточному користувачу для перегляду."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }
        
        qs = (
            Apartment.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        return apartment_accessible_for_user(self.request.user, qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_view_apartment": True,
                "can_view_commerce": user_can_view_commerce_list(self.request.user),
                "can_view_house": user_can_view_house_list(self.request.user),
                "can_view_land": user_can_view_land_list(self.request.user),
                "can_create": user_can_create_apartment(self.request.user),
                "can_update": user_can_update_apartment_list(
                    self.request.user,
                    context["object_list"],
                ),
                "can_view_history": user_can_view_apartment_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_apartment",
                "update_url_name": "objects:update_apartment",
                "delete_url_name": "objects:delete_apartment",
                "real_estate_type": RealEstateType.APARTMENT,
            }
        )
        return context


class AccessibleCommerceListView(
    CustomLoginRequiredMixin, UserPassesTestMixin, SaleListContextMixin, ListView
):
    """Список лише тих комерцій, які доступні поточному користувачу для перегляду."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }
        
        qs = (
            Commerce.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        return commerce_accessible_for_user(self.request.user, qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_view_apartment": user_can_view_apartment_list(self.request.user),
                "can_view_commerce": True,
                "can_view_house": user_can_view_house_list(self.request.user),
                "can_view_land": user_can_view_land_list(self.request.user),
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
                "real_estate_type": RealEstateType.COMMERCE,
            }
        )
        return context


class AccessibleHouseListView(
    CustomLoginRequiredMixin, UserPassesTestMixin, SaleListContextMixin, ListView
):
    """Список лише тих будинків, які доступні поточному користувачу для перегляду."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }
        
        qs = (
            House.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        return house_accessible_for_user(self.request.user, qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_view_apartment": user_can_view_apartment_list(self.request.user),
                "can_view_commerce": user_can_view_commerce_list(self.request.user),
                "can_view_house": True,
                "can_view_land": user_can_view_land_list(self.request.user),
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
                "real_estate_type": RealEstateType.HOUSE,
            }
        )
        return context


class AccessibleLandListView(
    CustomLoginRequiredMixin, UserPassesTestMixin, SaleListContextMixin, ListView
):
    """Список квартир."""

    template_name = "objects/real_estate_list.html"
    model = Land
    paginate_by = 5
    form_class = HandbooksSearchForm

    def test_func(self):
        return has_any_perm_from_list(
            self.request.user,
            "objects.view_land",
            "objects.view_own_land",
            "objects.view_filial_land",
        )

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Land.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        return land_accessible_for_user(self.request.user, qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_view_apartment": user_can_view_apartment_list(self.request.user),
                "can_view_commerce": user_can_view_commerce_list(self.request.user),
                "can_view_house": user_can_view_house_list(self.request.user),
                "can_view_land": True,
                "can_create": has_any_perm_from_list(
        self.request.user, "objects.add_land", "objects.add_own_land"
    ),
                "can_update": user_can_update_land_list(
                    self.request.user,
                    context["object_list"],
                ),
                "can_view_history": user_can_view_land_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_land",
                "update_url_name": "objects:update_land",
                "delete_url_name": "objects:delete_land",
                "real_estate_type": RealEstateType.LAND,
            }
        )
        return context


class OfficeMyApartmentListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """Список власних квартир поточного користувача в офісі."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Apartment.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        return qs.filter(realtor=self.request.user)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
                "form": self.form_class(self.request.GET),
                "can_create": user_can_create_apartment(self.request.user),
                "can_update": user_can_update_apartment_list(
                    self.request.user,
                    context["object_list"],
                ),
                "can_view_history": user_can_view_apartment_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_apartment",
                "update_url_name": "objects:update_apartment",
                "delete_url_name": "objects:delete_apartment",
                "real_estate_type": RealEstateType.APARTMENT,
            }
        )
        return context


class OfficeMyCommerceListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """Список власних комерцій поточного користувача в офісі."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Commerce.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        return qs.filter(realtor=self.request.user)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
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
                "real_estate_type": RealEstateType.COMMERCE,
            }
        )
        return context


class OfficeMyHouseListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """Список власних будинків поточного користувача в офісі."""

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

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            House.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        return qs.filter(realtor=self.request.user)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
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
                "real_estate_type": RealEstateType.HOUSE,
            }
        )
        return context


class OfficeMyLandListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """Список земельних ділянок."""

    template_name = "objects/office_real_estate_list.html"
    model = Land
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_own_office_objects"

    def test_func(self):
        return user_can_view_land_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Land.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        return qs.filter(realtor=self.request.user)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
                "can_create": has_any_perm_from_list(self.request.user, "objects.add_land",
                                                     "objects.add_own_land"),
                "can_update": user_can_update_land_list(
                    self.request.user, context["object_list"]
                ),
                "can_view_history": user_can_view_land_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_land",
                "update_url_name": "objects:update_land",
                "delete_url_name": "objects:delete_land",
                "real_estate_type": RealEstateType.LAND,
            }
        )
        return context


class OfficeFilialApartmentListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """
    Список лише тих квартир  в офісі, рієлтори яких належать до тих же філіалів,
    що й поточний користувач.
    """

    template_name = "objects/office_filial_real_estate_list.html"
    model = Apartment
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }
        
        qs = (
            Apartment.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        user_filials = self.request.user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
                "form": self.form_class(self.request.GET),
                "can_create": user_can_create_apartment(self.request.user),
                "can_update": user_can_update_apartment_list(
                    self.request.user,
                    context["object_list"],
                ),
                "can_view_history": user_can_view_apartment_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_apartment",
                "update_url_name": "objects:update_apartment",
                "delete_url_name": "objects:delete_apartment",
                "real_estate_type": RealEstateType.APARTMENT,
            }
        )
        return context


class OfficeFilialCommerceListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """
    Список лише тих комерцій  в офісі, рієлтори яких належать до тих же філіалів,
    що й поточний користувач.
    """

    template_name = "objects/office_filial_real_estate_list.html"
    model = Commerce
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def test_func(self):
        return user_can_view_commerce_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Commerce.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        user_filials = self.request.user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
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
                "real_estate_type": RealEstateType.COMMERCE,
            }
        )
        return context


class OfficeFilialHouseListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """
    Список лише тих будинків  в офісі, рієлтори яких належать до тих же філіалів,
    що й поточний користувач.
    """

    template_name = "objects/office_filial_real_estate_list.html"
    model = House
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def test_func(self):
        return user_can_view_house_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            House.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        user_filials = self.request.user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
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
                "real_estate_type": RealEstateType.HOUSE,
            }
        )
        return context


class OfficeFilialLandListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    """Список будинків."""

    template_name = "objects/office_filial_real_estate_list.html"
    model = Land
    paginate_by = 5
    form_class = HandbooksSearchForm
    permission_required = "objects.view_filial_office_objects"

    def test_func(self):
        return user_can_view_land_list(self.request.user)

    def get_queryset(self):
        filters = {}
        if "id" in self.request.GET:
            form = self.form_class(self.request.GET)
            if not form.is_valid():
                return []

            filters = {
                field: value
                for field, value in form.cleaned_data.items()
                if value is not None
            }

        qs = (
            Land.objects.filter(on_delete=False, **filters)
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )

        user_filials = self.request.user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context.update(get_office_context(self.request.user))
        context.update(
            {
                "can_create": has_any_perm_from_list(self.request.user, "objects.add_land", "objects.add_own_land"),
                "can_update": user_can_update_land_list(
                    self.request.user, context["object_list"]
                ),
                "can_view_history": user_can_view_land_list_history(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_land",
                "update_url_name": "objects:update_land",
                "delete_url_name": "objects:delete_land",
                "real_estate_type": RealEstateType.LAND,
            }
        )
        return context


class NewAccessibleApartmentReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів квартир"""

    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class NewAccessibleCommerceReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів комерцій"""

    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Commerce.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class NewAccessibleLandReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів будинків"""

    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = Land.objects.filter(on_delete=False)
        qs = reports_accessible_for_user(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class NewAccessibleHouseReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів будинків"""

    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            House.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class AllApartmentReportListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Список всіх звітів квартир"""

    permission_required = "objects.view_report"
    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        self._form = RealEstateFilteringForm(self.request.GET)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class MyApartmentReportListView(CustomLoginRequiredMixin, ListView):
    """Список звітів квартир, які належать користувачу"""

    permission_required = "objects.view_own_report"
    template_name = "objects/report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        self._form = RealEstateFilteringForm(self.request.GET)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False, realtor=self.request.user)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        report_list_context = get_sale_report_list_context(
            self.kwargs["lang"], self.request.user, self._form
        )
        context.update(report_list_context)
        return context


class OfficeNewAccessibleApartmentReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів квартир в офісі"""

    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user_in_office(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class OfficeNewAccessibleCommerceReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів комерцій в офісі"""

    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Commerce.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user_in_office(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class OfficeNewAccessibleHouseReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів будинків в офісі"""

    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            House.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        qs = reports_accessible_for_user_in_office(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class OfficeNewAccessibleLandReportListView(CustomLoginRequiredMixin, ListView):
    """Список нових, доступних користувачу для перегляду, звітів будинків в офісі"""

    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        form_data = self.request.GET.copy()
        if "creation_date_min" not in form_data:
            creation_date_min = datetime.datetime.today() - datetime.timedelta(days=30)
            form_data["creation_date_min"] = creation_date_min

        self._form = RealEstateFilteringForm(form_data)
        if not self._form.is_valid():
            raise BadRequest()

        qs = Land.objects.filter(on_delete=False)
        qs = reports_accessible_for_user_in_office(self.request.user, qs)
        return real_estate_form_filter(qs, self._form.cleaned_data)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class OfficeAllApartmentReportListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Список всіх звітів квартир в офісі"""

    permission_required = "objects.view_office_report"
    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        self._form = RealEstateFilteringForm(self.request.GET)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class OfficeMyApartmentReportListView(CustomLoginRequiredMixin, ListView):
    """Список звітів квартир, які належать користувачу в офісі"""

    permission_required = "objects.view_office_own_report"
    template_name = "objects/office_report_list.html"
    paginate_by = 10

    _form: RealEstateFilteringForm

    def get_queryset(self):
        self._form = RealEstateFilteringForm(self.request.GET)
        if not self._form.is_valid():
            raise BadRequest()

        qs = (
            Apartment.objects.filter(on_delete=False, realtor=self.request.user)
            .select_related("locality", "street", "owner")
            .only("locality__locality", "street__street", "owner__email", "owner__first_name", "owner__last_name")
        )
        return real_estate_form_filter(qs, self._form.cleaned_data)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self._form,
        })
        context.update(get_office_context(self.request.user))
        return context


class AccessibleApartmentContractListView(CustomLoginRequiredMixin, ListView):
    """
    Список лише тих контрактів по квартирах, які доступні
    поточному користувачу для перегляду.
    """
    template_name = "objects/contract_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Apartment.objects.filter(on_delete=False)
        return contracts_accessible_for_user(self.request.user, qs)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data()
        context.update(
            get_sale_contract_list_context(self.kwargs["lang"], self.request.user)
        )
        return context


class AccessibleCommerceContractListView(CustomLoginRequiredMixin, ListView):
    """
    Список лише тих контрактів по комерціям, які доступні
    поточному користувачу для перегляду.
    """
    template_name = "objects/contract_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Commerce.objects.filter(on_delete=False)
        return contracts_accessible_for_user(self.request.user, qs)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data()
        context.update(
            get_sale_contract_list_context(self.kwargs["lang"], self.request.user)
        )
        return context


class AccessibleHouseContractListView(CustomLoginRequiredMixin, ListView):
    """
    Список лише тих контрактів по будинках, які доступні
    поточному користувачу для перегляду.
    """
    template_name = "objects/contract_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = House.objects.filter(on_delete=False)
        return contracts_accessible_for_user(self.request.user, qs)
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data()
        context.update(
            get_sale_contract_list_context(self.kwargs["lang"], self.request.user)
        )
        return context


class HistoryReportListView(CustomLoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Apartment.history.all().model
    template_name = "objects/changes_report_list.html"
    handbook_type = "report"
    paginate_by = 5

    def test_func(self):
        return user_can_view_report(self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # переклад

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        context.update(
            {
                "can_view_client": has_any_perm_from_list(
                    self.request.user,
                    "handbooks.view_client",
                    "handbooks.view_own_client",
                ),
                "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
                "can_view_report": self.request.user.has_perm("objects.view_report"),
                "can_view_contract": self.request.user.has_perm("objects.view_contract")
                                     or self.request.user.has_perm("objects.view_filial_contract")
                                     or self.request.user.has_perm("objects.view_own_contract"),
            }
        )
        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_filial_report": self.request.user.has_perm("objects.view_filial_report"),
            "can_view_own_report": self.request.user.has_perm("objects.view_own_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract")
                                 or self.request.user.has_perm("objects.view_filial_contract")
                                 or self.request.user.has_perm("objects.view_own_contract"),
        })

        context["choice"] = self.handbook_type

        apartments = Apartment.history.all().order_by("history_date")
        commerces = Commerce.history.all().order_by("history_date")
        houses = House.history.all().order_by("history_date")
        lands = Land.history.all().order_by("history_date")
        context["object_list"] = sorted(
            chain(apartments, commerces, houses, lands),
            key=lambda x: x.history_date,
            reverse=True,
        )

        if context["object_list"]:  # Якщо нам взагалі є з чим працювати
            context["object_values"] = []
            for record in context["object_list"]:
                if record.prev_record:
                    prev_record = record.prev_record
                    for field in record._meta.fields:
                        if field.name.find("history") == -1:
                            field_name = field.name
                            old_value = getattr(prev_record, field_name)
                            new_value = getattr(record, field_name)
                            if old_value != new_value:
                                context["object_values"].append(
                                    {
                                        "id": record.id,
                                        "date": record.history_date,
                                        "user": record.history_user,
                                        "field": field.verbose_name,
                                        "old_value": old_value,
                                        "new_value": new_value,
                                        "model": record._meta.model_name[10::],
                                    }
                                )
        else:
            context["object_values"] = None
        return context


class OfficeHistoryReportListView(CustomLoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Apartment.history.all().model
    template_name = "objects/office_changes_report_list.html"
    handbook_type = "report"
    paginate_by = 5

    def test_func(self):
        return user_can_view_office_report(self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # переклад

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        context.update(
            {
                "can_view_client": has_any_perm_from_list(
                    self.request.user,
                    "handbooks.view_client",
                    "handbooks.view_own_client",
                ),
                "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
                "can_view_report": self.request.user.has_perm("objects.view_report"),
                "can_view_contract": self.request.user.has_perm("objects.view_contract")
                                     or self.request.user.has_perm("objects.view_filial_contract")
                                     or self.request.user.has_perm("objects.view_own_contract"),
            }
        )
        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_filial_report": self.request.user.has_perm("objects.view_filial_report"),
            "can_view_own_report": self.request.user.has_perm("objects.view_own_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract")
                                 or self.request.user.has_perm("objects.view_filial_contract")
                                 or self.request.user.has_perm("objects.view_own_contract"),
        })

        context["choice"] = self.handbook_type

        apartments = Apartment.history.all().order_by("history_date")
        commerces = Commerce.history.all().order_by("history_date")
        houses = House.history.all().order_by("history_date")
        lands = Land.history.all().order_by("history_date")
        context["object_list"] = sorted(
            chain(apartments, commerces, houses, lands),
            key=lambda x: x.history_date,
            reverse=True,
        )

        if context["object_list"]:  # Якщо нам взагалі є з чим працювати
            context["object_values"] = []
            for record in context["object_list"]:
                if record.prev_record:
                    prev_record = record.prev_record
                    for field in record._meta.fields:
                        if field.name.find("history") == -1:
                            field_name = field.name
                            old_value = getattr(prev_record, field_name)
                            new_value = getattr(record, field_name)
                            if old_value != new_value:
                                context["object_values"].append(
                                    {
                                        "id": record.id,
                                        "date": record.history_date,
                                        "user": record.history_user,
                                        "field": field.verbose_name,
                                        "old_value": old_value,
                                        "new_value": new_value,
                                        "model": record._meta.model_name[10::],
                                    }
                                )
        else:
            context["object_values"] = None
        return context


class ApartmentCreateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
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


class CommerceCreateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
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


class HouseCreateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
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


class LandCreateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
    """
    Форма створення нової квартири.
    Для доступу до цієї сторінки потрібно мати право
    objects.add_apartment або objects.add_own_apartment.
    """

    model = Land
    form_class = LandForm
    template_name = "objects/real_estate_create_form.html"

    def test_func(self):
        return has_any_perm_from_list(
            self.request.user, "objects.add_land", "objects.add_own_land"
        )

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.LAND

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
        return reverse_lazy("objects:land_list", kwargs=kwargs)


class ApartmentUpdateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування квартири."""

    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_apartment(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.APARTMENT

        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_apartment(user, self.kwargs["pk"]):
            for name, field in context["form"].fields.items():
                if (
                    not (
                        name == "comment"
                        and self.request.user.has_perm("objects.change_object_comment")
                    )
                ) and (
                    not (
                        name == "price"
                        and self.request.user.has_perm("objects.change_object_price")
                    )
                ):
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True
            for form in context["formset"].forms:
                for name, field in form.fields.items():
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True

        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_apartment(user, self.kwargs["pk"]):
            o = self.get_object()
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(o, field)
            f = self.form_class(post_data, instance=o)
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class CommerceUpdateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування комерції."""

    model = Commerce
    form_class = CommerceForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_commerce(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.COMMERCE

        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_commerce(user, self.kwargs["pk"]):
            for name, field in context["form"].fields.items():
                if (
                    not (
                        name == "comment"
                        and self.request.user.has_perm("objects.change_object_comment")
                    )
                ) and (
                    not (
                        name == "price"
                        and self.request.user.has_perm("objects.change_object_price")
                    )
                ):
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True
            for form in context["formset"].forms:
                for name, field in form.fields.items():
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True

        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_commerce(user, self.kwargs["pk"]):
            o = self.get_object()
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(o, field)
            f = self.form_class(post_data, instance=o)
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:commerce_list", kwargs=kwargs)


class HouseUpdateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування будинку."""

    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_house(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.HOUSE

        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_house(user, self.kwargs["pk"]):
            for name, field in context["form"].fields.items():
                if (
                    not (
                        name == "comment"
                        and self.request.user.has_perm("objects.change_object_comment")
                    )
                ) and (
                    not (
                        name == "price"
                        and self.request.user.has_perm("objects.change_object_price")
                    )
                ):
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True
            for form in context["formset"].forms:
                for name, field in form.fields.items():
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True

        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_house(user, self.kwargs["pk"]):
            o = self.get_object()
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(o, field)
            f = self.form_class(post_data, instance=o)
            for obj in House.objects.all():
                if obj.room_types >= 5:
                    obj.room_types = 4
                    obj.save()
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:house_list", kwargs=kwargs)


class LandUpdateView(
    CustomLoginRequiredMixin,
    UserPassesTestMixin,
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування будинку."""

    model = Land
    form_class = LandForm
    template_name = "objects/real_estate_update_form.html"

    def test_func(self):
        return user_can_update_land(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.LAND

        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_land(user, self.kwargs["pk"]):
            for name, field in context["form"].fields.items():
                if (
                    not (
                        name == "comment"
                        and self.request.user.has_perm("objects.change_object_comment")
                    )
                ) and (
                    not (
                        name == "price"
                        and self.request.user.has_perm("objects.change_object_price")
                    )
                ):
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True
            for form in context["formset"].forms:
                for name, field in form.fields.items():
                    field.widget.attrs["disabled"] = True
                    field.widget.attrs["readonly"] = True

        return context

    def form_valid(self, form):
        _, is_saved = real_estate_form_save(
            form,
            RealEstateImageFormSet,
            self.request.POST,
            self.request.FILES,
            instance=self.get_object(),
        )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        user = self.request.user
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and not user_can_update_full_land(user, self.kwargs["pk"]):
            o = self.get_object()
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(o, field)
            f = self.form_class(post_data, instance=o)
            for obj in Land.objects.all():
                if obj.room_types >= 5:
                    obj.room_types = 4
                    obj.save()
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:land_list", kwargs=kwargs)


class ApartmentDeleteView(CustomLoginRequiredMixin, UserPassesTestMixin, DeleteView):
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


class CommerceDeleteView(CustomLoginRequiredMixin, UserPassesTestMixin, DeleteView):
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


class HouseDeleteView(CustomLoginRequiredMixin, UserPassesTestMixin, DeleteView):
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


class LandDeleteView(CustomLoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Видалення будинку."""

    template_name = "delete_form.html"
    model = Land

    def test_func(self):
        return user_can_update_land(self.request.user, self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:land_list", kwargs=kwargs)


class CatalogListView(ListView):
    paginate_by = 15
    template_name = "objects/catalog.html"
    queryset = Apartment.objects.filter(on_delete=False)
    context_object_name = "objects"

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data.get("locality"):
                queryset = queryset.filter(
                    locality__locality__icontains=form.cleaned_data["locality"]
                )
            if form.cleaned_data.get("street"):
                queryset = queryset.filter(
                    street__street__icontains=form.cleaned_data["street"]
                )
            if form.cleaned_data.get("price_min"):
                queryset = queryset.filter(price__gte=form.cleaned_data["price_min"])
            if form.cleaned_data.get("price_max"):
                queryset = queryset.filter(price__lte=form.cleaned_data["price_max"])

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)

        context["lang"] = self.kwargs["lang"]
        context["form"] = SearchForm(self.request.GET)

        objects = []
        for obj in context["objects"]:
            objects.append({"object": obj, "image": obj.images.first()})
        context["objects"] = objects
        return context


class ApartmentDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = Apartment.objects.filter(on_delete=False)
    form_class = ApartmentForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class CommerceDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = Commerce.objects.filter(on_delete=False)
    form_class = CommerceForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class HouseDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = House.objects.filter(on_delete=False)
    form_class = HouseForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class LandDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = Land.objects.filter(on_delete=False)
    form_class = LandForm
    model = Land

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class ApartmentHistoryView(CustomLoginRequiredMixin, UserPassesTestMixin, HistoryView):
    handbook_type = "apartment"
    queryset = Apartment.objects.filter(on_delete=False)

    def test_func(self):
        return user_can_view_apartment_list_history(
            self.request.user, Apartment.objects.filter(id=self.kwargs["pk"])
        )


class CommerceHistoryView(CustomLoginRequiredMixin, UserPassesTestMixin, HistoryView):
    handbook_type = "commerce"
    queryset = Commerce.objects.filter(on_delete=False)

    def test_func(self):
        return user_can_view_commerce_list_history(
            self.request.user, Commerce.objects.filter(id=self.kwargs["pk"])
        )


class HouseHistoryView(CustomLoginRequiredMixin, UserPassesTestMixin, HistoryView):
    handbook_type = "house"
    queryset = House.objects.filter(on_delete=False)

    def test_func(self):
        return user_can_view_house_list_history(
            self.request.user, House.objects.filter(id=self.kwargs["pk"])
        )


class LandHistoryView(CustomLoginRequiredMixin, UserPassesTestMixin, HistoryView):
    handbook_type = "land"
    queryset = Land.objects.filter(on_delete=False)

    def test_func(self):
        return user_can_view_land_list_history(
            self.request.user, Land.objects.filter(id=self.kwargs["pk"])
        )
