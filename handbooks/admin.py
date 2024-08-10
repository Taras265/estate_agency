from django.contrib import admin
from simple_history import register


from handbooks.models import *

admin.site.register(Region)
admin.site.register(District)
admin.site.register(Locality)
admin.site.register(LocalityDistrict)
admin.site.register(Street)
admin.site.register(ObjectType)
admin.site.register(Client)
admin.site.register(Handbook)
admin.site.register(FilialAgency)
admin.site.register(FilialReport)
admin.site.register(UserFilial)

register(Region)
register(District)
register(Locality)
register(LocalityDistrict)
register(Street)
register(ObjectType)
register(Client)
register(Handbook)
register(FilialAgency)
register(FilialReport)
register(UserFilial)
