from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import CustomUser, CustomGroup

admin.site.register(CustomUser)
admin.site.register(CustomGroup)
admin.site.register(Permission)
