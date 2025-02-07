import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from simple_history.models import HistoricalRecords

from images.models import RealEstateImage
from accounts.models import CustomUser
from handbooks.models import Locality, Street, Handbook, Client
from .choices import RealEstateStatus, RoomType


class BaseRealEstate(models.Model):
    """
    Базовий клас, який містить спільні поля для 
    обʼєктів нерухомості: квартири, комерції та будинку.
    """
    class Meta:
        abstract = True
        default_permissions = ("add", "change", "view")
    
    creation_date = models.DateField() # дата побудови
    deposit_date = models.DateField(null=True, blank=True) # дата постановки
    # date_before_temporarily_removed = models.DateField(null=True, blank=True)
    # purchase_date = models.DateField(null=True, blank=True)
    # sale_date = models.DateField(null=True, blank=True)
    # date_of_next_call = models.DateField(null=True, blank=True)
    # inspection_form = models.DateTimeField(null=True, blank=True)

    exclusive = models.BooleanField(default=False)
    # exclusive_to = models.DateTimeField(null=True, blank=True)
    # exclusive_from = models.DateTimeField(null=True, blank=True)

    # region = models.ForeignKey(
    #     Region,
    #     on_delete=models.CASCADE,
    #     null=True, blank=True
    # )
    # district = models.ForeignKey(
    #     District,
    #     on_delete=models.CASCADE,
    #     null=True, blank=True,
    # )
    locality = models.ForeignKey(
        Locality,
        on_delete=models.CASCADE,
    )
    # locality_district = models.ForeignKey(
    #     LocalityDistrict,
    #     on_delete=models.CASCADE,
    # )
    street = models.ForeignKey(
        Street,
        on_delete=models.CASCADE,
    )
    house = models.CharField(max_length=100)

    realtor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)ss",
    )
    # site_realtor1 = models.ForeignKey(
    #     CustomUser, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="%(app_label)s_%(class)ss",
    # )
    # site_realtor2 = models.ForeignKey(
    #     CustomUser, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="%(app_label)s_%(class)ss",
    # )
    # realtor_5_5 = models.ForeignKey(
    #     CustomUser, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="%(app_label)s_%(class)ss",
    # )
    condition = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="condition_%(app_label)s_%(class)ss",
    )
    material = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="material_%(app_label)s_%(class)ss",
    )
    agency = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="agency_%(app_label)s_%(class)ss",
    )
    house_type = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="house_type_%(app_label)s_%(class)ss",
    )
    layout = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="layout_%(app_label)s_%(class)ss",
    )
    stair = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="stair_%(app_label)s_%(class)ss",
    )
    # withdrawal_reason = models.ForeignKey(
    #     Handbook, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="withdrawal_reason_%(app_label)s_%(class)ss",
    # )
    # separation = models.ForeignKey(
    #     Handbook, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="separation_%(app_label)s_%(class)ss",
    # )
    # agency_sales = models.ForeignKey(
    #     Handbook, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="agency_sales_%(app_label)s_%(class)ss",
    # )

    owner = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name="owner_%(app_label)s_%(class)ss",
    )
    # author = models.ForeignKey(
    #     CustomUser, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="author_%(app_label)s_%(class)ss",
    # )
    # client = models.ForeignKey(
    #     Client, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="client_%(app_label)s_%(class)ss",
    # )

    # for_trainee = models.BooleanField(null=True, blank=True)
    # on_site = models.BooleanField(default=True)
    # inspection_flag = models.BooleanField(null=True, blank=True)
    # paid_exclusive_flag = models.BooleanField(null=True, blank=True)
    # sea_flag = models.BooleanField(null=True, blank=True)
    # vip = models.BooleanField(null=True, blank=True)
    # independent = models.BooleanField(null=True, blank=True)
    # special = models.BooleanField(null=True, blank=True)
    # urgently = models.BooleanField(null=True, blank=True)
    # trade = models.BooleanField(null=True, blank=True)
    parking = models.BooleanField(default=False)
    generator = models.BooleanField(default=False)
    e_home = models.BooleanField(default=False) # єОселя
    on_delete = models.BooleanField(default=False)

    price = models.IntegerField()
    # site_price = models.IntegerField(null=True, blank=True)
    # square_meter_price = models.IntegerField(null=True, blank=True)
    square = models.IntegerField()
    kitchen_square = models.PositiveIntegerField()
    height = models.FloatField()
    # owners_number = models.PositiveSmallIntegerField(null=True, blank=True)
    floor = models.PositiveIntegerField()
    storeys_number = models.PositiveIntegerField()
    
    status = models.PositiveSmallIntegerField(choices=RealEstateStatus.choices)
    room_types = models.PositiveSmallIntegerField(choices=RoomType.choices) # рубрика

    document = models.CharField(max_length=150, blank=True)
    # filename_of_exclusive_agreement = models.CharField(max_length=150, null=True, blank=True)
    # inspection_file_name = models.CharField(max_length=150, null=True, blank=True)
    # filename_forbid_sale = models.CharField(max_length=150, null=True, blank=True)
    # reference_point = models.CharField(max_length=150, null=True, blank=True)

    sale_terms = models.CharField(max_length=150, blank=True)
    realtor_notes = models.TextField(blank=True)
    comment = models.TextField()

    images = GenericRelation(
        RealEstateImage,
        related_query_name="%(app_label)s_%(class)s"
    )
    history = HistoricalRecords(inherit=True)

    def delete(self):
        self.on_delete = True
        self.save()


