from django.db import models


class RealEstateType(models.IntegerChoices):
    """Тип обʼєкта нерухомості"""
    APARTMENT = 1, "Apartment"
    COMMERCE = 2, "Commerce"
    HOUSE = 3, "House"


class RealEstateStatus(models.IntegerChoices):
    """Статус обʼєкта нерухомості"""
    ON_SALE = 1, "В продаже"
    DEPOSIT = 2, "Задаток"
    WITHDRAWN = 3, "Снята"
    SOLD = 4, "Продана"
    COMPLETELY_WITHDRAWN = 5, "Снята совсем"


class RoomType(models.IntegerChoices):
    """Тип кімнат (рубрика) обʼєкта нерухомості"""
    ADJACENT = 1, "Смежные"
    SEPARATE = 2, "Раздельные"
    STUDIO_KITCHEN = 3, "Кухня-студия"
    ROOM = 4, "Комната"
