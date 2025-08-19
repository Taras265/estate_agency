from dateutil.relativedelta import relativedelta
from django.views.generic import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate

from handbooks.forms import (
    ClientForm,
    DistrictForm,
    FilialForm,
    FilialReportForm,
    HandbookForm,
    LocalityDistrictForm,
    LocalityForm,
    RegionForm,
    StreetForm,
    IdSearchForm,
)
from handbooks.models import (
    Region,
    District,
    Locality,
    Street,
    LocalityDistrict,
    Client,
    FilialAgency,
    FilialReport,
    Handbook,
)
from handbooks.choices import ClientStatusType
from objects.services import user_can_view_real_estate_list, user_can_view_report
from utils.const import BASE_CHOICES, SALE_CHOICES
from utils.mixins.mixins import (
    ByUserMixin,
    ClientListMixin,
    CustomLoginRequiredMixin,
    FilialClientListMixin,
    SearchByIdMixin,
    UserClientListMixin,
)
from utils.views import (
    CustomCreateView,
    CustomDeleteView,
    CustomUpdateView,
    HistoryView,
    CustomListView,
    NewCustomHandbookListView,
)


def handbook_redirect(request, lang):
    # Функція, яка перебрасує користувача на довідник,
    # з яким він моєе взаємодіяти
    kwargs = {"lang": lang}

    if request.user:
        for choice in BASE_CHOICES:
            if request.user.has_perm(f"handbooks.view_{choice}"):
                return redirect(
                    reverse_lazy(f"handbooks:{choice}_list", kwargs=kwargs)
                )
        return render(request, "403.html", kwargs)
    return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))


def sale_redirect(request, lang):
    kwargs = {"lang": lang}
    if request.user:
        if user_can_view_real_estate_list(request.user):
            return redirect(
                reverse_lazy("objects:real_estate_list_redirect", kwargs=kwargs)
            )
        elif (
            request.user.has_perm("handbooks.view_client")
            or request.user.has_perm("handbooks.view_own_client")
            or request.user.has_perm("handbooks.view_filial_client")
        ):
            return redirect(reverse_lazy("handbooks:client_list", kwargs=kwargs))
        elif user_can_view_report(request.user):
            return redirect(reverse_lazy("objects:report_list", kwargs=kwargs))
        elif request.user.has_perm("objects.view_contract"):
            return redirect(reverse_lazy("objects:report_list", kwargs=kwargs))
        return render(request, "403.html", kwargs)
    return redirect(reverse_lazy("accounts:login", kwargs=kwargs))


class RegionListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список областей"""

    queryset = Region.objects.filter(on_delete=False)
    template_name = "handbooks/region_list.html"
    permission_required = "handbooks.view_region"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_region": user.has_perm("handbooks.change_region"),
        })
        return context


class DistrictListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список обласних районів"""

    queryset = District.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/district_list.html"
    permission_required = "handbooks.view_district"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_district": user.has_perm("handbooks.change_district"),
        })
        return context


class LocalityListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список міст"""

    queryset = Locality.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/locality_list.html"
    permission_required = "handbooks.view_locality"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_locality": user.has_perm("handbooks.change_locality"),
        })
        return context


class LocalityDistrictListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список районів міст"""

    queryset = LocalityDistrict.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/localitydistrict_list.html"
    permission_required = "handbooks.view_localitydistrict"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_localitydistrict": user.has_perm("handbooks.change_localitydistrict"),
        })
        return context


class StreetListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список вулиць"""

    queryset = Street.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/street_list.html"
    permission_required = "handbooks.view_street"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_street": user.has_perm("handbooks.change_street"),
        })
        return context


class WithdrawalReasonListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=1)
    permission_required = "handbooks.view_withdrawalreason"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "withdrawalreason"


class ConditionListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=2)
    permission_required = "handbooks.view_condition"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "condition"


class MaterialListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=3)
    permission_required = "handbooks.view_material"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "material"


class SeparationListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=4)
    permission_required = "handbooks.view_separation"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "separation"


class AgencyListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=5)
    permission_required = "handbooks.view_agency"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "agency"


class AgencySalesListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=6)
    permission_required = "handbooks.view_agencysales"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "agencysales"


class NewBuildingNameListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=7)
    permission_required = "handbooks.view_newbuildingname"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "newbuildingname"


class StairListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=8)
    permission_required = "handbooks.view_stair"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "stair"


class HeatingListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=9)
    permission_required = "handbooks.view_heating"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "heating"


class LayoutListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=10)
    permission_required = "handbooks.view_layout"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "layout"


class HouseTypeListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=11)
    permission_required = "handbooks.view_housetype"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "housetype"


class ComplexListView(
    CustomLoginRequiredMixin,
    PermissionRequiredMixin,
    SearchByIdMixin,
    NewCustomHandbookListView,
):
    queryset = Handbook.objects.filter(on_delete=False, type=12)
    permission_required = "handbooks.view_complex"
    template_name = "handbooks/handbook_list.html"
    choices = BASE_CHOICES

    app = "handbooks"
    handbook_type = "complex"


class FilialAgencyListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список філіалів"""

    queryset = FilialAgency.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/filial_list.html"
    permission_required = "handbooks.view_filialagency"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_filial": user.has_perm("handbooks.change_filialagency"),
        })
        return context


class FilialReportListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список філіальних звітів"""

    queryset = FilialReport.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/filialreport_list.html"
    permission_required = "handbooks.view_filialreport"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_filialreport": user.has_perm("handbooks.change_filialreport"),
        })
        return context


class RegionCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = RegionForm
    permission_required = "handbooks.add_region"

    app = "handbooks"
    handbook_type = "region"


class DistrictCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = DistrictForm
    permission_required = "handbooks.add_district"

    app = "handbooks"
    handbook_type = "district"


class LocalityCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = LocalityForm
    permission_required = "handbooks.add_locality"

    app = "handbooks"
    handbook_type = "locality"


class LocalityDistrictCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = LocalityDistrictForm
    permission_required = "handbooks.add_localitydistrict"

    app = "handbooks"
    handbook_type = "localitydistrict"


class StreetCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = StreetForm
    permission_required = "handbooks.add_street"

    app = "handbooks"
    handbook_type = "street"


class WithdrawalReasonCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_withdrawalreason"

    app = "handbooks"
    handbook_type = "withdrawalreason"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 1
        return kwargs


class ConditionCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_condition"

    app = "handbooks"
    handbook_type = "condition"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 2
        return kwargs


class MaterialCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_material"

    app = "handbooks"
    handbook_type = "material"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 3
        return kwargs


class SeparationCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_separation"

    app = "handbooks"
    handbook_type = "separation"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 4
        return kwargs


class AgencyCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_agency"

    app = "handbooks"
    handbook_type = "agency"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 5
        return kwargs


class AgencySalesCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_agencysales"

    app = "handbooks"
    handbook_type = "agencysales"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 6
        return kwargs


class NewBuildingNameCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_newbuildingname"

    app = "handbooks"
    handbook_type = "newbuildingname"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 7
        return kwargs


class StairCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_stair"

    app = "handbooks"
    handbook_type = "stair"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 8
        return kwargs


class HeatingCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_heating"

    app = "handbooks"
    handbook_type = "heating"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 9
        return kwargs


class LayoutCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_layout"

    app = "handbooks"
    handbook_type = "layout"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 10
        return kwargs


class HouseTypeCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_housetype"

    app = "handbooks"
    handbook_type = "housetype"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 11
        return kwargs


class ComplexCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_complex"

    app = "handbooks"
    handbook_type = "complex"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 12
        return kwargs


class FilialAgencyCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = FilialForm
    permission_required = "handbooks.add_filialagency"

    app = "handbooks"
    handbook_type = "filialagency"


class FilialReportCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = FilialReportForm
    permission_required = "handbooks.add_filialreport"

    app = "handbooks"
    handbook_type = "filialreport"


class RegionUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    permission_required = "handbooks.change_region"

    app = "handbooks"
    handbook_type = "region"


class DistrictUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    permission_required = "handbooks.change_district"

    app = "handbooks"
    handbook_type = "district"


class LocalityUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    permission_required = "handbooks.change_locality"

    app = "handbooks"
    handbook_type = "locality"


class LocalityDistrictUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    permission_required = "handbooks.change_localitydistrict"

    app = "handbooks"
    handbook_type = "localitydistrict"


class StreetUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    permission_required = "handbooks.change_street"

    app = "handbooks"
    handbook_type = "street"


class WithdrawalReasonUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_withdrawalreason"

    app = "handbooks"
    handbook_type = "withdrawalreason"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 1
        return kwargs


class ConditionUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_condition"

    app = "handbooks"
    handbook_type = "condition"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 2
        return kwargs


class MaterialUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_material"

    app = "handbooks"
    handbook_type = "material"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 3
        return kwargs


class SeparationUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_separation"

    app = "handbooks"
    handbook_type = "separation"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 4
        return kwargs


class AgencyUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_agency"

    app = "handbooks"
    handbook_type = "agency"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 5
        return kwargs


class AgencySalesUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_agencysales"

    app = "handbooks"
    handbook_type = "agencysales"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 6
        return kwargs


class NewBuildingNameUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_newbuildingname"

    app = "handbooks"
    handbook_type = "newbuildingname"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 7
        return kwargs


class StairUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_stair"

    app = "handbooks"
    handbook_type = "stair"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 8
        return kwargs


class HeatingUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_heating"

    app = "handbooks"
    handbook_type = "heating"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 9
        return kwargs


class LayoutUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_layout"

    app = "handbooks"
    handbook_type = "layout"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 10
        return kwargs


class HouseTypeUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_housetype"

    app = "handbooks"
    handbook_type = "housetype"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 11
        return kwargs


class ComplexUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_complex"

    app = "handbooks"
    handbook_type = "complex"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("data") and kwargs.get("data").get("handbook"):
            kwargs = super().get_form_kwargs()
            kwargs["data"]._mutable = True
            kwargs["data"]["type"] = 12
        return kwargs


class FilialAgencyUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = FilialAgency.objects.filter(on_delete=False)
    form_class = FilialForm
    permission_required = "handbooks.change_filialagency"

    app = "handbooks"
    handbook_type = "filialagency"


class FilialReportUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    permission_required = "handbooks.change_filialreport"

    app = "handbooks"
    handbook_type = "filialreport"


class RegionDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Region.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_region"
    handbook_type = "region"


class DistrictDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = District.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_district"
    handbook_type = "district"


class LocalityDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Locality.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_locality"
    handbook_type = "locality"


class LocalityDistrictDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_localitydistrict"
    handbook_type = "localitydistrict"


class StreetDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Street.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_street"
    handbook_type = "street"


class WithdrawalReasonDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_withdrawalreason"
    handbook_type = "withdrawalreason"


class ConditionDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_condition"
    handbook_type = "condition"


class MaterialDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_material"
    handbook_type = "material"


class SeparationDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_separation"
    handbook_type = "separation"


class AgencyDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_agency"
    handbook_type = "agency"


class AgencySalesDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_agencysales"
    handbook_type = "agencysales"


class NewBuildingNameDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_newbuildingname"
    handbook_type = "newbuildingname"


class StairDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_stair"
    handbook_type = "stair"


class HeatingDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_heating"
    handbook_type = "heating"


class LayoutDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_layout"
    handbook_type = "layout"


class HouseTypeDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_housetype"
    handbook_type = "housetype"


class ComplexDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_complex"
    handbook_type = "complex"


class FilialAgencyDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = FilialAgency.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_filialagency"
    handbook_type = "filialagency"


class FilialReportDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = FilialReport.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    permission_required = "handbooks.change_filialreport"
    handbook_type = "filialreport"


class AllClientsListView(ClientListMixin, ByUserMixin, CustomListView):
    queryset = Client.objects.filter(on_delete=False)
    filter = "all"
    perm = "view"
    choices = SALE_CHOICES


class NewClientListView(ClientListMixin, ByUserMixin, CustomListView):
    queryset = Client.objects.filter(
        on_delete=False,
        date_of_add__gte=timezone.now() - relativedelta(months=1)
    )
    filter = "new"
    perm = "view"
    choices = SALE_CHOICES


class InSelectionClientListView(
    ClientListMixin, ByUserMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.IN_SEARCH)
    filter = "in_selection"
    perm = "view"
    choices = SALE_CHOICES


class WithShowClientListView(
    ClientListMixin, ByUserMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.WITH_SHOW)
    filter = "with_show"
    perm = "view"
    choices = SALE_CHOICES


class DecidedClientListView(
    ClientListMixin, ByUserMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DECIDED)
    filter = "decided"
    perm = "view"
    choices = SALE_CHOICES


class DeferredDemandClientListView(
    ClientListMixin, ByUserMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DEFERRED_DEMAND)
    filter = "deferred_demand"
    perm = "view"
    choices = SALE_CHOICES


'''
class MyAllClientsListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False)
    filter = "all"
    perm = "view"
    choices = SALE_CHOICES


class MyNewClientListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(
        on_delete=False,
        date_of_add__gte=timezone.now() - relativedelta(months=1)
    )
    filter = "new"
    perm = "view"
    choices = SALE_CHOICES


class MyInSelectionClientListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.IN_SEARCH)
    filter = "in_selection"
    perm = "view"
    choices = SALE_CHOICES


class MyWithShowClientListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.WITH_SHOW)
    filter = "with_show"
    perm = "view"
    choices = SALE_CHOICES


class MyDecidedClientListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DECIDED)
    filter = "decided"
    perm = "view"
    choices = SALE_CHOICES


class MyDeferredDemandClientListView(
    UserClientListMixin, PermissionRequiredMixin, SearchByIdMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DEFERRED_DEMAND)
    filter = "deferred_demand"
    perm = "view"
    choices = SALE_CHOICES
'''

class FilialAllClientsListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False)
    filter = "all"
    perm = "view"
    choices = SALE_CHOICES


class FilialNewClientListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(
        on_delete=False,
        date_of_add__gte=timezone.now() - relativedelta(months=1)
    )
    filter = "new"
    perm = "view"
    choices = SALE_CHOICES


class FilialInSelectionClientListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.IN_SEARCH)
    filter = "in_selection"
    perm = "view"
    choices = SALE_CHOICES


class FilialWithShowClientListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.WITH_SHOW)
    filter = "with_show"
    perm = "view"
    choices = SALE_CHOICES


class FilialDecidedClientListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DECIDED)
    filter = "decided"
    perm = "view"
    choices = SALE_CHOICES


class FilialDeferredDemandClientListView(
    FilialClientListMixin, PermissionRequiredMixin, CustomListView
):
    queryset = Client.objects.filter(on_delete=False, status=ClientStatusType.DEFERRED_DEMAND)
    filter = "deferred_demand"
    perm = "view"
    choices = SALE_CHOICES


class ClientCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = ClientForm
    template_name = "handbooks/client_form.html"
    permission_required = "handbooks.add_client"

    app = "handbooks"
    handbook_type = "client"


class ClientUpdateView(ByUserMixin, CustomUpdateView):
    queryset = Client.objects.filter(on_delete=False)
    form_class = ClientForm
    template_name = "handbooks/client_form.html"
    perm = "change"

    app = "handbooks"
    handbook_type = "client"


class ClientDeleteView(ByUserMixin, CustomDeleteView):
    queryset = Client.objects.filter(on_delete=False)
    template_name = "delete_form.html"
    success_message = "Success"
    handbook_type = "client"
    perm = "change"
    app = "handbooks"


class RegionHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_region"
    handbook_type = "region"
    queryset = Region.objects.filter(on_delete=False)


class DistrictHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_district"
    handbook_type = "district"
    queryset = District.objects.filter(on_delete=False)


class LocalityHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_locality"
    handbook_type = "locality"
    queryset = Locality.objects.filter(on_delete=False)


class LocalityDistrictHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_localitydistrict"
    handbook_type = "localitydistrict"
    queryset = LocalityDistrict.objects.filter(on_delete=False)


class StreetHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_street"
    handbook_type = "street"
    queryset = Street.objects.filter(on_delete=False)


class WithdrawalReasonHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_withdrawalreason"
    handbook_type = "withdrawalreason"
    queryset = Handbook.objects.filter(on_delete=False)


class ConditionHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_condition"
    handbook_type = "condition"
    queryset = Handbook.objects.filter(on_delete=False)


class MaterialHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_material"
    handbook_type = "material"
    queryset = Handbook.objects.filter(on_delete=False)


class SeparationHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_separation"
    handbook_type = "separation"
    queryset = Handbook.objects.filter(on_delete=False)


class AgencyHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_agency"
    handbook_type = "agency"
    queryset = Handbook.objects.filter(on_delete=False)


class AgencySalesHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_agencysales"
    handbook_type = "agencysales"
    queryset = Handbook.objects.filter(on_delete=False)


class NewBuildingNameHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_newbuildingname"
    handbook_type = "newbuildingname"
    queryset = Handbook.objects.filter(on_delete=False)


class StairHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_stair"
    handbook_type = "stair"
    queryset = Handbook.objects.filter(on_delete=False)


class HeatingHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_heating"
    handbook_type = "heating"
    queryset = Handbook.objects.filter(on_delete=False)


class LayoutHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_layout"
    handbook_type = "layout"
    queryset = Handbook.objects.filter(on_delete=False)


class HouseTypeHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_housetype"
    handbook_type = "housetype"
    queryset = Handbook.objects.filter(on_delete=False)


class FilialAgencyHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_filialagency"
    handbook_type = "filialagency"
    queryset = FilialAgency.objects.filter(on_delete=False)


class FilialReportHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_filialreport"
    handbook_type = "filialreport"
    queryset = FilialReport.objects.filter(on_delete=False)


class ComplexHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_complex"
    handbook_type = "complex"
    queryset = Handbook.objects.filter(on_delete=False)


class ClientHistoryView(HistoryView):
    permission_required = "handbooks.view_client"
    handbook_type = "client"
    perm = "view"
    app = "handbooks"
    queryset = Client.objects.filter(on_delete=False)
