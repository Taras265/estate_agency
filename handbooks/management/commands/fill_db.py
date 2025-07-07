import xml.etree.ElementTree as ET
import uuid
from datetime import datetime

from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import make_aware, get_current_timezone

from accounts.models import CustomUser
from handbooks.choices import CityType, CenterType, NewBuildingDistrictType
from handbooks.management.commands.utils import get_date, handbook_fill
from handbooks.models import Handbook, FilialAgency, Region, District, Locality, LocalityDistrict, Street, Client
from objects.choices import RealEstateStatus, RoomType
from objects.models import Apartment, House, Commerce

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

STATUS_MAP = {
    "В продаже": RealEstateStatus.ON_SALE,
    "Задаток": RealEstateStatus.DEPOSIT,
    "Временно снята": RealEstateStatus.WITHDRAWN,
    "Продана":RealEstateStatus.SOLD,
    "Снята": RealEstateStatus.COMPLETELY_WITHDRAWN,
}


ROOMS_TYPE_MAP = {
    "Смежные": RoomType.ADJACENT,
    "Раздельные": RoomType.SEPARATE,
    "Кухня-студия": RoomType.STUDIO_KITCHEN,
    "1 комната ":RoomType.NONE,
}


class Command(BaseCommand):
    help = "Парсит XML и загружает данные в базу"

    def handle(self, *args, **kwargs):
        Permission.objects.filter(codename__icontains="history").delete()
        Permission.objects.filter(codename__icontains="historical").delete()
        Permission.objects.filter(codename__icontains="session").delete()
        Permission.objects.filter(codename__icontains="log").delete()
        Permission.objects.filter(codename__icontains="permission").delete()
        Permission.objects.filter(codename__icontains="contenttype").delete()
        Permission.objects.filter(codename__icontains="delete").delete()

        Client.objects.all().delete()
        client = {
            "date_of_add": datetime.now(),
            "email": "client@gmail.com",
            "first_name": "Client",
            "last_name": "Test Client",
            "phone": "050",
            "messenger": "viber",
            "realtor": CustomUser.objects.all().first()
        }
        client = Client.objects.create(**client)

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

        Handbook.objects.create(type=12, handbook="Complex")

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
        streets = dict()
        for street in street_root.find("StreetList"):
            street_name = street.find("Name").text
            s = Street.objects.create(
                street=street_name,
                locality=localities[street.find("TownId").text],
                locality_district=locality_districts[street.find("TownRegionId").text]
            )
            streets.update({street.find("ID").text: s, })

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
            open_date = get_date(filial, "DateOpen", "%d.%m.%Y %H:%M:%S")

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

        self.stdout.write("Filling Objects")
        Apartment.objects.all().delete()
        Commerce.objects.all().delete()
        House.objects.all().delete()

        object_tree = ET.parse("xml/Catalog_22_02.xml")
        object_root = object_tree.getroot()
        for obj in object_root.find("Catalog"):

            obj_data = {
                "deposit_date": get_date(obj, "deposit_date", "%d.%m.%Y"),
                "exclusive": bool(obj.find("exclusive")) if obj.find("exclusive") else False,
                "locality": localities[obj.find("locality").text],
                "street": streets[obj.find("street").text],
                "house": obj.find("house").text,

                "realtor": CustomUser.objects.all().first(),
                "condition": Handbook.objects.filter(type=2, handbook=obj.find("condition").text).first()
                                            if obj.find('condition') is not None else None,
                "material": Handbook.objects.filter(type=3, handbook=obj.find("material").text).first()
                                            if obj.find('material') is not None else None,
                "agency": Handbook.objects.filter(type=5).first(),
                "house_type": Handbook.objects.filter(type=11, handbook=obj.find("house_type").text).first()
                                            if obj.find('house_type') is not None else None,
                "layout": Handbook.objects.filter(type=10, handbook=obj.find("layout").text).first()
                                            if obj.find('layout') is not None else None,
                "stair": Handbook.objects.filter(type=8, handbook=obj.find("stair").text).first()
                                        if obj.find('stair') is not None else None,
                "owner": client,
                "parking": bool(obj.find("parking")) if obj.find("parking") else False,
                "generator": bool(obj.find("generator")) if obj.find("generator") else False,
                "e_home": bool(obj.find("e_home")) if obj.find("e_home") else False,

                "price": int(obj.find("price").text),
                "square": int(float(obj.find("square").text)),
                "kitchen_square": int(float(obj.find("kitchen_square").text)),
                "height": float(obj.find("height").text),
                "floor": int(obj.find("floor").text),
                "storeys_number": int(obj.find("storeys_number").text),

                "status": STATUS_MAP[obj.find("status").text],
                "room_types": ROOMS_TYPE_MAP[obj.find('room_types').text] if obj.find('room_types') is not None
                                            else RoomType.NONE,

                "document": obj.find("document").text,
                "sale_terms": obj.find("sale_terms").text if obj.find('sale_terms') is not None else None,
                "realtor_notes": obj.find('realtor_notes').text if obj.find('realtor_notes') is not None else None,
                "comment": obj.find('comment').text if obj.find('comment') is not None else None,
            }
            if obj.find("creation_date"):
                obj_data["creation_date"] = get_date(obj, "creation_date", "%d.%m.%Y")

            if obj.find("object_type").text == "квартира":
                print(obj.find("living_square").text)
                obj_data.update({
                    "apartment": obj.find("apartment").text,
                    "living_square": int(float(obj.find("living_square").text)),
                    "balcony": bool(obj.find("balcony")) if obj.find("balcony") else False,
                    "balcony_number": int(obj.find("balcony_number").text),
                    "complex": Handbook.objects.filter(type=12).first(),
                })
                Apartment.objects.create(**obj_data)
            elif obj.find("object_type").text == "дом":
                obj_data.update({
                    "housing":  obj.find("housing").text if obj.find('housing') is not None else None,
                    "useful_square": int(float(obj.find("useful_square").text))
                                        if obj.find('useful_square') is not None else None,
                    "land_square": int(float(obj.find("land_square").text))
                                        if obj.find('land_square') is not None else None,
                    "rooms_number": int(obj.find("rooms_number").text)
                                        if obj.find('rooms_number') is not None else None,
                    "communications": bool(obj.find("communications")) if obj.find("communications") else False,
                    "terrace": bool(obj.find("terrace")) if obj.find("terrace") else False,
                    "facade": bool(obj.find("facade")) if obj.find("facade") else False,
                    "own_parking": bool(obj.find("own_parking")) if obj.find("own_parking") else False,
                })

                House.objects.create(**obj_data)
            elif obj.find("object_type").text == "комерция":
                obj_data.update({
                    "premises": obj.find("premises").text if obj.find('premises') is not None else "",
                    "useful_square": int(obj.find("useful_square").text)
                    if obj.find('useful_square') is not None else None,
                    "balcony": bool(obj.find("balcony")) if obj.find("balcony") else False,
                    "balcony_number": int(obj.find("balcony_number").text)
                    if obj.find('balcony_number') is not None else 0,
                    "ground_floor": bool(obj.find("ground_floor")) if obj.find("ground_floor") else False,
                    "facade": bool(obj.find("balcony")) if obj.find("balcony") else False,
                    "own_parking": bool(obj.find("own_parking")) if obj.find("own_parking") else False,
                    "own_courtyard": bool(obj.find("own_courtyard")) if obj.find("own_courtyard") else False,
                    "separate_building": bool(obj.find("separate_building")) if obj.find(
                        "separate_building") else False,
                    "complex": Handbook.objects.filter(type=12).first()
                })
                Commerce.objects.create(**obj_data)

        self.stdout.write(self.style.SUCCESS("Data filled successfully!"))
