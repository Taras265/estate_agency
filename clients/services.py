import io
from enum import Enum
from typing import Any

import weasyprint
from django.db.models import QuerySet, Q, F
from django.template import loader
from django.utils.translation import gettext as _

from .models import Client, Selection
from accounts.models import CustomUser
from objects.models import (
    BaseRealEstate,
    Apartment,
    Commerce,
    House,
    Land
)
from .forms import SelectionForm
from objects.choices import RealEstateType


def selection_add_selected_objects(
    selection: Selection, object_type: int, *objects: BaseRealEstate
) -> None:
    """
    Функція для того, щоб створити запис того, що ми зробили вибірку для клієнтів (Selection)
    """
    if object_type == RealEstateType.APARTMENT:
        selection.selected_apartments.add(*objects)
    elif object_type == RealEstateType.COMMERCE:
        selection.selected_commerces.add(*objects)
    elif object_type == RealEstateType.HOUSE:
        selection.selected_houses.add(*objects)
    elif object_type == RealEstateType.LAND:
        selection.selected_lands.add(*objects)


class ShowingActPDFType(Enum):
    """Тип pdf файлу акту показу нерухомості"""
    SIMPLE = 1
    WITH_OWNER_INFO = 2


class ShowingActPDFService:
    """Генерує pdf файл акту показу нерухомості"""
    def generate(
        self,
        showing_act_type: ShowingActPDFType,
        user: CustomUser,
        client: Client,
        objects: QuerySet[BaseRealEstate]
    ) -> io.BytesIO:
        template_name: str
        if showing_act_type == ShowingActPDFType.SIMPLE:
            template_name = "showing_act_pdf_simple.html"
        elif showing_act_type == ShowingActPDFType.WITH_OWNER_INFO:
            template_name = "showing_act_pdf_owner_info.html"
        else:
            raise ValueError("Wrong value for showing act type.")

        descriptions = {obj.id: self._real_estate_brief_description(obj) for obj in objects}
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


    @classmethod
    def _real_estate_brief_description(cls, real_estate: BaseRealEstate) -> str:
        """
        Повертає короткий опис технічного стану об'єкту показу.
        Якщо переданий об'єкт не є нерухомістю, буде повернуто помилку ValueError.
        """
        if type(real_estate) == Apartment:
            return cls._apartment_brief_description(real_estate)
        if type(real_estate) == Commerce:
            return cls._commerce_brief_description(real_estate)
        if type(real_estate) == House:
            return cls._house_brief_description(real_estate)
        if type(real_estate) == Land:
            return cls._land_brief_description(real_estate)
        raise ValueError("Object must be of type BaseRealEstate")

    @staticmethod
    def _apartment_brief_description(apartment: Apartment) -> str:
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

    @staticmethod
    def _commerce_brief_description(commerce: Commerce) -> str:
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

    @staticmethod
    def _house_brief_description(house: House) -> str:
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

    @staticmethod
    def _land_brief_description(land: Land) -> str:
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


def process_selection_form(
    qs: QuerySet[BaseRealEstate],
    form: SelectionForm
) -> QuerySet[BaseRealEstate]:
    print(form.cleaned_data, flush=True)

    if rooms := form.cleaned_data.get("rooms_number"):
        qs = qs.filter(rooms_number=rooms)

    if (localities := form.cleaned_data.get("locality")).exists():
        qs = qs.filter(locality__in=localities)
    # if (locality_districts := form.cleaned_data.get("locality_district")).exists():
    #     qs = qs.filter(street__locality_district__in=locality_districts)
    if (street := form.cleaned_data.get("street")).exists():
        qs = qs.filter(street__in=street)
    if house := form.cleaned_data.get("house"):
        qs = qs.filter(house=house)

    if floor_min := form.cleaned_data.get("floor_min"):
        qs = qs.filter(floor__gte=floor_min)
    if floor_max := form.cleaned_data.get("floor_max"):
        qs = qs.filter(floor__lte=floor_max)

    if form.cleaned_data.get("not_first"):
        qs = qs.exclude(floor=1)
    if form.cleaned_data.get("not_last"):
        qs = qs.exclude(floor=F("storeys_number"))

    if price_from := form.cleaned_data.get("price_from"):
        qs = qs.filter(price__gte=price_from)
    if price_to := form.cleaned_data.get("price_to"):
        qs = qs.filter(price__lte=price_to)

    if sq_meter_price_max := form.cleaned_data.get("square_meter_price_max"):
        qs = qs.filter(square_meter_price__lte=sq_meter_price_max)

    if (conditions := form.cleaned_data.get("condition")).exists():
        qs = qs.filter(condition__in=conditions)

    if keyword := form.cleaned_data.get("key_word"):
        qs = qs.filter(
            Q(locality__locality__icontains=keyword)
            | Q(street__street__icontains=keyword)
            | Q(house__icontains=keyword)
            | Q(comment__icontains=keyword)
        )

    return qs


def user_can_update_client_list(user: CustomUser, clients: QuerySet[Client]) -> dict[int, bool]:
    """
    Перевіряє для кожного клієнта з <clients> чи може користувач <user> його редагувати.
    Повертає словник, в якому ключі - id клієнта, значення - True/False.
    """

    if user.has_perm("handbooks.change_own_client"):
        return {client.id: user == client.realtor for client in clients}

    return {client.id: False for client in clients}


def get_client_list_context(lang: str, user: CustomUser, object_list) -> dict[str, Any]:
    context = {
        "lang": lang,
        "can_update_clients": user_can_update_client_list(user, object_list),
        "can_view_client_history": user.has_perm("handbooks.view_own_clients"),
        "can_add_client": user.has_perm("handbooks.add_own_client")
    }
    return context