class Apartment(BaseRealEstate):
    """Квартира"""
    class Meta(BaseRealEstate.Meta):
        permissions = (
            ("add_own_apartment", "Can add own apartment"),
            ("change_own_apartment", "Can change own apartment"),
            ("view_own_apartment", "Can view own apartment"),
            ("view_own_historicalapartment", "Can view own historical apartment"),

            ("view_report", "Can view reports"),
            ("view_contract", "Can view contracts"),
        )

    apartment = models.CharField(max_length=50)
    living_square = models.PositiveIntegerField()
    balcony = models.BooleanField(default=False)
    balcony_number = models.PositiveSmallIntegerField(default=0)
    complex = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="complex_objects_apartment",
    )

    # two_level_apartment = models.BooleanField(default=False)
    # commune = models.BooleanField(default=False)
    # penthouse = models.BooleanField(default=False)
    # electric_stove = models.BooleanField(default=False)
    # new_building = models.BooleanField(default=False)
    # new_building_name = models.ForeignKey(
    #     Handbook, on_delete=models.CASCADE, null=True, blank=True,
    # )
    # NEW_BUILDING_TYPE_CHOICES = (
    #     (1, "От хозяина"),
    #     (2, "От строителя")
    # )
    # new_building_type = models.PositiveSmallIntegerField(
    #     choices=NEW_BUILDING_TYPE_CHOICES, null=True, blank=True
    # )
    # rooms_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # loggia = models.PositiveIntegerField(null=True, blank=True)
    # loggias_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # registered_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # child_registered_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # bay_windows_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # REDEVELOPMENT_CHOICES = (
    #     (1, "Нет"),
    #     (2, "Узаконенная"),
    #     (3, "Неузаконенная")
    # )
    # redevelopment = models.PositiveSmallIntegerField(
    #     choices=REDEVELOPMENT_CHOICES, null=True, blank=True
    # )
    # construction_number = models.CharField(max_length=150)
    # heating = models.ForeignKey(
    #     Handbook, on_delete=models.CASCADE, null=True, blank=True,
    #     related_name="%(app_label)s_%(class)ss",
    # )


class Commerce(BaseRealEstate):
    """Комерційна нерухомість"""
    class Meta(BaseRealEstate.Meta):
        permissions = (
            ("add_own_commerce", "Can add own commerce"),
            ("change_own_commerce", "Can change own commerce"),
            ("view_own_commerce", "Can view own commerce"),
            ("view_own_historicalcommerce", "Can view own historical commerce"),
        )

    premises = models.CharField(max_length=50) # приміщення
    useful_square = models.PositiveIntegerField() # корисна площа
    balcony = models.BooleanField(default=False)
    balcony_number = models.PositiveSmallIntegerField(default=0)
    ground_floor = models.BooleanField(default=False) # цоколь
    facade = models.BooleanField(default=False)
    own_parking = models.BooleanField(default=False)
    own_courtyard = models.BooleanField(default=False) # свій двір
    separate_building = models.BooleanField(default=False)
    # office = models.BooleanField(default=False) # квартира під офіс
    complex = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="complex_objects_commerce",
    )

class House(BaseRealEstate):
    """Приватний будинок"""
    class Meta(BaseRealEstate.Meta):
        permissions = (
            ("add_own_house", "Can add own house"),
            ("change_own_house", "Can change own house"),
            ("view_own_house", "Can view own house"),
            ("view_own_historicalhouse", "Can view own historical house"),
        )

    housing = models.CharField(max_length=50) # корпус
    useful_square = models.PositiveIntegerField() # корисна площа
    land_square = models.PositiveIntegerField() # площа ділянки
    rooms_number = models.PositiveSmallIntegerField()
    communications = models.BooleanField(default=False)
    terrace = models.BooleanField(default=False)
    facade = models.BooleanField(default=False)
    own_parking = models.BooleanField(default=False)
    # attic = models.BooleanField(default=False)
    # gas = models.BooleanField(default=False)


class Selection(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    selected_apartments = models.ManyToManyField(Apartment, blank=True, related_name="related_selected_apartments")
    selected_houses = models.ManyToManyField(House, blank=True, related_name="related_selected_houses" )
    selected_commerces = models.ManyToManyField(Commerce, blank=True, related_name="related_selected_commerces")
