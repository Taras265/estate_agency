from django.db import models
from simple_history.models import HistoricalRecords

from accounts.models import CustomUser


class Region(models.Model):
    region = models.CharField(max_length=100)
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return self.region


class District(models.Model):
    district = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_related_name")
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")

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

    class Meta:
        default_permissions = ("add", "change", "view")

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

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return self.district


class Street(models.Model):
    street = models.CharField(max_length=100)
    locality_district = models.ForeignKey(LocalityDistrict, on_delete=models.CASCADE,
                                          related_name="locality_district_related_name")
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return self.street


class Client(models.Model):
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    realtor = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                related_name="realtor_related_name")

    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")
        permissions = (
            ("add_own_client", "Can add own client"),
            ("change_own_client", "Can change own client"),
            ("view_own_client", "Can view own client"),
            ("view_own_historicalclient", "Can view own historical client"),
        )

    def __str__(self):
        return f'{self.email} {self.first_name} {self.last_name}'


class Handbook(models.Model):
    handbook = models.CharField(max_length=100)

    HANDBOOKS_TYPE_CHOICE = (
        (1, "withdrawal_reason"),
        (2, "condition"),
        (3, "material"),
        (4, "separation"),
        (5, "agency"),
        (6, "agency_sales"),
        (7, "new_building_name"),
        (8, "stair"),
        (9, "heating"),
        (10, "layout"),
        (11, "house_type")
    )

    type = models.PositiveSmallIntegerField(choices=HANDBOOKS_TYPE_CHOICE)
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ()
        permissions = (
            ("add_withdrawalreason", "Can add withdrawal reason"),
            ("change_withdrawalreason", "Can change withdrawal reason"),
            ("view_withdrawalreason", "Can view withdrawal reason"),
            ("view_historicalwithdrawalreason", "Can view historical withdrawal reason"),

            ("add_condition", "Can add condition"),
            ("change_condition", "Can change condition"),
            ("view_condition", "Can view condition"),
            ("view_historicalcondition", "Can view historical condition"),

            ("add_material", "Can add material"),
            ("change_material", "Can change material"),
            ("view_material", "Can view material"),
            ("view_historicalmaterial", "Can view historical material"),

            ("add_separation", "Can add separation"),
            ("change_separation", "Can change separation"),
            ("view_separation", "Can view separation"),
            ("view_historicalseparation", "Can view historical separation"),

            ("add_agency", "Can add agency"),
            ("change_agency", "Can change agency"),
            ("view_agency", "Can view agency"),
            ("view_historicalagency", "Can view historical agency"),

            ("add_agencysales", "Can add agency sales"),
            ("change_agencysales", "Can change agency sales"),
            ("view_agencysales", "Can view agency sales"),
            ("view_historicalagencysales", "Can view historical agency sales"),

            ("add_newbuildingname", "Can add new building name"),
            ("change_newbuildingname", "Can change new building name"),
            ("view_newbuildingname", "Can view new building name"),
            ("view_historicalnewbuildingname", "Can view historical new building name"),

            ("add_stair", "Can add stair"),
            ("change_stair", "Can change stair"),
            ("view_stair", "Can view stair"),
            ("view_historicalstair", "Can view historical stair"),

            ("add_heating", "Can add heating"),
            ("change_heating", "Can change heating"),
            ("view_heating", "Can view heating"),
            ("view_historicalheating", "Can view historical heating"),

            ("add_layout", "Can add layout"),
            ("change_layout", "Can change layout"),
            ("view_layout", "Can view layout"),
            ("view_historicallayout", "Can view historical layout"),

            ("add_housetype", "Can add house type"),
            ("change_housetype", "Can change house type"),
            ("view_housetype", "Can view house type"),
            ("view_historicalhousetype", "Can view historical house type"),
        )

    def __str__(self):
        return self.handbook


class FilialAgency(models.Model):
    filial_agency = models.CharField(max_length=100)
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return self.filial_agency


class FilialReport(models.Model):
    report = models.TextField()
    filial_agency = models.ForeignKey(FilialAgency, on_delete=models.CASCADE,
                                      related_name="filial_agency_related_name")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="user_report_related_name")
    on_delete = models.BooleanField(default=False)

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return self.report


class UserFilial(models.Model):
    filial_agency = models.ForeignKey(FilialAgency, on_delete=models.CASCADE,
                                      related_name="filial_user_related_name")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name="user_filial_related_name")

    class Meta:
        default_permissions = ("add", "change", "view")

    def __str__(self):
        return f'{self.user}: {self.filial_agency}'
