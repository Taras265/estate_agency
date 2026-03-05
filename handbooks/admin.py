from django.contrib import admin
from simple_history import register

from . import models

admin.site.register(models.Region)
admin.site.register(models.District)
admin.site.register(models.Locality)
admin.site.register(models.LocalityDistrict)
admin.site.register(models.Street)
admin.site.register(models.Handbook)
admin.site.register(models.FilialAgency)
admin.site.register(models.FilialReport)

register(models.Region)
register(models.District)
register(models.Locality)
register(models.LocalityDistrict)
register(models.Street)
register(models.Handbook)
register(models.FilialAgency)
register(models.FilialReport)
