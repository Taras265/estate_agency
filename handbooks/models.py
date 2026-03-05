from django.db import models
from django.utils import timezone

from accounts.models import CustomUser
from estate_agency.models import BaseModel
from handbooks.choices import (
    CenterType,
    CityType,
    NewBuildingDistrictType,
    HandbookType,
)


class Region(BaseModel):
    region = models.CharField(max_length=100)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.region


class District(BaseModel):
    district = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="region_related_name"
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.district


class Locality(BaseModel):
    locality = models.CharField(max_length=100)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="district_related_name"
    )
    city_type = models.PositiveSmallIntegerField(
        choices=CityType.choices, null=True, blank=True
    )
    center_type = models.PositiveSmallIntegerField(
        choices=CenterType.choices, null=True, blank=True
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.locality


class LocalityDistrict(BaseModel):
    district = models.CharField(max_length=100)
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE, related_name="locality_related_name"
    )
    description = models.TextField(null=True, blank=True)
    group_on_site = models.CharField(max_length=100, null=True, blank=True)
    hot_deals_limit = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    prefix_to_site = models.CharField(max_length=5)
    is_subdistrict = models.BooleanField()
    new_building_district = models.PositiveSmallIntegerField(
        choices=NewBuildingDistrictType.choices
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.district


class Street(BaseModel):
    street = models.CharField(max_length=100)
    locality_district = models.ForeignKey(
        LocalityDistrict,
        on_delete=models.CASCADE,
        related_name="locality_district_related_name",
    )
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE, related_name="locality_related_name_street"
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.street


class Handbook(BaseModel):
    handbook = models.CharField(max_length=100)

    type = models.PositiveSmallIntegerField(choices=HandbookType.choices)

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_handbooks", "Can view handbooks"),
            ("add_handbook", "Can add handbook"),
            ("change_handbook", "Can change handbook"),
        )
        """permissions = (
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
        )"""

    def __str__(self):
        return self.handbook


class FilialAgency(BaseModel):
    filial_agency = models.CharField(max_length=100)
    locality_district = models.ForeignKey(
        LocalityDistrict,
        on_delete=models.CASCADE,
        related_name="locality_district_agency_related_name",
    )
    phone = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    new_build_area = models.CharField(max_length=100, null=True, blank=True)
    open_date = models.DateTimeField(default=timezone.now)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.filial_agency


class FilialReport(BaseModel):
    report = models.TextField()
    filial_agency = models.ForeignKey(
        FilialAgency, on_delete=models.CASCADE, related_name="filial_agency_related_name"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_report_related_name"
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.report


class PhoneNumber(models.Model):
    """
    Номер телефону користувача
    (може бути декілька номерів у одного користувача).
    """

    number = models.CharField(max_length=15)
    user = models.ForeignKey(
        "accounts.CustomUser", related_name="phone_numbers", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.number
