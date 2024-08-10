from django.utils.translation import gettext as _

from handbooks.models import *
from objects.models import Apartment

CEO_CHOICES = [(_('profile'), 'profile'), (_('region'), 'region'), (_('district'), 'district'),
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
REALTOR_CHOICES = [(_('profile'), 'profile'), (_('client'), 'client'), (_('filial_report'), 'filial_report'),
                   (_('apartment'), 'apartment')]

CHOICES = {1: CEO_CHOICES, 3: REALTOR_CHOICES}

QUERYSET = {'region': Region, 'district': District,
            'locality': Locality, 'locality_district': LocalityDistrict, 'street': Street,
            'client': Client, 'filial_agency': FilialAgency, 'filial_report': FilialReport, 'apartment': Apartment}
HANDBOOKS_QUERYSET = {'withdrawal_reason': 1, 'condition': 2, 'material': 3, 'separation': 4,
                      'agency': 5, 'agency_sales': 6, 'new_building_name': 7, 'stair': 8,
                      'heating': 9, 'layout': 10, 'house_type': 11}

LIST_BY_USER = {1: dict(), 3: {'client': 'realtor',
                               'apartment': ['realtor', 'site_realtor1', 'site_realtor2', 'realtor_5_5']}}
