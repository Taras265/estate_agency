from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from accounts.models import CustomUser


class Region(models.Model):
    region = models.CharField(max_length=100)
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.region


class District(models.Model):
    district = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_related_name")
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.district


class Locality(models.Model):
    locality = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="district_related_name")

    CITY_TYPE_CHOICES = (
        (1, "село"),
        (2, "смт"),
        (3, "місто"),
    )
    city_type = models.PositiveSmallIntegerField(choices=CITY_TYPE_CHOICES, null=True, blank=True)

    CENTER_TYPE_CHOICES = (
        (1, "районий"),
        (2, "обласний"),
        (3, ""),
    )
    center_type = models.PositiveSmallIntegerField(choices=CENTER_TYPE_CHOICES)

    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.locality


class LocalityDistrict(models.Model):
    district = models.CharField(max_length=100)
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name="locality_related_name")

    description = models.TextField(null=True, blank=True)
    group_on_site = models.CharField(max_length=100, null=True, blank=True)
    hot_deals_limit = models.DecimalField(max_digits=4, decimal_places=2)
    prefix_to_site = models.CharField(max_length=5)
    is_subdistrict = models.BooleanField

    NEW_BUILDING_DISTRICT_CHOICES = (
        (1, "Приморский+Центр"),
        (2, "Киевский+Малиновский"),
        (3, "Суворовский"),
        (4, ""),
    )
    new_building_district = models.PositiveSmallIntegerField(choices=NEW_BUILDING_DISTRICT_CHOICES)

    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.district


class Street(models.Model):
    street = models.CharField(max_length=100)
    locality_district = models.ForeignKey(LocalityDistrict, on_delete=models.CASCADE,
                                          related_name="locality_district_related_name")
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.street


class Client(models.Model):
    date_of_add = models.DateField(default=timezone.now)

    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    realtor = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                related_name="realtor_related_name")

    STATUS_CHOICES = (
        (1, "В подборе"),
        (2, "С показом"),
        (3, "Определившиеся"),
        (4, "Отложенный спрос")
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.email} {self.first_name} {self.last_name}'


class Handbook(models.Model):
    handbook = models.CharField(max_length=100)

    HANDBOOKS_TYPE_CHOICE = ((1, "withdrawal_reason"),
                             (2, "condition"),
                             (3, "material"),
                             (4, "separation"),
                             (5, "agency"),
                             (6, "agency_sales"),
                             (7, "new_building_name"),
                             (8, "stair"),
                             (9, "heating"),
                             (10, "layout"),
                             (11, "house_type"))
    type = models.PositiveSmallIntegerField(choices=HANDBOOKS_TYPE_CHOICE)
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.handbook


class FilialAgency(models.Model):
    filial_agency = models.CharField(max_length=100)
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.filial_agency


class FilialReport(models.Model):
    report = models.TextField()
    filial_agency = models.ForeignKey(FilialAgency, on_delete=models.CASCADE,
                                      related_name="filial_agency_related_name")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="user_report_related_name")
    on_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.report


class UserFilial(models.Model):
    filial_agency = models.ForeignKey(FilialAgency, on_delete=models.CASCADE,
                                      related_name="filial_user_related_name")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="user_filial_related_name")

    def __str__(self):
        return f'{self.user}: {self.filial_agency}'
