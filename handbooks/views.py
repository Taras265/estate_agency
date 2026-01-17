from dateutil.relativedelta import relativedelta

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate
from django.forms.fields import IntegerField

from accounts.models import CustomUser
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
from objects.mixins import DefaultUserInCreateViewMixin
from objects.services import user_can_view_real_estate_list, user_can_view_report
from .utils import get_sale_client_list_context
from utils.mixins.mixins import (
    CustomLoginRequiredMixin,
    SearchByIdMixin,
)
from utils.views import (
    CustomCreateView,
    CustomDeleteView,
    CustomUpdateView,
    HistoryView,
)


def sale_redirect(request, lang):
    kwargs = {"lang": lang}
    if request.user:
        if user_can_view_real_estate_list(request.user):
            return redirect(
                reverse_lazy("objects:apartment_list", kwargs=kwargs)
            )
        return render(request, "403.html", kwargs)
    return redirect(reverse_lazy("accounts:login", kwargs=kwargs))


class RegionListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список областей"""

    queryset = Region.objects.filter(on_delete=False)
    template_name = "handbooks/region_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_region": user.has_perm("handbooks.change_handbook"),
        })
        return context


class DistrictListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список обласних районів"""

    queryset = District.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/district_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_district": user.has_perm("handbooks.change_handbook"),
        })
        return context


class LocalityListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список міст"""

    queryset = Locality.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/locality_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_locality": user.has_perm("handbooks.change_handbook"),
        })
        return context


class LocalityDistrictListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список районів міст"""

    queryset = LocalityDistrict.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/localitydistrict_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_localitydistrict": user.has_perm("handbooks.change_handbook"),
        })
        return context


class StreetListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список вулиць"""

    queryset = Street.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/street_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_street": user.has_perm("handbooks.change_handbook"),
        })
        return context


class WithdrawalReasonListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=1)
    template_name = "handbooks/handbook_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:withdrawalreason_create",
            "update_url_name": "handbooks:withdrawalreason_update",
            "delete_url_name": "handbooks:withdrawalreason_delete",
            "history_url_name": "handbooks:withdrawalreason_history"
        })
        return context


class ConditionListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=2)
    template_name = "handbooks/handbook_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:condition_create",
            "update_url_name": "handbooks:condition_update",
            "delete_url_name": "handbooks:condition_delete",
            "history_url_name": "handbooks:condition_history"
        })
        return context


class MaterialListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=3)
    template_name = "handbooks/handbook_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:material_create",
            "update_url_name": "handbooks:material_update",
            "delete_url_name": "handbooks:material_delete",
            "history_url_name": "handbooks:material_history"
        })
        return context


class SeparationListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=4)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:separation_create",
            "update_url_name": "handbooks:separation_update",
            "delete_url_name": "handbooks:separation_delete",
            "history_url_name": "handbooks:separation_history"
        })
        return context


class AgencyListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=5)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:agency_create",
            "update_url_name": "handbooks:agency_update",
            "delete_url_name": "handbooks:agency_delete",
            "history_url_name": "handbooks:agency_history"
        })
        return context


class AgencySalesListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=6)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:agencysales_create",
            "update_url_name": "handbooks:agencysales_update",
            "delete_url_name": "handbooks:agencysales_delete",
            "history_url_name": "handbooks:agencysales_history"
        })
        return context


class NewBuildingNameListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=7)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:newbuildingname_create",
            "update_url_name": "handbooks:newbuildingname_update",
            "delete_url_name": "handbooks:newbuildingname_delete",
            "history_url_name": "handbooks:newbuildingname_history"
        })
        return context


class StairListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=8)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:stair_create",
            "update_url_name": "handbooks:stair_update",
            "delete_url_name": "handbooks:stair_delete",
            "history_url_name": "handbooks:stair_history"
        })
        return context


class HeatingListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=9)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:heating_create",
            "update_url_name": "handbooks:heating_update",
            "delete_url_name": "handbooks:heating_delete",
            "history_url_name": "handbooks:heating_history"
        })
        return context


class LayoutListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=10)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:layout_create",
            "update_url_name": "handbooks:layout_update",
            "delete_url_name": "handbooks:layout_delete",
            "history_url_name": "handbooks:layout_history"
        })
        return context


class HouseTypeListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=11)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:housetype_create",
            "update_url_name": "handbooks:housetype_update",
            "delete_url_name": "handbooks:housetype_delete",
            "history_url_name": "handbooks:housetype_history"
        })
        return context


class ComplexListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    queryset = Handbook.objects.filter(on_delete=False, type=12)
    permission_required = "handbooks.view_handbooks"
    template_name = "handbooks/handbook_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_create_handbook": user.has_perm("handbooks.add_handbook"),
            "can_change_handbook": user.has_perm("handbooks.change_handbook"),
            "can_view_handbook_history": user.has_perm("handbooks.view_handbooks"),
            "create_url_name": "handbooks:complex_create",
            "update_url_name": "handbooks:complex_update",
            "delete_url_name": "handbooks:complex_delete",
            "history_url_name": "handbooks:complex_history"
        })
        return context


class FilialAgencyListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список філіалів"""

    queryset = FilialAgency.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/filial_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_filial": user.has_perm("handbooks.change_handbook"),
        })
        return context


