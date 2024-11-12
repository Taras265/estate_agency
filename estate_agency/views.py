from django.shortcuts import render
from django.views.generic import TemplateView

from accounts.models import CustomUser


class BaseView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lang'] = self.kwargs['lang']

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

    for i in range(1, 12):
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

    apartment = Apartment()
    apartment.creation_date = datetime.date(1997, 10, 19)
    apartment.purchase_date = datetime.date(1997, 10, 19)

    apartment.exclusive = False

    apartment.region = Region.objects.first()
    apartment.district = District.objects.first()
    apartment.locality = Locality.objects.first()
    apartment.locality_district = LocalityDistrict.objects.first()
    apartment.street = Street.objects.first()

    apartment.on_site = False
    apartment.inspection_flag = False
    apartment.paid_exclusive_flag = False
    apartment.terrace_flag = False
    apartment.sea_flag = False
    apartment.vip = False

    apartment.withdrawal_reason = Handbook.objects.first()
    apartment.independent = False
    apartment.condition = Handbook.objects.first()
    apartment.special = False
    apartment.urgently = False
    apartment.trade = False

    apartment.material = Handbook.objects.first()

    apartment.status = 1
    apartment.object_type = 1

    apartment.square = 11
    apartment.price = 11
    apartment.site_price = 11
    apartment.square_meter_price = 11

    apartment.realtor = CustomUser.objects.first()
    apartment.site_realtor1 = CustomUser.objects.first()

    apartment.for_trainee = False

    apartment.author = CustomUser.objects.first()
    apartment.owner = Client.objects.first()

    apartment.owners_number = 14
    apartment.comment = "Comment"

    apartment.separation = Handbook.objects.first()
    apartment.agency = Handbook.objects.first()
    apartment.agency_sales = Handbook.objects.first()
    apartment.new_building = False

    NEW_BUILDING_TYPE_CHOICES = (
        (1, "От хозяина"),
        (2, "От строителя")
    )

    """
    Personal for apartments
    """
    apartment.rooms_number = 14

    apartment.room_types = 1

    apartment.height = 2.1
    apartment.kitchen_square = 12
    apartment.living_square = 12
    apartment.gas = False
    apartment.courtyard = False
    apartment.balcony_number = 14
    apartment.registered_number = 14
    apartment.child_registered_number = 14
    apartment.loggias_number = 14
    apartment.bay_windows_number = 14
    apartment.commune = False
    apartment.frame = "Data"
    apartment.stair = Handbook.objects.first()
    apartment.balcony = False
    apartment.heating = Handbook.objects.first()
    apartment.office = False
    apartment.penthouse = False

    apartment.redevelopment = 1

    apartment.layout = Handbook.objects.first()
    apartment.construction_number = "Data"
    apartment.house_type = Handbook.objects.first()
    apartment.two_level_apartment = False
    apartment.loggia = 12
    apartment.attic = False
    apartment.electric_stove = False
    apartment.floor = 12
    apartment.storeys_number = 12
    apartment.save()

    return redirect(f'/{lang}/', {'lang': lang})
