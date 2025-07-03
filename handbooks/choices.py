from django.db import models
from django.utils.translation import gettext_lazy as _


class CityType(models.IntegerChoices):
    VILLAGE = 1, _("Village")
    URBAN_TYPE_VILLAGE = 2, _("Urban-type village")
    CITY = 3, _("City")


class CenterType(models.IntegerChoices):
    DISTRICT = 1, _("Districtional")
    REGIONAL = 2, _("Regional")
    NONE = 3, ""


class NewBuildingDistrictType(models.IntegerChoices):
    SEASIDE_CENTER = 1, _("Seaside+Center")
    KYIV_MALINOVSKY = 2, _("Kyiv+Malinovsky")
    SUVOROV = 3, _("Suvorov")
    NONE = 4, ""


class IncomeSourceType(models.IntegerChoices):
    RECOMMENDATIONS = 1, _("Recommendations")
    SELLER = 2, _("Seller")  # Продавець
    INTERNET = 3, _("Internet")
    VISITOR = 4, _("Visitor")
    BANNER = 5, _("Banner")
    POSTING = 6, _("Posting")  # Расклейка


class RealtorType(models.IntegerChoices):
    REALTOR = 1, _("Realtor")
    REALTOR_5_5 = 2, _("Realtor 5x5")


class ClientStatusType(models.IntegerChoices):
    IN_SEARCH = 1, _("In search")
    WITH_SHOW = 2, _("With a show")
    DECIDED = 3, _("Decided")
    DEFERRED_DEMAND = 4, _("Deferred demand")