class FilialReportListView(CustomLoginRequiredMixin, PermissionRequiredMixin, SearchByIdMixin, ListView):
    """Список філіальних звітів"""

    queryset = FilialReport.objects.filter(on_delete=False).select_related()
    template_name = "handbooks/filialreport_list.html"
    permission_required = "handbooks.view_handbooks"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        user = self.request.user
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": IdSearchForm(self.request.GET),
            "can_change_filialreport": user.has_perm("handbooks.change_handbook"),
        })
        return context


class RegionCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = RegionForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "region"


class DistrictCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = DistrictForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "district"


class LocalityCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = LocalityForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "locality"


class LocalityDistrictCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = LocalityDistrictForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "localitydistrict"


class StreetCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = StreetForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "street"


class WithdrawalReasonCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = HandbookForm
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

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
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "filialagency"


class FilialReportCreateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView
):
    form_class = FilialReportForm
    permission_required = "handbooks.add_handbook"

    app = "handbooks"
    handbook_type = "filialreport"


class RegionUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "region"


class DistrictUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "district"


class LocalityUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "locality"


class LocalityDistrictUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "localitydistrict"


class StreetUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "street"


class WithdrawalReasonUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

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
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "filialagency"


class FilialReportUpdateView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView
):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    permission_required = "handbooks.change_handbook"

    app = "handbooks"
    handbook_type = "filialreport"


class RegionDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Region.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "region"


class DistrictDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = District.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "district"


class LocalityDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Locality.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "locality"


class LocalityDistrictDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "localitydistrict"


class StreetDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Street.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "street"


class WithdrawalReasonDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "withdrawalreason"


class ConditionDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "condition"


class MaterialDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "material"


class SeparationDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "separation"


class AgencyDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "agency"


class AgencySalesDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "agencysales"


class NewBuildingNameDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "newbuildingname"


class StairDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "stair"


class HeatingDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "heating"


class LayoutDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "layout"


class HouseTypeDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "housetype"


class ComplexDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = Handbook.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "complex"


class FilialAgencyDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = FilialAgency.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "filialagency"


class FilialReportDeleteView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView
):
    queryset = FilialReport.objects.filter(on_delete=False)
    permission_required = "handbooks.change_handbook"
    handbook_type = "filialreport"


