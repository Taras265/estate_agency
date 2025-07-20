from django.db import models
from django.utils.translation import gettext_lazy as _


class RealEstateType(models.IntegerChoices):
    """Тип обʼєкта нерухомості"""

    APARTMENT = 1, _("Apartment")
    COMMERCE = 2, _("Commerce")
    HOUSE = 3, _("House")
    LAND = 4, _("Land")


class RealEstateStatus(models.IntegerChoices):
    """Статус обʼєкта нерухомості"""

    ON_SALE = 1, _("On sale")  # В продаже
    DEPOSIT = 2, _("Advance")  # Аванс
    WITHDRAWN = 3, _("Withdrawn")  # Снята
    SOLD = 4, _("Sold")  # Продана
    COMPLETELY_WITHDRAWN = 5, _("Completely withdrawn")  # Снята совсем


class RoomType(models.IntegerChoices):
    """Тип кімнат (рубрика) обʼєкта нерухомості"""

    ADJACENT = 1, _("Adjacent")  # Смежные
    SEPARATE = 2, _("Separate")  # Раздельные
    STUDIO_KITCHEN = 3, _("Studio")  # Студия
    NONE = 4, "---"


class LandTarget(models.IntegerChoices):
    """Назначення землі в земельній ділянці"""

    DWELLING = 1, _("Dwelling")  # Житло
    COMMERCE = 2, _("Commerce")  # Комерція


class LandDisposition(models.IntegerChoices):
    """Розташування земельної ділянки"""

    FACADE = 1, _("Facade")  # Фасад
    INTERNAL = 2, _("Internal")  # Внутрішній
    CORNER = 3, _("Corner")  # Кутовий
