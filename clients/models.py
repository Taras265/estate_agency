import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from estate_agency.models import BaseModel
from .choices import (
    IncomeSourceType,
    ClientStatusType,
)
from objects.choices import RealEstateType
from handbooks.choices import RealtorType


class Client(BaseModel):
    date_of_add = models.DateField(default=timezone.now)
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100)
    messenger = models.CharField(max_length=200, null=True, blank=True)
    viber = models.BooleanField(default=False)
    telegram = models.BooleanField(default=False)
    income_source = models.PositiveSmallIntegerField(
        choices=IncomeSourceType.choices,
        default=1
    )
    status = models.PositiveSmallIntegerField(
        choices=ClientStatusType.choices,
        default=1
    )
    object_type = models.PositiveSmallIntegerField(
        choices=RealEstateType.choices,
        default=1
    )
    realtor_type = models.PositiveSmallIntegerField(
        choices=RealtorType.choices,
        default=1
    )
    realtor = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="realtor_client_related_name"
    )
    rooms_number = models.PositiveSmallIntegerField(null=True, blank=True)
    locality = models.ManyToManyField(
        "handbooks.Locality",
        related_name="locality_client_related_name",
        null=True,
        blank=True
    )
    locality_district = models.ManyToManyField(
        "handbooks.LocalityDistrict",
        related_name="locality_district_client_related_name",
        null=True,
        blank=True,
    )
    street = models.ManyToManyField(
        "handbooks.Street",
        related_name="street_client_related_name",
        null=True,
        blank=True
    )
    house = models.CharField(max_length=100, null=True, blank=True)
    floor_min = models.PositiveIntegerField(null=True, blank=True)
    floor_max = models.PositiveIntegerField(null=True, blank=True)
    not_first = models.BooleanField(default=False)
    not_last = models.BooleanField(default=False)
    price_from = models.IntegerField(null=True, blank=True)
    price_to = models.IntegerField(null=True, blank=True)
    square_meter_price_max = models.IntegerField(null=True, blank=True)
    condition = models.ManyToManyField(
        "handbooks.Handbook",
        related_name="condition_client_related_name",
        null=True,
        blank=True
    )

    class Meta:
        permissions = (
            ("add_own_client", "Can add own clients"),
            ("view_own_clients", "Can view own client"),
            ("change_own_client", "Can change own client"),
            # ("view_filial_client", ""),
            # ("change_filial_client", ""),
        )
        default_permissions = ()
        """
        permissions = (
            ("change_own_client", "Can change own client"),
            ("view_own_client", "Can view own client"),
            ("change_filial_client", "Can change filial client"),
            ("view_filial_client", "Can view filial client"),
            ("view_own_office_client", "Can view in office own clients"),
            ("view_filial_office_client", "Can view in office filial clients"),
        )
        """

    def __str__(self):
        return f"{self.first_name} {self.phone}"


class Selection(models.Model):
    class Meta:
        default_permissions = ()
        permissions = (("selection", "Selection"),)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("Client"))
    date = models.DateField(default=datetime.date.today, verbose_name=_("Date"))
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, verbose_name=_("User"))
    selected_apartments = models.ManyToManyField(
        "objects.Apartment", blank=True, related_name="related_selected_apartments"
    )
    selected_houses = models.ManyToManyField(
        "objects.House", blank=True, related_name="related_selected_houses"
    )
    selected_commerces = models.ManyToManyField(
        "objects.Commerce", blank=True, related_name="related_selected_commerces"
    )
    selected_lands = models.ManyToManyField(
        "objects.Land", blank=True, related_name="related_selected_lands"
    )