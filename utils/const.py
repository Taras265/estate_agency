from django.utils.translation import gettext as _

BASE_CHOICES = [
    (_("region"), "region"),
    (_("district"), "district"),
    (_("locality"), "locality"),
    (_("localitydistrict"), "localitydistrict"),
    (_("street"), "street"),
    (_("withdrawalreason"), "withdrawalreason"),
    (_("condition"), "condition"),
    (_("material"), "material"),
    (_("separation"), "separation"),
    (_("agency"), "agency"),
    (_("agencysales"), "agencysales"),
    (_("newbuildingname"), "newbuildingname"),
    (_("stair"), "stair"),
    (_("heating"), "heating"),
    (_("layout"), "layout"),
    (_("housetype"), "housetype"),
    (_("filialagency"), "filialagency"),
    (_("filialreport"), "filialreport"),
    (_("complex"), "complex"),
]
SALE_CHOICES = [
    (_("client"), "client"),
    (_("realestate"), "realestate"),
    (_("report"), "report"),
]
USER_CHOICES = [(_("user"), "user"), (_("group"), "group")]

TABLE_TO_APP = {
    "region": "handbooks",
    "district": "handbooks",
    "locality": "handbooks",
    "localitydistrict": "handbooks",
    "street": "handbooks",
    "client": "handbooks",
    "filialagency": "handbooks",
    "filialreport": "handbooks",
    "apartment": "objects",
    "commerce": "objects",
    "house": "objects",
    "withdrawalreason": "handbooks",
    "condition": "handbooks",
    "material": "handbooks",
    "separation": "handbooks",
    "agency": "handbooks",
    "agencysales": "handbooks",
    "newbuildingname": "handbooks",
    "stair": "handbooks",
    "heating": "handbooks",
    "layout": "handbooks",
    "housetype": "handbooks",
    "report": "objects",
    "history_report": "objects",
    "contract": "objects",
    "complex": "handbooks",
    "user": "accounts",
    "group": "accounts",
}

OBJECT_COLUMNS = {
    "district": [
        "id",
        "district",
        "region",
    ],
    "locality": [
        "id",
        "locality",
        "district",
        "city type",
        "center type",
    ],
    "localitydistrict": [
        "id",
        "district",
        "locality",
        "description",
        "group on site",
        "hot deals limit",
        "prefix to site",
        "new building district",
    ],
    "street": [
        "id",
        "street",
        "locality district",
    ],
    "client": [
        "id",
        "email",
        "first_name",
        "object_type",
        "phone",
        "status",
    ],
    "apartment": [
        "id",
        "locality",
        "street",
    ],
    "filialagency": [
        "id",
        "filial agency",
    ],
    "filialreport": [
        "id",
        "report",
        "filial agency",
        "user",
    ],
    "report": [
        "id",
        "locality",
        "street",
        "floor",
        "creation date",
        "price",
        "status",
        "owner",
    ],
    "contract": [
        "id",
        "locality",
        "street",
    ],
    "user": ["id", "email", "first_name", "last_name", "phone_numbers"],
}

# хеш-таблиця, в якій ключі - це назви таблиць з БД,
# а значення - список полів відповідної таблиці, які потрібно відображати на вебсторінці
OBJECT_FIELDS = {
    "district": [
        "id",
        "district",
        "region__region",
    ],
    "locality": [
        "id",
        "locality",
        "district__district",
        "city_type",
        "center_type",
    ],
    "localitydistrict": [
        "id",
        "district",
        "locality__locality",
        "description",
        "group_on_site",
        "hot_deals_limit",
        "prefix_to_site",
        "new_building_district",
    ],
    "street": [
        "id",
        "street",
        "locality_district__district",
    ],
    "client": ["id", "email", "first_name", "object_type", "phone", "status"],
    "apartment": [
        "id",
        "locality__locality",
        "street__street",
    ],
    "filialreport": [
        "id",
        "report",
        "filial_agency__filial_agency",
        "user__email",
    ],
    "filialagency": [
        "id",
        "filial_agency",
    ],
    "report": [
        "id",
        "locality__locality",
        "street__street",
        "floor",
        "creation_date",
        "price",
        "status",
        "owner__email",
    ],
    "contract": [
        "id",
        "locality__locality",
        "street__street",
    ],
    "user": ["id", "email", "first_name", "last_name", "phone_numbers__number"],
}

LIST_BY_USER = {
    "client": "realtor",
    "apartment": ["realtor", "site_realtor1", "site_realtor2", "realtor_5_5"],
}
