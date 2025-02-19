import xml.etree.ElementTree as ET
import uuid
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import make_aware, get_current_timezone

from handbooks.choices import CityType, CenterType, NewBuildingDistrictType
from handbooks.models import Handbook, FilialAgency, Region, District, Locality, LocalityDistrict, Street

LOCALITY_TYPE_MAP = {
    "Село": CityType.VILLAGE,
    "Пгт": CityType.URBAN_TYPE_VILLAGE,
    "Город": CityType.CITY,
}

CENTER_TYPE_MAP = {
    "Районный": CenterType.DISTRICT,
    "Региональный": CenterType.REGIONAL,
    "Нет": CenterType.NONE,
}


class Command(BaseCommand):
    help = "Парсит XML и загружает данные в базу"

    def handle(self, *args, **kwargs):
        self.stdout.write("Filling Handbooks")
        Handbook.objects.all().delete()

        handbook_tree = ET.parse("xml/Catalogs16_02.xml")
        handbook_root = handbook_tree.getroot()

        handbook_fill(handbook_root, "withdrawal_reason")
        handbook_fill(handbook_root, "conditions")
        handbook_fill(handbook_root, "material")
        handbook_fill(handbook_root, "separation")
        handbook_fill(handbook_root, "agency")
        handbook_fill(handbook_root, "agency_sales")
        handbook_fill(handbook_root, "new_building_name")
        handbook_fill(handbook_root, "stair")
        handbook_fill(handbook_root, "heating")
        handbook_fill(handbook_root, "layout")
        handbook_fill(handbook_root, "house_type")

        self.stdout.write("Filling Region")
        Region.objects.all().delete()
        region_tree = ET.parse("xml/District16_02.xml")
        region_root = region_tree.getroot()
        regions = dict()
        for region in region_root.find("DistrictList"):
            region_name = region.find("Name").text

            r = Region.objects.create(
                region=region_name,
            )

            regions.update({region.find("ID").text: r, })

        self.stdout.write("Filling Districts")
        District.objects.all().delete()
        district_tree = ET.parse("xml/Region16_02.xml")
        district_root = district_tree.getroot()
        districts = dict()
        for district in district_root.find("RegionList"):
            district_name = district.find("Name").text

            d = District.objects.create(
                district=district_name,
                region=regions[district.find("DistrictId").text]
            )

            districts.update({district.find("ID").text: d, })

        self.stdout.write("Filling Localities")
        Locality.objects.all().delete()
        locality_tree = ET.parse("xml/Towns16_02.xml")
        locality_root = locality_tree.getroot()
        localities = dict()
        for locality in locality_root.find("TownList"):
            locality_name = locality.find("Name").text
            locality_type = locality.find('TownType').text if locality.find('TownType') is not None else None
            center_type = locality.find("CenterType").text if locality.find('CenterType') is not None else None

            l = Locality.objects.create(
                locality=locality_name,
                district=districts[locality.find("RegionId").text],
                city_type=LOCALITY_TYPE_MAP.get(locality_type, None),
                center_type=CENTER_TYPE_MAP.get(center_type, None),
            )

            localities.update({locality.find("ID").text: l, })

        self.stdout.write("Filling LocalityDistricts")
        LocalityDistrict.objects.all().delete()
        locality_district_tree = ET.parse("xml/TownRegions16_02.xml")
        locality_district_root = locality_district_tree.getroot()
        locality_districts = dict()
        for district in locality_district_root.find("TownRegionsList"):
            district_name = district.find("Name").text
            hot_offers_limit = float(district.find("HotOffersLimit").text) if district.find('HotOffersLimit') is not None else 0

            ld = LocalityDistrict.objects.create(
                district=district_name,
                locality=localities[district.find("TownId").text],
                description=None,
                group_on_site=None,
                hot_deals_limit=hot_offers_limit,
                prefix_to_site="",
                is_subdistrict=False,
                new_building_district=NewBuildingDistrictType.NONE,
            )

            locality_districts.update({district.find("ID").text: ld, })

        self.stdout.write("Filling Streets")
        Street.objects.all().delete()
        street_tree = ET.parse("xml/Streets16_02.xml")
        street_root = street_tree.getroot()
        for street in street_root.find("StreetList"):
            street_name = street.find("Name").text
            s = Street.objects.create(
                street=street_name,
                locality=localities[street.find("TownId").text],
                locality_district=locality_districts[street.find("TownRegionId").text]
            )

        self.stdout.write("Filling FilialAgencies")
        FilialAgency.objects.all().delete()
        filial_tree = ET.parse("xml/Branches16_02.xml")
        filial_root = filial_tree.getroot()
        for filial in filial_root.find(f"BranchList"):
            name = filial.find('Name').text
            phone = filial.find('Phone').text if filial.find('Phone') is not None else None
            email = filial.find('eMail').text if filial.find('eMail') is not None else None
            address = filial.find('Address').text if filial.find('Address') is not None else None
            filial_type = filial.find('BranchType').text if filial.find('BranchType') is not None else None
            new_build_area = filial.find('NewBuildArea').text if filial.find('NewBuildArea') is not None else None
            open_date_text = filial.find('DateOpen').text
            try:
                open_date = datetime.strptime(open_date_text, "%d.%m.%Y %H:%M:%S") if open_date_text else None
            except ValueError:
                open_date = None

            FilialAgency.objects.create(
                filial_agency=name,
                locality_district=locality_districts[filial.find('TownRegionId').text],
                phone=phone,
                email=email,
                address=address,
                type=filial_type,
                new_build_area=new_build_area,
                open_date=make_aware(open_date, get_current_timezone())
            )

        self.stdout.write(self.style.SUCCESS("Data filled successfully!"))


def handbook_fill(root, handbook_name):
    handbooks = root.find(f".//{handbook_name}")
    for handbook in handbooks.findall("Element"):
        handbook_type = int(handbook.find("CatalogId").text)
        handbook = handbook.find("Name").text.strip()

        h = Handbook.objects.create(handbook=handbook, type=handbook_type)
