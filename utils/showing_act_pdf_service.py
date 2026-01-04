import io
from enum import Enum

import weasyprint
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from django.template import loader

from objects.models import BaseRealEstate, Apartment, Commerce, House, Land
from accounts.models import CustomUser
from handbooks.models import Client


class ShowingActPDFType(Enum):
    """Тип pdf файлу акту показу нерухомості"""
    SIMPLE = 1
    WITH_OWNER_INFO = 2


class ShowingActPDFService:
    """Генерує pdf файл акту показу нерухомості"""
    def generate(
        self,
        type: ShowingActPDFType,
        user: CustomUser,
        client: Client,
        objects: QuerySet[BaseRealEstate]
    ) -> io.BytesIO:
        template_name: str
        if type == ShowingActPDFType.SIMPLE:
            template_name = "showing_act_pdf_simple.html"
        elif type == ShowingActPDFType.WITH_OWNER_INFO:
            template_name = "showing_act_pdf_owner_info.html"
        else:
            raise ValueError("Wrong value for showing act type.")

        descriptions = {obj.id: real_estate_brief_description(obj) for obj in objects}
        context = {
            "client": client,
            "realtor": user,
            "objects": objects,
            "real_estate_descriptions": descriptions
        }
        html_string = loader.render_to_string(template_name, context)
        html = weasyprint.HTML(string=html_string, base_url="..")
        css = weasyprint.CSS("static/css/showing_act_pdf.css")
        buffer = io.BytesIO()
        html.write_pdf(buffer, stylesheets=[css])
        buffer.seek(0)
        return buffer
    

def real_estate_brief_description(real_estate: BaseRealEstate) -> str:
    """
    Повертає короткий опис технічного стану об'єкту показу.
    Якщо переданий об'єкт не є нерухомістю, буде повернуто помилку ValueError.
    """
    if type(real_estate) == Apartment:
        return apartment_brief_description(real_estate)
    if type(real_estate) == Commerce:
        return commerce_brief_description(real_estate)
    if type(real_estate) == House:
        return house_brief_description(real_estate)
    if type(real_estate) == Land:
        return land_brief_description(real_estate)
    raise ValueError("Object must be real estate")


def apartment_brief_description(apartment: Apartment) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для квартири."""
    result = []
    if apartment.floor and apartment.storeys_number:
        floor = apartment.floor
        storeys_number = apartment.storeys_number
        result.append(_("Floor: ") + f"{floor}/{storeys_number}.")

    if apartment.square and apartment.living_square and apartment.kitchen_square:
        total = apartment.square
        living = apartment.living_square
        kitchen = apartment.kitchen_square
        result.append(_("Area (total/living/kitchen): ") + f"{total}/{living}/{kitchen}.")

    if apartment.house_type:
        result.append(_("House type: ") + f"{apartment.house_type.handbook}.")

    if apartment.layout:
        result.append(_("Layout: ") + f"{apartment.layout.handbook}.")

    if apartment.condition:
        result.append(_("Condition: ") + f"{apartment.condition.handbook}.")

    return " ".join(result)


def commerce_brief_description(commerce: Commerce) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для комерції."""
    result = []
    if commerce.floor and commerce.storeys_number:
        floor = commerce.floor
        storeys_number = commerce.storeys_number
        result.append(_("Floor: ") + f"{floor}/{storeys_number}.")

    if commerce.square and commerce.living_square and commerce.kitchen_square:
        total=commerce.square,
        useful=commerce.useful_square,
        kitchen=commerce.kitchen_square
        result.append(_("Area (total/useful/kitchen): ") + f"{total}/{useful}/{kitchen}.")

    if commerce.house_type:
        result.append(_("House type: ") + f"{commerce.house_type.handbook}.")

    if commerce.layout:
        result.append(_("Layout: ") + f"{commerce.layout.handbook}.")

    if commerce.condition:
        result.append(_("Condition: ") + f"{commerce.condition.handbook}.")

    return " ".join(result)


def house_brief_description(house: House) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для будинку."""
    result = []
    if house.floor and house.storeys_number:
        floor = house.floor
        storeys_number = house.storeys_number
        result.append(_("Floor: ") + f"{floor}/{storeys_number}.")

    if house.square and house.living_square and house.kitchen_square:
        total = house.square,
        land = house.land_square,
        kitchen = house.kitchen_square
        result.append(_("Area (total/land/kitchen): ") + f"{total}/{land}/{kitchen}.")

    if house.house_type:
        result.append(_("House type: ") + f"{house.house_type.handbook}.")

    if house.layout:
        result.append(_("Layout: ") + f"{house.layout.handbook}.")

    if house.condition:
        result.append(_("Condition: ") + f"{house.condition.handbook}.")

    return " ".join(result)


def land_brief_description(land: Land) -> str:
    """
    Повертає короткий опис технічного стану об'єкту показу для земельної ділянки.
    """
    result = []
    if land.floor and land.storeys_number:
        floor = land.floor
        storeys_number = land.storeys_number
        result.append(_("Floor: ") + f"{floor}/{storeys_number}.")

    if land.square and land.living_square and land.kitchen_square:
        total = land.square,
        land = land.land_square,
        kitchen = land.kitchen_square
        result.append(_("Area (total/land/kitchen): ") + f"{total}/{land}/{kitchen}.")

    if land.house_type:
        result.append(_("House type: ") + f"{land.house_type.handbook}.")

    if land.layout:
        result.append(_("Layout: ") + f"{land.layout.handbook}.")

    if land.condition:
        result.append(_("Condition: ") + f"{land.condition.handbook}.")

    return " ".join(result)
