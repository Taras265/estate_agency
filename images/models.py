from django.db import models

from objects.models import Apartment


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartment_image/')
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")
