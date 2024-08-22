from django.utils.translation import gettext as _

from handbooks.models import *
from objects.models import Apartment

CEO_CHOICES = []
REALTOR_CHOICES = [(_('profile'), 'profile'), (_('client'), 'client'), (_('filial_report'), 'filial_report'),
                   (_('apartment'), 'apartment')]

CHOICES = [(_('region'), 'region'), (_('district'), 'district'),
           (_('locality'), 'locality'),
           (_('locality_district'), 'locality_district'),
           (_('street'), 'street'), (_('client'), 'client'),
           (_('withdrawal_reason'), 'withdrawal_reason'),
           (_('condition'), 'condition'), (_('material'), 'material'),
           (_('separation'), 'separation'), (_('agency'), 'agency'),
           (_('agency_sales'), 'agency_sales'),
           (_('new_building_name'), 'new_building_name'),
           (_('stair'), 'stair'), (_('heating'), 'heating'), (_('layout'), 'layout'),
           (_('house_type'), 'house_type'), (_('filial_agency'), 'filial_agency'),
           (_('filial_report'), 'filial_report'),
           (_('apartment'), 'apartment')]

MODEL = {'region': Region, 'district': District,
         'locality': Locality, 'locality_district': LocalityDistrict, 'street': Street,
         'client': Client, 'filial_agency': FilialAgency, 'filial_report': FilialReport,
         'apartment': Apartment}
HANDBOOKS_QUERYSET = {'withdrawal_reason': 1, 'condition': 2, 'material': 3, 'separation': 4,
                      'agency': 5, 'agency_sales': 6, 'new_building_name': 7, 'stair': 8,
                      'heating': 9, 'layout': 10, 'house_type': 11}
PERMISSION = {'region': 'handbooks.view_region', 'district': 'handbooks.view_district',
              'locality': 'handbooks.view_locality', 'locality_district': 'handbooks.view_localitydistrict',
              'street': 'handbooks.view_street',
              'client': 'handbooks.view_client', 'filial_agency': 'handbooks.view_filialagency',
              'filial_report': 'handbooks.view_filialreport', 'apartment': 'objects.view_apartment',
              'withdrawal_reason': 'handbooks.view_handbook', 'condition': 'handbooks.view_handbook',
              'material': 'handbooks.view_handbook', 'separation': 'handbooks.view_handbook',
              'agency': 'handbooks.view_handbook', 'agency_sales': 'handbooks.view_handbook',
              'new_building_name': 'handbooks.view_handbook', 'stair': 'handbooks.view_handbook',
              'heating': 'handbooks.view_handbook', 'layout': 'handbooks.view_handbook',
              'house_type': 'handbooks.view_handbook'
              }
OBJECT_COLUMNS = {'apartment': ["id", "region_id", "district_id", "locality_id",
                                "locality_district_id", "street_id"], }

LIST_BY_USER = {1: dict(), 3: {'client': 'realtor',
                               'apartment': ['realtor', 'site_realtor1', 'site_realtor2', 'realtor_5_5']}}
