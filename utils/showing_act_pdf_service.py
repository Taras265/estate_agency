from typing import Sequence

from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from fpdf import FPDF, FontFace
from fpdf.enums import Align, VAlign

from objects.models import BaseRealEstate, Apartment, Commerce, House, Land
from objects.choices import ShowingActType
from accounts.models import CustomUser
from handbooks.models import Client


def generate_showing_act_pdf(
    user: CustomUser,
    client: Client,
    qs: QuerySet[BaseRealEstate],
    type: ShowingActType
) -> FPDF:
    """Генерує pdf файл для акту показу об'єкту нерухомості"""
    FONT_FAMILY = "DejaVuSerif"
    FONT_SIZE = 10
    FONT_SIZE_TABLE_BODY = 9
    FPDF_FONT_DIR = "static/fonts"

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    pdf.add_font(FONT_FAMILY, fname=f"{FPDF_FONT_DIR}/{FONT_FAMILY}.ttf")
    pdf.add_font(FONT_FAMILY, "B", fname=f"{FPDF_FONT_DIR}/{FONT_FAMILY}-Bold.ttf")
    pdf.add_font(FONT_FAMILY, "I", fname=f"{FPDF_FONT_DIR}/{FONT_FAMILY}-Italic.ttf")

    # вміст файлу
    TABLE_WIDTH = pdf.w - pdf.l_margin - pdf.r_margin
    COLUMN_WIDTHS = (13, 15, 23, 53, 62, 17, 53, 23)

    pdf.set_font(FONT_FAMILY, "B", size=14)
    pdf.cell(text=_("SHOWING ACT"))
    pdf.ln(6)

    pdf.set_font(FONT_FAMILY, size=FONT_SIZE)
    pdf.cell(text=_("(of apartment, house, land, new building)"))
    pdf.ln(FONT_SIZE)

    pdf.set_x(pdf.get_x() + 6)
    pdf.cell(text=_("I am,"))

    pdf.set_line_width(0.4)
    pdf.set_draw_color(0, 0, 0)
    line_x2 = pdf.l_margin + _get_table_column_x_pos(pdf, COLUMN_WIDTHS, 5)
    pdf.line(pdf.get_x() + 3, pdf.get_y() + 4, line_x2, pdf.get_y() + 4)

    # ім'я клієнта
    pdf.set_font(FONT_FAMILY, "I", size=FONT_SIZE)
    pdf.set_x(pdf.get_x() + 5)
    pdf.cell(text=client.first_name)

    pdf.ln(5)
    pdf.set_font(FONT_FAMILY, size=FONT_SIZE)
    pdf.cell(text=_("I confirm that I received the services provided to me by the branch employee"))

    # число
    pdf.set_x(pdf.l_margin + _get_table_column_x_pos(pdf, COLUMN_WIDTHS, 6) + 15)
    pdf.cell(text='"')
    pdf.set_line_width(0.1)
    line_x2 = pdf.get_x() + 10
    pdf.line(pdf.get_x(), pdf.get_y() + 3, line_x2, pdf.get_y() + 3)
    pdf.set_x(line_x2)
    pdf.write(text='"')

    # місяць
    line_x2 = pdf.get_x() + 35
    pdf.line(pdf.get_x() + 2, pdf.get_y() + 3, line_x2, pdf.get_y() + 3)
    pdf.set_x(line_x2)

    # рік
    pdf.write(text=_("202_ y."))
    pdf.ln(5)

    pdf.cell(text=_("S. N. P. of user / filial"))

    pdf.set_line_width(0.5)
    line_x2 = pdf.l_margin + _get_table_column_x_pos(pdf, COLUMN_WIDTHS, 5)
    pdf.line(pdf.get_x() + 3, pdf.get_y() + 4, line_x2, pdf.get_y() + 4)

    # дані про користувача та філіал
    pdf.set_font(FONT_FAMILY, "I", size=FONT_SIZE)
    pdf.set_x(pdf.get_x() + 5)
    pdf.cell(text=f"{user.first_name} / {user.filials.first().filial_agency}")
    pdf.ln(FONT_SIZE)

    # таблиця
    TABLE_BODY_TEXT_ALIGN = (
        "CENTER", "CENTER", "CENTER", "LEFT", "LEFT", "CENTER", "CENTER", "CENTER", "CENTER"
    )
    TABLE_HEAD_DATA = (
        _("N"), _("ID"), _("Rubric"), _("Object's address"),
        _("Brief description of the technical condition of the display object"),
        _("Price"), _("Customer reviews and recommendations"),
        _("Customer signature")
    )
    pdf.set_font(FONT_FAMILY, size=FONT_SIZE)

    with pdf.table(
        col_widths=COLUMN_WIDTHS,
        text_align=TABLE_BODY_TEXT_ALIGN,
        v_align=VAlign.T,
        line_height=4,
    ) as table:
        # шапка таблиці
        row = table.row()
        for data in TABLE_HEAD_DATA:
            row.cell(data, align=Align.C, v_align=VAlign.B)

        # тіло таблиці
        pdf.set_line_width(0.1)

        for index, obj in enumerate(qs):
            address_data = ""
            if type == ShowingActType.SIMPLE:
                address_data = f"{obj.locality} {obj.street}"
            elif type == ShowingActType.WITH_USER_INFO:
                address_data = f"{obj.locality} {obj.street} {obj.owner.first_name} {obj.owner.last_name} {obj.owner.phone}"

            row_data = (
                str(index + 1),
                str(obj.pk),
                str(obj.get_rubric_display()),
                address_data,
                _get_real_estate_description(obj),
                str(obj.price),
                "",
                "",
            )
            table.row(row_data, style=FontFace(size_pt=FONT_SIZE_TABLE_BODY))
    
    # футер
    pdf.ln(FONT_SIZE)
    pdf.cell(text=_("The show was conducted by a real estate representative from the agency"))

    text = _("(Surname, name, signature)")
    text_width = pdf.get_string_width(text)
    text_x1 = pdf.l_margin + TABLE_WIDTH - text_width
    pdf.set_x(text_x1)
    pdf.cell(text=text)

    pdf.set_line_width(0.4)
    line_x1 = text_x1 - 90
    line_x2 = text_x1
    pdf.line(line_x1, pdf.get_y() + 4, line_x2, pdf.get_y() + 4)

    username = f"{user.last_name} {user.first_name}"
    pdf.set_x(line_x2 - pdf.get_string_width(username) - 3)
    pdf.cell(text=f"{user.last_name} {user.first_name}")

    pdf.ln(6)
    pdf.cell(text=_("This document is given to the branch director (after the transaction is completed)"))
    pdf.set_x(pdf.get_x() + 10)
    pdf.cell(text="(098)7546898, e-mail: reklama@evropa.od.ua")

    return pdf


