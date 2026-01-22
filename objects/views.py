import datetime
from itertools import chain
from urllib.parse import urlencode

from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    UpdateView,
    View, DetailView,
)

from handbooks.forms import SelectionForm
from handbooks.models import Client, Street
from images.forms import RealEstateImageFormSet

from .models import Apartment, Commerce, House, Land, Selection
from .utils import (
    real_estate_form_save,
    real_estate_form_filter
)
from utils.mixins.mixins import CustomLoginRequiredMixin
from utils.showing_act_pdf_service import ShowingActPDFService, ShowingActPDFType
from utils.views import HistoryView

from .choices import RealEstateStatus, RealEstateType, PermissionUpdateLevel
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
    RealEstateListContextMixin,
)

from .services import (
    user_can_update_real_estate,
    user_can_update_real_estate_list,
    real_estate_model_from_type,
    has_any_perm_from_list,
    selection_add_selected_objects,
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
            status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT)
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
    objects = model_class.objects.filter(
        ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
        id__in=selected_ids
    )
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
        qs = model_class.objects.filter(
            ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            id__in=selected_ids
        )
        objects = []
        for obj in qs:
            objects.append(
                {
                    "object": obj,
                    "image": obj.images.first(),
                }
            )
        context["objects"] = objects
        context["url"] = f"objects:{model_class._meta.model_name}_showing_act_details"

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
    objects = model_class.objects.filter(
        ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
        id__in=selected_ids
    )
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


class ShowingActPDFView(CustomLoginRequiredMixin, View):
    def get(self, request, lang):
        """Повертає pdf файл акту показу нерухомості"""
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
        objects = (
            model_class.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
                id__in=selected_ids
            )
            .select_related()
        )

        service = ShowingActPDFService()
        buffer = service.generate(ShowingActPDFType.SIMPLE, request.user, client, objects)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=showing_act.pdf"
        return response


class AccessibleApartmentListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, RealEstateListContextMixin, ListView
):
    """Список лише тих квартир, які доступні поточному користувачу для перегляду."""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    model = Apartment
    paginate_by = 5
    form_class = HandbooksSearchForm

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

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
            Apartment.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN), **filters
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        ordering = self.get_ordering()
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user,
                    context["object_list"],
                ),
                "create_url_name": "objects:create_apartment",
                "update_url_name": "objects:update_apartment",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class AccessibleCommerceListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, RealEstateListContextMixin, ListView
):
    """Список лише тих комерцій, які доступні поточному користувачу для перегляду."""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    model = Commerce
    paginate_by = 5
    form_class = HandbooksSearchForm

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

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
            Commerce.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN), **filters
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        ordering = self.get_ordering()
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_commerce",
                "update_url_name": "objects:update_commerce",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class AccessibleHouseListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, RealEstateListContextMixin, ListView
):
    """Список лише тих будинків, які доступні поточному користувачу для перегляду."""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    model = House
    paginate_by = 5
    form_class = HandbooksSearchForm

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

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
            House.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN), **filters
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        ordering = self.get_ordering()
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user, context["object_list"]
                ),
                "create_url_name": "objects:create_house",
                "update_url_name": "objects:update_house",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class AccessibleLandListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, RealEstateListContextMixin, ListView
):
    """Список квартир."""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    model = Land
    paginate_by = 5
    form_class = HandbooksSearchForm

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

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
            Land.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN), **filters
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "realtor__email")
        )
        ordering = self.get_ordering()
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user,
                    context["object_list"],
                ),
                "create_url_name": "objects:create_land",
                "update_url_name": "objects:update_land",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class HistoryReportListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "objects.view_changes_report"
    model = Apartment.history.all().model
    template_name = "objects/changes_report_list.html"
    handbook_type = "report"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # переклад

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
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
    PermissionRequiredMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
    """Сторінка створення квартири"""

    permission_required = "objects.add_own_real_estate"
    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_create_form.html"

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
    PermissionRequiredMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
    """Форма створення комерції"""

    permission_required = "objects.add_own_real_estate"
    model = Commerce
    form_class = CommerceForm
    template_name = "objects/real_estate_create_form.html"

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
    PermissionRequiredMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
    """Форма створення будинку"""

    permission_required = "objects.add_own_real_estate"
    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_create_form.html"

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
    PermissionRequiredMixin,
    RealEstateCreateContextMixin,
    DefaultUserInCreateViewMixin,
    CreateView,
):
    """Форма створення земельної ділянки"""

    permission_required = "objects.add_own_real_estate"
    model = Land
    form_class = LandForm
    template_name = "objects/real_estate_create_form.html"

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
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування квартири."""

    model = Apartment
    form_class = ApartmentForm
    template_name = "objects/real_estate_update_form.html"

    def get_object(self, queryset=None):
        """
        Перевіряє, чи може користувач редагувати дану квартиру;
        якщо перевірка проходить, повертає її
        """
        apartment = get_object_or_404(Apartment, id=self.kwargs["pk"])
        perm_update_level = user_can_update_real_estate(self.request.user, apartment)
        if perm_update_level == PermissionUpdateLevel.NONE:
            raise PermissionDenied(self.request.user.has_perm("objects.change_own_real_estate"))
        return apartment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.APARTMENT
        """
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
        """
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

    def form_invalid(self, form):
        user = self.request.user
        # замінити на
        # if user_can_update_real_estate(user, self.object) == PermissionUpdateLevel.PARTIAL
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and user_can_update_real_estate(user, self.object) != PermissionUpdateLevel.FULL:
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(self.object, field)
            f = self.form_class(post_data, instance=self.object)
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:apartment_list", kwargs=kwargs)


class CommerceUpdateView(
    CustomLoginRequiredMixin,
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування комерції."""

    model = Commerce
    form_class = CommerceForm
    template_name = "objects/real_estate_update_form.html"

    def get_object(self, queryset=None):
        """
        Перевіряє, чи може користувач редагувати дану комерцію;
        якщо перевірка проходить, повертає її
        """
        commerce = get_object_or_404(Commerce, id=self.kwargs["pk"])
        perm_update_level = user_can_update_real_estate(self.request.user, commerce)
        if perm_update_level == PermissionUpdateLevel.NONE:
            raise PermissionDenied()
        return commerce

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.COMMERCE
        """
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
        """
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

    def form_invalid(self, form):
        user = self.request.user
        # замінити на
        # if user_can_update_real_estate(user, self.object) == PermissionUpdateLevel.PARTIAL
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and user_can_update_real_estate(user, self.object) != PermissionUpdateLevel.FULL:
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(self.object, field)
            f = self.form_class(post_data, instance=self.object)
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
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування будинку."""

    model = House
    form_class = HouseForm
    template_name = "objects/real_estate_update_form.html"

    def get_object(self, queryset=None):
        """
        Перевіряє, чи може користувач редагувати даний будинок;
        якщо перевірка проходить, повертає його
        """
        house = get_object_or_404(House, id=self.kwargs["pk"])
        perm_update_level = user_can_update_real_estate(self.request.user, house)
        if perm_update_level == PermissionUpdateLevel.NONE:
            raise PermissionDenied()
        return house

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.HOUSE
        """
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
        """
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

    def form_invalid(self, form):
        user = self.request.user
        # замінити на
        # if user_can_update_real_estate(user, self.object) == PermissionUpdateLevel.PARTIAL
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and user_can_update_real_estate(user, self.object) != PermissionUpdateLevel.FULL:
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(self.object, field)
            f = self.form_class(post_data, instance=self.object)
            """for obj in House.objects.all():
                if obj.room_types >= 5:
                    obj.room_types = 4
                    obj.save()"""
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
    RealEstateUpdateContextMixin,
    UpdateView,
):
    """Форма редагування будинку."""

    model = Land
    form_class = LandForm
    template_name = "objects/real_estate_update_form.html"

    def get_object(self, queryset=None):
        """
        Перевіряє, чи може користувач редагувати дану земельну ділянку;
        якщо перевірка проходить, повертає її
        """
        land = get_object_or_404(Land, id=self.kwargs["pk"])
        perm_update_level = user_can_update_real_estate(self.request.user, land)
        if perm_update_level == PermissionUpdateLevel.NONE:
            raise PermissionDenied()
        return land

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = RealEstateType.LAND
        """
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
        """
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

    def form_invalid(self, form):
        user = self.request.user
        # замінити на
        # if user_can_update_real_estate(user, self.object) == PermissionUpdateLevel.PARTIAL
        if (
            user.has_perm("objects.change_object_comment")
            or user.has_perm("objects.change_object_price")
        ) and user_can_update_real_estate(user, self.object) != PermissionUpdateLevel.FULL:
            post_data = self.request.POST.copy()
            for field in self.form_class().fields.keys():
                if not post_data.get(field):
                    post_data[field] = getattr(self.object, field)
            f = self.form_class(post_data, instance=self.object)
            """for obj in Land.objects.all():
                if obj.room_types >= 5:
                    obj.room_types = 4
                    obj.save()"""
            if f.is_valid():
                f.save()
                return redirect(self.get_success_url())
        return super().form_invalid(form)

        return redirect(self.get_success_url())

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("objects:land_list", kwargs=kwargs)


class CatalogListView(ListView):
    paginate_by = 15
    template_name = "objects/catalog.html"
    queryset = Apartment.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
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
    queryset = Apartment.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
    form_class = ApartmentForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        context["form"].fields.pop("owner")
        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class CommerceDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = Commerce.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
    form_class = CommerceForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        context["form"].fields.pop("owner")
        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class HouseDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = House.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
    form_class = HouseForm

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        context["form"].fields.pop("owner")
        for field in context["form"].fields.values():
            field.widget.attrs["disabled"] = True
            field.widget.attrs["readonly"] = True

        context["disabled"] = True

        return context


class LandDetailView(UpdateView):
    template_name = "objects/real_estate_details_form.html"
    queryset = Land.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
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


class ApartmentShowingActDetailView(DetailView):
    template_name = "objects/real_estate_showing_act_detail.html"
    queryset = Apartment.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["type"] = "apartment"

        return context


class CommerceShowingActDetailView(DetailView):
    template_name = "objects/real_estate_showing_act_detail.html"
    queryset = Commerce.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["type"] = "commerce"

        return context


class HouseShowingActDetailView(DetailView):
    template_name = "objects/real_estate_showing_act_detail.html"
    queryset = House.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["type"] = "house"

        return context


class LandShowingActDetailView(DetailView):
    template_name = "objects/real_estate_showing_act_detail.html"
    queryset = Land.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["type"] = "land"

        return context


class ApartmentHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "objects.view_real_estate"
    handbook_type = "apartment"
    queryset = Apartment.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)


class CommerceHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "objects.view_real_estate"
    handbook_type = "commerce"
    queryset = Commerce.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)


class HouseHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "objects.view_real_estate"
    handbook_type = "house"
    queryset = House.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)


class LandHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "objects.view_real_estate"
    handbook_type = "land"
    queryset = Land.objects.exclude(status=RealEstateStatus.COMPLETELY_WITHDRAWN)
