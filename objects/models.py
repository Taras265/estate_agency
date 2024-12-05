from django.db import models
from simple_history.models import HistoricalRecords

from accounts.models import CustomUser
from handbooks.models import Region, District, Locality, LocalityDistrict, Street, Handbook, Client


class Apartment(models.Model):
    creation_date = models.DateField()
    date_before_temporarily_removed = models.DateField(null=True, blank=True)
    deposit_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateField()
    sale_date = models.DateField(null=True, blank=True)
    date_of_next_call = models.DateField(null=True, blank=True)
    inspection_form = models.DateTimeField(null=True, blank=True)

    exclusive = models.BooleanField()
    exclusive_to = models.DateTimeField(null=True, blank=True)
    exclusive_from = models.DateTimeField(null=True, blank=True)

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_object_related_name")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="district_object_related_name")
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name="locality_object_related_name")
    locality_district = models.ForeignKey(LocalityDistrict, on_delete=models.CASCADE,
                                          related_name="locality_district_object_related_name")
    street = models.ForeignKey(Street, on_delete=models.CASCADE, related_name="street_object_related_name")
    house = models.CharField(max_length=100, null=True, blank=True)
    apartment = models.CharField(max_length=50, null=True, blank=True)

    on_site = models.BooleanField()
    inspection_flag = models.BooleanField()
    paid_exclusive_flag = models.BooleanField()
    terrace_flag = models.BooleanField()
    sea_flag = models.BooleanField()
    vip = models.BooleanField()

    withdrawal_reason = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                          related_name="withdrawal_reason_related_name", null=True, blank=True)
    independent = models.BooleanField()
    condition = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                  related_name="condition_related_name")
    special = models.BooleanField()
    urgently = models.BooleanField()
    trade = models.BooleanField()

    material = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                 related_name="material_related_name")

    STATUS_CHOICES = (
        (1, "В продаже"),
        (2, "Задаток"),
        (3, "Снята"),
        (4, "Продана"),
        (5, "Снята совсем")
    )

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    OBJECT_TYPE_CHOICES = (
        (1, "Квартира"),
    )

    object_type = models.PositiveSmallIntegerField(choices=OBJECT_TYPE_CHOICES, default=1)

    square = models.IntegerField()
    price = models.IntegerField()
    site_price = models.IntegerField()
    square_meter_price = models.IntegerField()

    realtor = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                related_name="object_realtor_related_name")
    site_realtor1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                      related_name="site_realtor1_related_name")
    site_realtor2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                      related_name="site_realtor2_related_name", null=True, blank=True)
    realtor_5_5 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                    related_name="realtor_5_5_related_name", null=True, blank=True)

    for_trainee = models.BooleanField()
    realtor_notes = models.TextField(null=True, blank=True)
    reference_point = models.CharField(max_length=150, null=True, blank=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name="author_related_name")
    owner = models.ForeignKey(Client, on_delete=models.CASCADE,
                              related_name="owner_related_name")
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name="client_related_name", null=True, blank=True)

    owners_number = models.PositiveSmallIntegerField()
    comment = models.TextField()

    separation = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                   related_name="separation_related_name")
    agency = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                               related_name="agency_related_name")
    agency_sales = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                     related_name="agency_sales_related_name")

    sale_terms = models.CharField(max_length=150, null=True, blank=True)
    filename_of_exclusive_agreement = models.CharField(max_length=150, null=True, blank=True)
    inspection_file_name = models.CharField(max_length=150, null=True, blank=True)
    document = models.CharField(max_length=150, null=True, blank=True)
    filename_forbid_sale = models.CharField(max_length=150, null=True, blank=True)

    new_building_name = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                          related_name="new_building_name_related_name", null=True, blank=True)
    new_building = models.BooleanField()

    NEW_BUILDING_TYPE_CHOICES = (
        (1, "От хозяина"),
        (2, "От строителя")
    )

    new_building_type = models.PositiveSmallIntegerField(choices=NEW_BUILDING_TYPE_CHOICES, null=True, blank=True)

    """
    Personal for apartments
    """
    rooms_number = models.PositiveSmallIntegerField()

    ROOM_TYPE_CHOICES = (
        (1, "Смежные"),
        (2, "Раздельные"),
        (3, "Кухня-студия"),
        (4, "Комната")
    )
    room_types = models.PositiveSmallIntegerField(choices=ROOM_TYPE_CHOICES)

    height = models.FloatField()
    kitchen_square = models.PositiveIntegerField()
    living_square = models.PositiveIntegerField()
    gas = models.BooleanField()
    courtyard = models.BooleanField()
    balcony_number = models.PositiveSmallIntegerField()
    registered_number = models.PositiveSmallIntegerField()
    child_registered_number = models.PositiveSmallIntegerField()
    loggias_number = models.PositiveSmallIntegerField()
    bay_windows_number = models.PositiveSmallIntegerField()
    commune = models.BooleanField()
    frame = models.CharField(max_length=150)
    stair = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                              related_name="stair_related_name")
    balcony = models.BooleanField()
    heating = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                related_name="heating_related_name")
    office = models.BooleanField()
    penthouse = models.BooleanField()
    parking = models.BooleanField(default=False)
    generator = models.BooleanField(default=False)
    e_home = models.BooleanField(default=False) # єОселя

    REDEVELOPMENT_CHOICES = (
        (1, "Нет"),
        (2, "Узаконенная"),
        (3, "Неузаконенная")
    )
    redevelopment = models.PositiveSmallIntegerField(choices=REDEVELOPMENT_CHOICES)

    layout = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                               related_name="layout_related_name")
    construction_number = models.CharField(max_length=150)
    house_type = models.ForeignKey(Handbook, on_delete=models.CASCADE,
                                   related_name="house_type_related_name")
    two_level_apartment = models.BooleanField()
    loggia = models.PositiveIntegerField()
    attic = models.BooleanField()
    electric_stove = models.BooleanField()
    floor = models.PositiveIntegerField()
    storeys_number = models.PositiveIntegerField()

    on_delete = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        default_permissions = ("add", "change", "view")
        permissions = (
            ("add_own_apartment", "Can add own apartment"),
            ("change_own_apartment", "Can change own apartment"),
            ("view_own_apartment", "Can view own apartment"),
            ("view_own_historicalapartment", "Can view own historical apartment"),

            ("view_report", "Can view reports"),
            ("view_contract", "Can view contracts"),
        )
