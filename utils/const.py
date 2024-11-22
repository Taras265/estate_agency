from django.utils.translation import gettext as _

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
           (_('apartment'), 'apartment'), (_('report'), 'report')]
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
           (_('filialreport'), 'filialreport')]
SALE_CHOICES = [(_('client'), 'client'), (_('apartment'), 'apartment'),
                (_('report'), 'report'), (_('contract'), 'contract')]

MODEL = {'region': Region, 'district': District,
         'locality': Locality, 'localitydistrict': LocalityDistrict, 'street': Street,
         'client': Client, 'filialagency': FilialAgency, 'filialreport': FilialReport,
         'apartment': Apartment}
HANDBOOKS_QUERYSET = {'withdrawalreason': 1, 'condition': 2, 'material': 3, 'separation': 4,
                      'agency': 5, 'agencysales': 6, 'newbuildingname': 7, 'stair': 8,
                      'heating': 9, 'layout': 10, 'housetype': 11}
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
                'contract': 'objects'}
HANDBOOKS_FORMS = {'region': RegionForm, 'district': DistrictForm,
                   'locality': LocalityForm, 'localitydistrict': LocalityDistrictForm, 'street': StreetForm,
                   'client': ClientForm, 'filialagency': FilialForm, 'filialreport': FilialReportForm,
                   'apartment': ApartmentForm}
OBJECT_COLUMNS = {'client': ["id", "email", "first_name",
                                "last_name", "phone", "status"],
                  'apartment': ["id", "region_id", "district_id", "locality_id",
                                "locality_district_id", "street_id"],
                  'report': ['id', "locality_id", "locality_district_id", "street_id", 'floor',
                             'rooms_number', 'creation_date', 'price', 'status', 'owner_id']
                  }
OBJECT_COLUMNS['contract'] = OBJECT_COLUMNS['apartment']

LIST_BY_USER = {'client': 'realtor',
                'apartment': ['realtor', 'site_realtor1', 'site_realtor2', 'realtor_5_5']}
