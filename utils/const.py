BASE_CHOICES = [
        "region", "district", "locality",
        "localitydistrict", "street",
        "withdrawalreason", "condition",
        "material", "separation", "agency",
        "agencysales", "newbuildingname", "stair",
        "heating", "layout", "housetype",
        "filialagency", "filialreport", "complex",
]
SALE_CHOICES = [
    "client", "realestate", "report"
]
USER_CHOICES = ["user", "group"]

# словник з назвами таблиць та які в них поля мають посилання до таблиці користувачів
LIST_BY_USER = {
    "client": "realtor",
    "apartment": ["realtor", "site_realtor1", "site_realtor2", "realtor_5_5"],
    "commerce": ["realtor", "site_realtor1", "site_realtor2", "realtor_5_5"],
    "house": ["realtor", "site_realtor1", "site_realtor2", "realtor_5_5"],
}
