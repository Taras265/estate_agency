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


class ApartmentRubric(models.IntegerChoices):
    """Рубрика квартири"""

    ONE_ROOM = 1, _("1 room")  # 1 кімнатна
    TWO_ROOM = 2, _("2 rooms")  # 2 кімнатна
    THREE_ROOM = 3, _("3 rooms")  # 3 кімнатна
    MANY_ROOMS = 4, _("Many rooms")  # багато кімнат


class CommerceRubric(models.IntegerChoices):
    """Рубрика комерції"""
    RESIDENTIAL = 1, _("Residential")  # Житлова
    NOT_RESIDENTIAL = 2, _("Not residential")  # Не житлова


class HouseRubric(models.IntegerChoices):
    """Рубрика будинку"""
    HOUSE = 1, _("House")  # будинок


class LandRubric(models.IntegerChoices):
    """Рубрика ділянки"""
    HOUSE = 1, _("House")  # будинок
    LAND = 2, _("Land")  # ділянка


class LandTarget(models.IntegerChoices):
    """Назначення землі в земельній ділянці"""

    DWELLING = 1, _("Dwelling")  # Житло
    COMMERCE = 2, _("Commerce")  # Комерція


class LandDisposition(models.IntegerChoices):
    """Розташування земельної ділянки"""

    FACADE = 1, _("Facade")  # Фасад
    INTERNAL = 2, _("Internal")  # Внутрішній
    CORNER = 3, _("Corner")  # Кутовий
