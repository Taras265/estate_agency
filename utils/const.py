from django.utils.translation import gettext as _

from accounts.forms import UserForm, GroupForm
from accounts.models import CustomGroup
from handbooks.forms import (RegionForm, StreetForm, LocalityDistrictForm, LocalityForm,
                             DistrictForm, ClientForm, FilialReportForm, FilialForm)
from handbooks.models import *
from objects.forms import ApartmentForm
from objects.models import Apartment


CHOICES = [(_('region'), 'region'), (_('district'), 'district'),
           (_('locality'), 'locality'),
           (_('localitydistrict'), 'localitydistrict'),
           (_('street'), 'street'), (_('client'), 'client'),
           (_('withdrawalreason'), 'withdrawalreason'),
           (_('condition'), 'condition'), (_('material'), 'material'),
           (_('separation'), 'separation'), (_('agency'), 'agency'),
           (_('agencysales'), 'agencysales'),
           (_('newbuildingname'), 'newbuildingname'),
           (_('stair'), 'stair'), (_('heating'), 'heating'), (_('layout'), 'layout'),
           (_('housetype'), 'housetype'), (_('filialagency'), 'filialagency'),
           (_('filialreport'), 'filialreport'),
           (_('apartment'), 'apartment'), (_('report'), 'report'), (_('complex'), 'complex')]
BASE_CHOICES = [(_('region'), 'region'), (_('district'), 'district'),
           (_('locality'), 'locality'),
           (_('localitydistrict'), 'localitydistrict'),
           (_('street'), 'street'),
           (_('withdrawalreason'), 'withdrawalreason'),
           (_('condition'), 'condition'), (_('material'), 'material'),
           (_('separation'), 'separation'), (_('agency'), 'agency'),
           (_('agencysales'), 'agencysales'),
           (_('newbuildingname'), 'newbuildingname'),
           (_('stair'), 'stair'), (_('heating'), 'heating'), (_('layout'), 'layout'),
           (_('housetype'), 'housetype'), (_('filialagency'), 'filialagency'),
           (_('filialreport'), 'filialreport'), (_('complex'), 'complex')]
SALE_CHOICES = [(_('client'), 'client'), (_('apartment'), 'apartment'),
                (_('report'), 'report'), (_('contract'), 'contract')]
USER_CHOICES = [(_('user'), 'user'), (_('group'), 'group')]

MODEL = {'region': Region, 'district': District,
         'locality': Locality, 'localitydistrict': LocalityDistrict, 'street': Street,
         'client': Client, 'filialagency': FilialAgency, 'filialreport': FilialReport,
         'apartment': Apartment, 'user': CustomUser, 'group': CustomGroup}
HANDBOOKS_QUERYSET = {'withdrawalreason': 1, 'condition': 2, 'material': 3, 'separation': 4,
                      'agency': 5, 'agencysales': 6, 'newbuildingname': 7, 'stair': 8,
                      'heating': 9, 'layout': 10, 'housetype': 11, 'complex': 12}
TABLE_TO_APP = {'region': 'handbooks', 'district': 'handbooks',
                'locality': 'handbooks', 'localitydistrict': 'handbooks',
                'street': 'handbooks',
                'client': 'handbooks', 'filialagency': 'handbooks',
                'filialreport': 'handbooks', 'apartment': 'objects',
                'withdrawalreason': 'handbooks', 'condition': 'handbooks',
                'material': 'handbooks', 'separation': 'handbooks',
                'agency': 'handbooks', 'agencysales': 'handbooks',
                'newbuildingname': 'handbooks', 'stair': 'handbooks',
                'heating': 'handbooks', 'layout': 'handbooks',
                'housetype': 'handbooks', 'report': 'objects', 'history_report': 'objects',
                'contract': 'objects', 'complex': 'handbooks', 'user': 'accounts', 'group': 'accounts'}
HANDBOOKS_FORMS = {'region': RegionForm, 'district': DistrictForm,
                   'locality': LocalityForm, 'localitydistrict': LocalityDistrictForm, 'street': StreetForm,
                   'client': ClientForm, 'filialagency': FilialForm, 'filialreport': FilialReportForm,
                   'apartment': ApartmentForm, 'user': UserForm, 'group': GroupForm}

TEMPLATES = {'apartment': 'objects/apartment_form.html', 'client': 'handbooks/client_form.html'}

OBJECT_COLUMNS = {
    'district': [
        'id', 'district', 'region',
    ],
    'locality': [
        'id', 'locality', 'district', 'city type', 'center type',
    ],
    'localitydistrict': [
        'id', 'district', 'locality', 'description', 'group on site',
        'hot deals limit', 'prefix to site', 'new building district',
    ],
    'street': [
        'id', 'street', 'locality district',
    ],
    'client': [
        'id', 'email', 'first_name', 'last_name', 'phone', 'status'
    ],
    'apartment': [
        'id', 'region', 'district', 'locality', 'locality district', 'street'
    ],
    'filialagency': [
        'id', 'filial agency'
    ],
    'filialreport': [
        'id', 'report', 'filial agency', 'user',
    ],
    'report': [
        'id', "locality", "locality district", "street", 'floor',
        'rooms number', 'creation date', 'price', 'status', 'owner'
    ],
    'contract': [
        'id', 'region', 'district', 'locality', 'locality district', 'street'
    ],
    'user': [
        'id', 'email', 'first_name', 'last_name', 'phone'
    ],
}

# хеш-таблиця, в якій ключі - це назви таблиць з БД,
# а значення - список полів відповідної таблиці, які потрібно відображати на вебсторінці
OBJECT_FIELDS = {
    'district': [
        'id', 'district', 'region__region',
    ],
    'locality': [
        'id', 'locality', 'district__district', 'city_type', 'center_type',
    ],
    'localitydistrict': [
        'id', 'district', 'locality__locality', 'description', 'group_on_site',
        'hot_deals_limit', 'prefix_to_site', 'new_building_district',
    ],
    'street': [
        'id', 'street', 'locality_district__district',
    ],
    'client': [
        'id', 'email', 'first_name', 'last_name', 'phone', 'status'
    ],
    'apartment': [
        'id', 'region__region', 'district__district', 'locality__locality',
        'locality_district__district', 'street__street'
    ],
    'filialreport': [
        'id', 'report', 'filial_agency__filial_agency', 'user__email',
    ],
    'report': [
        'id', "locality__locality", "locality_district__district", "street__street", 'floor',
        'rooms_number', 'creation_date', 'price', 'status', 'owner__email'
    ],
    'contract': [
        'id', 'region__region', 'district__district', 'locality__locality',
        'locality_district__district', 'street__street'
    ],
    'user': [
        'id', 'email', 'first_name', 'last_name', 'phone'
    ],
}

LIST_BY_USER = {'client': 'realtor',
                'apartment': ['realtor', 'site_realtor1', 'site_realtor2', 'realtor_5_5']}
