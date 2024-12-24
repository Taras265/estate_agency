from fpdf import FPDF, FontFace
from fpdf.enums import Align, VAlign
from fpdf.template import FlexTemplate

from django.db.models.query import QuerySet
from objects.models import Apartment


document_data_ua: tuple[str] = (
    # head data
    'АКТ ПОКАЗУ',
    '(квартири, домоволодіння, земельної ділянки, об\'єкту новобудови)',
    '     Я, ',
    'підтверджую, що прийняв послуги, надані мені співробітником філії',
    '202_р.',
    'П.І.Б представника / філіал',

    # table head data
    '№ п/п', 
    'ID', 
    'К-сть кімнат', 
    'Адреса обʼекту', 
    'Короткий опис технічного стану об\'єкта показу', 
    'Ціна', 
    'Ціна за 1кв.м', 
    'Відгуки та рекомендації клієнта', 
    'Підпис клієнта',

    # table body data
    'Поверх',
    'Площа (заг/житл/кухня)',
    'Тип дому',
    'Планування',
)

TABLE_WIDTH = 277
COLUMN_WIDTHS = (14, 17, 17, 56, 62, 17, 19, 56, 20)


def generate_pdf(data: QuerySet[Apartment], username: str) -> FPDF:

    font_family = 'DejaVuSerif'
    font_size = 10
    font_size_table_body = 9

    pdf = FPDF(orientation='L', unit='mm', format='A4')

    FPDF_FONT_DIR = 'static/fonts'

    pdf.add_page()

    pdf.add_font(font_family, fname=f'{FPDF_FONT_DIR}/{font_family}.ttf')
    pdf.add_font(font_family, 'B', fname=f'{FPDF_FONT_DIR}/{font_family}-Bold.ttf')
    pdf.add_font(font_family, 'I', fname=f'{FPDF_FONT_DIR}/{font_family}-Italic.ttf')

    # document content
    pdf.set_font(font_family, 'B', size=14)

    # current index for document_data_ua
    data_index = 0

    # print text
    pdf.write(text=document_data_ua[data_index])
    data_index += 1
    pdf.ln(font_size / 1.5)

    pdf.set_font(font_family, size=font_size)

    pdf.write(text=document_data_ua[data_index])
    data_index += 1
    pdf.ln(font_size)

    pdf.write(text=document_data_ua[data_index])
    data_index += 1

    # print line
    line_x2 = pdf.l_margin + sum(COLUMN_WIDTHS[0:5]) - 1

    pdf.set_line_width(0.4)
    pdf.set_draw_color(0, 0, 0)
    pdf.line(pdf.get_x() + 3, pdf.get_y() + 3, line_x2, pdf.get_y() + 3)

    # print username
    elements: list[dict] = [
        {
            'name': 'username', 
            'type': 'T', 
            'x1': 30, 'y1': 27, 'x2': 30 + line_x2, 'y2': 27, 
            'font': font_family, 'size': font_size, 'italic': True
        }
    ]

    template = FlexTemplate(pdf, elements)
    template['username'] = username
    template.render()

    pdf.ln(font_size / 1.5)

    # print text
    pdf.write(text=document_data_ua[data_index])
    data_index += 1

    # print place for current date
    pdf.set_x(pdf.l_margin + sum(COLUMN_WIDTHS[0:7]))

    pdf.write(text='"')

    pdf.set_line_width(0.1)

    line_x2 = pdf.get_x() + 10
    pdf.line(pdf.get_x() + 2, pdf.get_y() + 3, line_x2, pdf.get_y() + 3)
    pdf.set_x(line_x2)

    pdf.write(text='"')

    line_x2 = pdf.get_x() + 35
    pdf.line(pdf.get_x() + 2, pdf.get_y() + 3, line_x2, pdf.get_y() + 3)
    pdf.set_x(line_x2)

    pdf.write(text=document_data_ua[data_index])
    data_index += 1

    pdf.ln(font_size / 1.5)

    # print text
    pdf.write(text=document_data_ua[data_index])
    data_index += 1

    # print line
    line_x2 = pdf.l_margin + sum(COLUMN_WIDTHS[0:5]) - 1

    pdf.set_line_width(0.5)
    pdf.line(pdf.get_x() + 3, pdf.get_y() + 3, line_x2, pdf.get_y() + 3)
    pdf.ln(font_size)

    # print table
    with pdf.table(width=TABLE_WIDTH, col_widths=COLUMN_WIDTHS, text_align='CENTER', v_align=VAlign.B, line_height=4) as table:

        # table head
        table.row(document_data_ua[data_index:data_index + 9])
        data_index += 9

        # table body
        pdf.set_line_width(0.1)

        for row_index, apartment in enumerate(data):

            row = table.row(style=FontFace(size_pt=font_size_table_body))

            # tuple with text in each cell in current row
            data_row: tuple[str] = (
                str(row_index + 1), # first cell
                str(apartment.pk), # second
                str(apartment.rooms_number), # third
                f'{apartment.region} {apartment.district} {apartment.locality} {apartment.locality_district} {apartment.street}', # fourth

                f'{document_data_ua[data_index]}: {apartment.floor}/{apartment.storeys_number}. ' +
                f'{document_data_ua[data_index + 1]}: {apartment.square}/{apartment.living_square}/{apartment.kitchen_square}. ' + 
                f'{document_data_ua[data_index + 2]}: {apartment.house_type.handbook}.', # fifth

                str(apartment.site_price), # sixth
                str(apartment.square_meter_price), # seventh
                apartment.comment, # eighth
                '' # ninth
            )

            for cell_index, cell_data in enumerate(data_row):

                text_align: Align = Align.L if cell_index in (3, 4, 7) else Align.C

                row.cell(cell_data, text_align, VAlign.T)


    return pdf
