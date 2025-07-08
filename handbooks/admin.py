from django.contrib import admin
from simple_history import register
from handbooks.models import (Region, District, Locality, LocalityDistrict, Street,
                              Client, Handbook, FilialAgency, FilialReport)

admin.site.register(Region)
admin.site.register(District)
admin.site.register(Locality)
admin.site.register(LocalityDistrict)
admin.site.register(Street)
admin.site.register(Client)
admin.site.register(Handbook)
admin.site.register(FilialAgency)
admin.site.register(FilialReport)

register(Region)
register(District)
register(Locality)
register(LocalityDistrict)
register(Street)
register(Client)
register(Handbook)
register(FilialAgency)
register(FilialReport)
