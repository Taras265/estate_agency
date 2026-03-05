from django.contrib import admin
from simple_history import register

from . import models

admin.site.register(models.Client)
admin.site.register(models.Selection)

register(models.Client)
register(models.Selection)
