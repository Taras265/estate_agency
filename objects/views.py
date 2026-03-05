from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext_lazy as _
from django.views.decorators.http import require_GET
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
)

from images.forms import RealEstateImageFormSet
from .models import Apartment, Commerce, House, Land
from .utils import real_estate_form_save
from utils.mixins.mixins import CustomLoginRequiredMixin, CustomPaginateOnPageMixin
from utils.views import HistoryView
from .choices import RealEstateStatus, RealEstateType, PermissionUpdateLevel
from .forms import (
    ApartmentForm,
    ApartmentVerifyAddressForm,
    ApartmentSearchForm,
    CommerceForm,
    CommerceVerifyAddressForm,
    CommerceSearchForm,
    HouseForm,
    HouseVerifyAddressForm,
    HouseSearchForm,
    SearchForm,
    LandForm,
    LandSearchForm,
    RealEstateHistorySearchForm,
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
    process_real_estate_search_form,
    process_real_estate_history_search_form,
    real_estate_history_changes,
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


class ApartmentListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomPaginateOnPageMixin,
    RealEstateListContextMixin, ListView
):
    """Список квартир"""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    form = None
    paginate_by = 10

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

    def get_queryset(self):
        if "id" in self.request.GET:
            # форма була відправлена
            self.form = ApartmentSearchForm(self.request.GET)
        else:
            # форма не була відправлена,
            # користувач перейшов на сторінку по посиланню
            self.form = ApartmentSearchForm({
                "status": [RealEstateStatus.ON_SALE],
                "whose_real_estate": "my"
            })

        if not self.form.is_valid():
            return []

        qs = (
            Apartment.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "rubric", "on_site", "realtor__email")
        )
        qs = process_real_estate_search_form(qs, self.form, self.request.user)
        if (ordering := self.get_ordering()):
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
                "form": self.form,
                "create_url_name": "objects:create_apartment",
                "update_url_name": "objects:update_apartment",
                "view_url_name": "objects:apartment_detail",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class CommerceListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomPaginateOnPageMixin,
    RealEstateListContextMixin, ListView
):
    """Список комерцій"""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    paginate_by = 10
    form = None

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

    def get_queryset(self):
        if "id" in self.request.GET:
            # форма була відправлена
            self.form = CommerceSearchForm(self.request.GET)
        else:
            # форма не була відправлена,
            # користувач перейшов на сторінку по посиланню
            self.form = CommerceSearchForm({
                "status": [RealEstateStatus.ON_SALE],
                "whose_real_estate": "my"
            })

        if not self.form.is_valid():
            return []

        qs = (
            Commerce.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "rubric", "on_site", "realtor__email")
        )
        qs = process_real_estate_search_form(qs, self.form, self.request.user)
        if (ordering := self.get_ordering()):
            qs = qs.order_by(ordering)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user, context["object_list"]
                ),
                "form": self.form,
                "create_url_name": "objects:create_commerce",
                "update_url_name": "objects:update_commerce",
                "view_url_name": "objects:commerce_detail",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class HouseListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomPaginateOnPageMixin,
    RealEstateListContextMixin, ListView
):
    """Список будинків"""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    paginate_by = 10

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

    def get_queryset(self):
        if "id" in self.request.GET:
            # форма була відправлена
            self.form = HouseSearchForm(self.request.GET)
        else:
            # форма не була відправлена,
            # користувач перейшов на сторінку по посиланню
            self.form = HouseSearchForm({
                "status": [RealEstateStatus.ON_SALE],
                "whose_real_estate": "my"
            })

        if not self.form.is_valid():
            return []

        qs = (
            House.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "rubric", "on_site", "realtor__email")
        )
        qs = process_real_estate_search_form(qs, self.form, self.request.user)
        if (ordering := self.get_ordering()):
            qs = qs.order_by(ordering)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "can_update": user_can_update_real_estate_list(
                    self.request.user, context["object_list"]
                ),
                "form": self.form,
                "create_url_name": "objects:create_house",
                "update_url_name": "objects:update_house",
                "view_url_name": "objects:house_detail",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class LandListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomPaginateOnPageMixin,
    RealEstateListContextMixin, ListView
):
    """Список земельних ділянок"""

    permission_required = "objects.view_real_estate"
    template_name = "objects/real_estate_list.html"
    paginate_by = 10

    def get_ordering(self):
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("direction")
        if sort and direction in ["s", "d"]:
            return sort if direction == "s" else f"-{sort}"
        return None

    def get_queryset(self):
        if "id" in self.request.GET:
            # форма була відправлена
            self.form = LandSearchForm(self.request.GET)
        else:
            # форма не була відправлена,
            # користувач перейшов на сторінку по посиланню
            self.form = LandSearchForm({
                "status": [RealEstateStatus.ON_SALE],
                "whose_real_estate": "my"
            })

        if not self.form.is_valid():
            return []

        qs = (
            Land.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            )
            .select_related("locality", "street", "realtor")
            .only("id", "locality__locality", "street__street", "rubric", "on_site", "realtor__email")
        )
        qs = process_real_estate_search_form(qs, self.form, self.request.user)
        if (ordering := self.get_ordering()):
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
                "form": self.form,
                "create_url_name": "objects:create_land",
                "update_url_name": "objects:update_land",
                "view_url_name": "objects:land_detail",
                "sort": self.request.GET.get("sort"),
                "direction": self.request.GET.get("direction"),
            }
        )
        return context


class RealEstateHistoryListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    CustomPaginateOnPageMixin,
    ListView
):
    permission_required = "objects.view_changes_report"
    template_name = "objects/changes_report_list.html"
    form = None
    paginate_by = 10

    def get_queryset(self, queryset=None):
        user = self.request.user
        if "real_estate_type" in self.request.GET:
            self.form = RealEstateHistorySearchForm(user, self.request.GET)
        else:
            self.form = RealEstateHistorySearchForm(user, {
                "real_estate_type": RealEstateType.APARTMENT,
                "whose_real_estate": "my"
            })

        if not self.form.is_valid():
            return []

        model = real_estate_model_from_type(self.form.cleaned_data["real_estate_type"])
        history_qs = model.history.select_related("history_user")
        history_qs = process_real_estate_history_search_form(history_qs, self.form, user)
        return real_estate_history_changes(history_qs)

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form" : self.form
        })
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
        context["history_url"] = "objects:history_apartment"
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
        context["history_url"] = "objects:history_commerce"
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
        context["history_url"] = "objects:history_house"
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
        context["history_url"] = "objects:history_land"
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