def _get_table_column_x_pos(pdf: FPDF, column_widths: Sequence[int], column_index: int) -> float:
    """
    Повертає значення координати x для лівої межі стовпчика таблиці.
    column_index починається з 0
    """
    TABLE_WIDTH = pdf.w - pdf.l_margin - pdf.r_margin
    col_width_sum = sum(column_widths)
    normalized_col_width = [col_width / col_width_sum for col_width in column_widths]
    return sum(normalized_col_width[0:column_index]) * TABLE_WIDTH


def _get_real_estate_description(obj: BaseRealEstate) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для об'єкту нерухомості."""
    if isinstance(obj, Apartment):
        return _get_apartment_description(obj)
    if isinstance(obj, Commerce):
        return _get_commerce_description(obj)
    if isinstance(obj, House):
        return _get_house_description(obj)
    if isinstance(obj, Land):
        return _get_land_description(obj)


def _get_apartment_description(obj: Apartment) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для квартири."""
    result = ""
    if obj.floor and obj.storeys_number:
        result += _("Floor: {current}/{total}. ").format(current=obj.floor, total=obj.storeys_number)
    if obj.square and obj.living_square and obj.kitchen_square:
        result += _("Area (total/living/kitchen): {total}/{living}/{kitchen}. ").format(
            total=obj.square,
            living=obj.living_square,
            kitchen=obj.kitchen_square
        )
    if obj.house_type:
        result += _("House type: {house_type}. ").format(house_type=obj.house_type.handbook)
    if obj.layout:
        result += _("Layout: {layout}. ").format(layout=obj.layout.handbook)
    if obj.condition:
        result += _("Condition: {condition}. ").format(condition=obj.condition.handbook)
    return result


def _get_commerce_description(obj: Commerce) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для комерції."""
    result = ""
    if obj.floor and obj.storeys_number:
        result += _("Floor: {current}/{total}. ").format(current=obj.floor, total=obj.storeys_number)
    if obj.square and obj.living_square and obj.kitchen_square:
        result += _("Area (total/useful/kitchen): {total}/{useful}/{kitchen}. ").format(
            total=obj.square,
            useful=obj.useful_square,
            kitchen=obj.kitchen_square
        )
    if obj.house_type:
        result += _("House type: {house_type}. ").format(house_type=obj.house_type.handbook)
    if obj.layout:
        result += _("Layout: {layout}. ").format(layout=obj.layout.handbook)
    if obj.condition:
        result += _("Condition: {condition}. ").format(condition=obj.condition.handbook)
    return result


def _get_house_description(obj: House) -> str:
    """Повертає короткий опис технічного стану об'єкту показу для будинку."""
    result = ""
    if obj.floor and obj.storeys_number:
        result += _("Floor: {current}/{total}. ").format(current=obj.floor, total=obj.storeys_number)
    if obj.square and obj.living_square and obj.kitchen_square:
        result += _("Area (total/land/kitchen): {total}/{land}/{kitchen}. ").format(
            total=obj.square,
            land=obj.land_square,
            kitchen=obj.kitchen_square
        )
    if obj.house_type:
        result += _("House type: {house_type}. ").format(house_type=obj.house_type.handbook)
    if obj.layout:
        result += _("Layout: {layout}. ").format(layout=obj.layout.handbook)
    if obj.condition:
        result += _("Condition: {condition}. ").format(condition=obj.condition.handbook)
    return result


def _get_land_description(obj: Land) -> str:
    """
    Повертає короткий опис технічного стану об'єкту показу для земельної ділянки.
    """
    result = ""
    if obj.floor and obj.storeys_number:
        result += _("Floor: {current}/{total}. ").format(current=obj.floor, total=obj.storeys_number)
    if obj.square and obj.living_square and obj.kitchen_square:
        result += _("Area (total/land/kitchen): {total}/{land}/{kitchen}. ").format(
            total=obj.square,
            land=obj.land_square,
            kitchen=obj.kitchen_square
        )
    if obj.house_type:
        result += _("House type: {house_type}. ").format(house_type=obj.house_type.handbook)
    if obj.layout:
        result += _("Layout: {layout}. ").format(layout=obj.layout.handbook)
    if obj.condition:
        result += _("Condition: {condition}. ").format(condition=obj.condition.handbook)
    return result
