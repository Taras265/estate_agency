from django.utils.translation import activate
from django.views.generic import TemplateView

from accounts.models import CustomUser
from objects.services import user_can_view_real_estate_list, user_can_view_report
from utils.const import BASE_CHOICES
from utils.mixins.mixins import CustomLoginRequiredMixin


class BaseView(CustomLoginRequiredMixin, TemplateView):
    template_name = "main.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # переклад
        context = super().get_context_data(**kwargs)

        context["lang"] = self.kwargs["lang"]
        context.update(
            {
                "accounts": any(
                    self.request.user.has_perm(perm)
                    for perm in ["accounts.view_customuser", "accounts.view_group"]
                ),
                "sale": any(
                    self.request.user.has_perm(perm)
                    for perm in [
                        "handbooks.view_client",
                        "handbooks.view_own_client",
                        "handbooks.view_filial_client",
                        "objects.view_contract",
                    ]
                )
                and any(
                    [user_can_view_real_estate_list(self.request.user), user_can_view_report(self.request.user)]
                ),
                "selection": any(
                    self.request.user.has_perm(perm)
                    for perm in [
                        "handbooks.view_client",
                        "handbooks.view_own_client",
                        "handbooks.view_filial_client",
                    ]
                )
                        and self.request.user.has_perm("objects.selection"),
                "handbooks": any(
                    self.request.user.has_perm(f"handbooks.view_{perm}") for perm in BASE_CHOICES
                ),
            }
        )

        return context


def fill_db(request, lang):

    from django.shortcuts import redirect

    from handbooks.models import (
        Client,
        District,
        FilialAgency,
        FilialReport,
        Handbook,
        Locality,
        LocalityDistrict,
        Region,
        Street,
    )

    region = Region()
    region.region = "Region 1"
    region.save()

    district = District()
    district.district = "District 1"
    district.region = Region.objects.first()
    district.save()

    locality = Locality()
    locality.locality = "Locality 1"
    locality.district = District.objects.first()
    locality.city_type = 1
    locality.center_type = 1
    locality.save()

    locality_district = LocalityDistrict()
    locality_district.district = "District 1"
    locality_district.locality = Locality.objects.first()
    locality_district.description = ""
    locality_district.group_on_site = ""
    locality_district.hot_deals_limit = 1.0
    locality_district.prefix_to_site = "1"
    locality_district.is_subdistrict = False
    locality_district.new_building_district = 1
    locality_district.save()

    street = Street()
    street.street = "Street 1"
    street.locality_district = LocalityDistrict.objects.first()
    street.save()

    client = Client()
    client.email = "t@gmail.com"
    client.first_name = "Client"
    client.last_name = "Test"
    client.phone = "050"
    client.realtor = CustomUser.objects.first()
    client.save()

    for i in range(1, 13):
        handbooks = Handbook()
        handbooks.handbook = "Handbook"
        handbooks.type = i
        handbooks.save()

    agency = FilialAgency()
    agency.filial_agency = "Agency 1"
    agency.save()

    report = FilialReport()
    report.report = "Report"
    report.filial_agency = FilialAgency.objects.first()
    report.user = CustomUser.objects.first()
    report.save()

    return redirect(f"/{lang}/", {"lang": lang})
