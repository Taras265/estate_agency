from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.translation import activate

from accounts.models import CustomUser
from accounts.services import user_get
from objects.services import user_can_view_real_estate_list, user_can_view_report
from utils.const import BASE_CHOICES
from utils.mixins.new_mixins import CustomLoginRequiredMixin


class BaseView(CustomLoginRequiredMixin, TemplateView):
    template_name = "main.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # переклад
        context = super().get_context_data(**kwargs)

        user = user_get(email=self.request.user)

        context['lang'] = self.kwargs['lang']
        context.update({
            'accounts': any(user.has_perm(perm) for perm in [
                'accounts.view_customuser', 'accounts.view_group'
            ]),
            'sale': any(user.has_perm(perm) for perm in [
                'handbooks.view_client', 'handbooks.view_own_client', 'handbooks.view_filial_client',
                'objects.view_contract'
            ]) and any([user_can_view_real_estate_list(user), user_can_view_report(user)]),
            'handbooks': any(user.has_perm(f'handbooks.view_{perm[1]}') for perm in BASE_CHOICES),
        })

        return context


def fill_db(request, lang):
    from handbooks.models import (
        Region,
        District,
        Locality,
        LocalityDistrict,
        Street,
        Client,
        Handbook,
        FilialAgency,
        FilialReport
    )
    from objects.models import Apartment
    from django.shortcuts import redirect
    import datetime

    region = Region()
    region.region = 'Region 1'
    region.save()

    district = District()
    district.district = 'District 1'
    district.region = Region.objects.first()
    district.save()

    locality = Locality()
    locality.locality = 'Locality 1'
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
    client.email = 't@gmail.com'
    client.first_name = 'Client'
    client.last_name = "Test"
    client.phone = '050'
    client.realtor = CustomUser.objects.first()
    client.save()

    for i in range(1, 13):
        handbooks = Handbook()
        handbooks.handbook = 'Handbook'
        handbooks.type = i
        handbooks.save()

    agency = FilialAgency()
    agency.filial_agency = 'Agency 1'
    agency.save()

    report = FilialReport()
    report.report = 'Report'
    report.filial_agency = FilialAgency.objects.first()
    report.user = CustomUser.objects.first()
    report.save()

    return redirect(f'/{lang}/', {'lang': lang})