class AccessibleClientListView(CustomLoginRequiredMixin,
                               PermissionRequiredMixin,
                               ListView):
    """Список лише тих клієнтів, які доступні поточному користувачу для перегляду."""

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class NewAccessibleClientListView(CustomLoginRequiredMixin,
                                  PermissionRequiredMixin,
                                  ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та були додані 1 місяць тому.
    """

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        date_off_add_min = timezone.now() - relativedelta(months=1)
        return Client.objects.filter(
            on_delete=False,
             date_of_add__gte=date_off_add_min,
             realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class InSelectionAccessibleClientListView(CustomLoginRequiredMixin,
                                          PermissionRequiredMixin,
                                          ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.IN_SEARCH.
    """

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.IN_SEARCH,
            realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class WithShowAccessibleClientListView(CustomLoginRequiredMixin,
                                       PermissionRequiredMixin,
                                       ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.WITH_SHOW.
    """

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.WITH_SHOW,
            realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class DecidedAccessibleClientListView(CustomLoginRequiredMixin,
                                      PermissionRequiredMixin,
                                      ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.DECIDED.
    """

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.DECIDED,
            realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class DeferredDemandAccessibleClientListView(CustomLoginRequiredMixin,
                                             PermissionRequiredMixin,
                                             ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.DEFERRED_DEMAND.
    """

    template_name = "handbooks/client_list.html"
    paginate_by = 10
    permission_required = "handbooks.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.DEFERRED_DEMAND,
            realtor=self.request.user
        ).select_related("realtor")
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_sale_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class ClientCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, DefaultUserInCreateViewMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "handbooks/client_form.html"
    permission_required = "handbooks.add_own_client"

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        # щоб не змінював рієлтора, якщо може створювати лише він
        context["form"].fields["realtor"].widget.attrs["disabled"] = True
        context["form"].fields["realtor"].widget.attrs["readonly"] = True

        return context

    def form_invalid(self, form):
        # щоб не змінював рієлтора, якщо може створювати лише він
        post_data = self.request.POST.copy()
        post_data["realtor"] = self.request.user
        f = self.form_class(post_data)
        if f.is_valid():
            f.save()
            return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("handbooks:all_client_list", kwargs=kwargs)


class ClientUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = ClientForm
    template_name = "handbooks/client_form.html"
    permission_required = "handbooks.change_own_client"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            raise AttributeError(
                "Generic detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )
        client = get_object_or_404(Client.objects.select_related(), id=pk, on_delete=False)

        # умова що ми можемо працювати з клієнтом
        if client.realtor != self.request.user:
            raise PermissionDenied()
        return client

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        # щоб не змінював рієлтора, якщо може створювати лише він
        context["form"].fields["realtor"].widget.attrs["disabled"] = True
        context["form"].fields["realtor"].widget.attrs["readonly"] = True
        return context

    def form_invalid(self, form):
        # щоб не змінював рієлтора, якщо може створювати лише він
        o = self.get_object()
        post_data = self.request.POST.copy()
        post_data["realtor"] = self.request.user
        f = self.form_class(post_data, instance=o)
        if f.is_valid():
            f.save()
            return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("handbooks:all_client_list", kwargs=kwargs)


class ClientDeleteView(CustomLoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = "delete_form.html"
    permission_required = "handbooks.change_own_client"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            raise AttributeError(
                "Generic detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )
        client = get_object_or_404(Client, id=pk, on_delete=False)

        # умова що ми можемо працювати з клієнтом
        if client.realtor != self.request.user:
            raise PermissionDenied()
        return client

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("handbooks:all_client_list", kwargs=kwargs)


class RegionHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "region"
    queryset = Region.objects.filter(on_delete=False)


class DistrictHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "district"
    queryset = District.objects.filter(on_delete=False)


class LocalityHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "locality"
    queryset = Locality.objects.filter(on_delete=False)


class LocalityDistrictHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "localitydistrict"
    queryset = LocalityDistrict.objects.filter(on_delete=False)


class StreetHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "street"
    queryset = Street.objects.filter(on_delete=False)


class WithdrawalReasonHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "withdrawalreason"
    queryset = Handbook.objects.filter(on_delete=False)


class ConditionHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "condition"
    queryset = Handbook.objects.filter(on_delete=False)


class MaterialHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "material"
    queryset = Handbook.objects.filter(on_delete=False)


class SeparationHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "separation"
    queryset = Handbook.objects.filter(on_delete=False)


class AgencyHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "agency"
    queryset = Handbook.objects.filter(on_delete=False)


class AgencySalesHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "agencysales"
    queryset = Handbook.objects.filter(on_delete=False)


class NewBuildingNameHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "newbuildingname"
    queryset = Handbook.objects.filter(on_delete=False)


class StairHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "stair"
    queryset = Handbook.objects.filter(on_delete=False)


class HeatingHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "heating"
    queryset = Handbook.objects.filter(on_delete=False)


class LayoutHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "layout"
    queryset = Handbook.objects.filter(on_delete=False)


class HouseTypeHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "housetype"
    queryset = Handbook.objects.filter(on_delete=False)


class FilialAgencyHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "filialagency"
    queryset = FilialAgency.objects.filter(on_delete=False)


class FilialReportHistoryView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView
):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "filialreport"
    queryset = FilialReport.objects.filter(on_delete=False)


class ComplexHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    permission_required = "handbooks.view_handbooks"
    handbook_type = "complex"
    queryset = Handbook.objects.filter(on_delete=False)


class ClientHistoryView(HistoryView):
    permission_required = "handbooks.view_own_clients"
    handbook_type = "client"
    perm = "view"
    app = "handbooks"
    queryset = Client.objects.filter(on_delete=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        # тимчасове рішення,
        # оскільки "handbooks:client_list" було перейменовано на "handbooks:all_client_list"
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["list_url"] = "handbooks:all_client_list"
        return context


@require_GET
def load_filials(request, lang):
    filials = CustomUser.objects.get(id=request.GET.get("realtor")).filials.all()
    return JsonResponse(list(filials.values("id", "filial_agency")), safe=False)


@require_GET
def load_locality_districts(request, lang):
    """
    Повертає список районів міст (поля id, district).
    Якщо вказано query параметр locality (можна вказати декілька locality),
    то буде повернуто список районів для міста з id=locality.
    Query параметри:
    - locality: list[int]
    """
    # валідація query параметрів
    int_field = IntegerField(
        required=False,
        min_value=1,
        error_messages={"invalid": "Enter a positive integer."}
    )

    localities = request.GET.getlist("locality")
    try:
        locality_ids = list(map(int_field.clean, localities))
    except:
        return JsonResponse(
            {"success": False, "districts": [], "errors": int_field.error_messages}
        )

    locality_districts = LocalityDistrict.objects.filter(on_delete=False)
    if locality_ids:
        locality_districts = locality_districts.filter(locality__in=locality_ids)
    
    return JsonResponse(
        {
            "success": True,
            "districts": list(locality_districts.values("id", "district")),
            "errors": []
        },
        safe=False
    )


@require_GET
def load_streets(request, lang):
    """
    Повертає список вулиць (поля id, street).
    Якщо вказано query параметр locality_district (можна вказати
    декілька locality_district), то буде повернуто список вулиць для району
    міста з id=locality_district.
    Якщо query параметр locality_district не вказано, проте вказано 
    query параметр locality (можна вказати декілька locality),
    то буде повернуто список вулиць для міста з id=locality.
    Query параметри:
    - locality: list[int]
    - locality_district: list[int]
    """
    # валідація query параметрів
    int_field = IntegerField(
        required=False,
        min_value=1,
        error_messages={"invalid": "Enter a positive integer."}
    )

    locality_districts = request.GET.getlist("locality_district")
    localities = request.GET.getlist("locality")
    try:
        locality_district_ids = list(map(int_field.clean, locality_districts))
        locality_ids = list(map(int_field.clean, localities))
    except:
        return JsonResponse(
            {"success": False, "streets": [], "errors": int_field.error_messages}
        )

    streets = Street.objects.filter(on_delete=False)
    if locality_district_ids:
        streets = streets.filter(locality_district__in=locality_district_ids)
    elif locality_ids:
        streets = streets.filter(locality__in=locality_ids)

    return JsonResponse(
        {"success": True, "streets": list(streets.values("id", "street")), "errors": []},
        safe=False
    )