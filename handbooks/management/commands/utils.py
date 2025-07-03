import xml.etree.ElementTree as ET
from datetime import datetime

from handbooks.models import Handbook


def handbook_fill(root, handbook_name):
    handbooks = root.find(f".//{handbook_name}")
    for handbook in handbooks.findall("Element"):
        handbook_type = int(handbook.find("CatalogId").text)
        handbook = handbook.find("Name").text.strip()

        Handbook.objects.create(handbook=handbook, type=handbook_type)


def get_date(obj: ET.Element, field: str, f: str):  # f - format
    field = obj.find(field).text
    try:
        return datetime.strptime(field, f) if field else None
    except ValueError:
        return None
