import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _
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
    
    creation_date = models.DateField(verbose_name=_("Creation date"), null=True, blank=True) # дата побудови
    deposit_date = models.DateField(null=True, blank=True, verbose_name=_("Deposit date")) # дата постановки
    # date_before_temporarily_removed = models.DateField(null=True, blank=True)
    # purchase_date = models.DateField(null=True, blank=True)
    # sale_date = models.DateField(null=True, blank=True)
    # date_of_next_call = models.DateField(null=True, blank=True)
    # inspection_form = models.DateTimeField(null=True, blank=True)

    exclusive = models.BooleanField(default=False, verbose_name=_("Exclusive"))
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
        verbose_name=_("Locality")
    )
    # locality_district = models.ForeignKey(
    #     LocalityDistrict,
    #     on_delete=models.CASCADE,
    # )
    street = models.ForeignKey(
        Street,
        on_delete=models.CASCADE,
        verbose_name=_("Street")
    )
    house = models.CharField(max_length=100, verbose_name=_("House"))

    realtor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)ss",
        verbose_name=_("Realtor")
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
        verbose_name=_("Condition"), null=True, blank=True
    )
    material = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="material_%(app_label)s_%(class)ss",
        verbose_name=_("Material"), null=True, blank=True
    )
    agency = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="agency_%(app_label)s_%(class)ss",
        verbose_name=_("Agency")
    )
    house_type = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="house_type_%(app_label)s_%(class)ss",
        verbose_name=_("House type"), null=True, blank=True
    )
    layout = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="layout_%(app_label)s_%(class)ss",
        verbose_name=_("Layout"), null=True, blank=True
    )
    stair = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="stair_%(app_label)s_%(class)ss",
        verbose_name=_("Stair"), null=True, blank=True
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
        verbose_name=_("Owner")
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
    parking = models.BooleanField(default=False, verbose_name=_("Parking"))
    generator = models.BooleanField(default=False, verbose_name=_("Generator"))
    e_home = models.BooleanField(default=False, verbose_name=_("EHome")) # єОселя
    on_delete = models.BooleanField(default=False)

    price = models.IntegerField(verbose_name=_("Price"))
    # site_price = models.IntegerField(null=True, blank=True)
    # square_meter_price = models.IntegerField(null=True, blank=True)
    square = models.IntegerField(verbose_name=_("Square"))
    kitchen_square = models.PositiveIntegerField(verbose_name=_("Kitchen square"))
    height = models.FloatField(verbose_name=_("Height"))
    # owners_number = models.PositiveSmallIntegerField(null=True, blank=True)
    floor = models.PositiveIntegerField(verbose_name=_("Floor"))
    storeys_number = models.PositiveIntegerField(verbose_name=_("Number of storeys"))
    
    status = models.PositiveSmallIntegerField(
        choices=RealEstateStatus.choices,
        verbose_name=_("Status")
    )
    room_types = models.PositiveSmallIntegerField(
        choices=RoomType.choices,
        verbose_name=_("Rubric"),
        default=RoomType.NONE
    )

    document = models.CharField(max_length=150, blank=True, verbose_name=_("Document"))
    # filename_of_exclusive_agreement = models.CharField(max_length=150, null=True, blank=True)
    # inspection_file_name = models.CharField(max_length=150, null=True, blank=True)
    # filename_forbid_sale = models.CharField(max_length=150, null=True, blank=True)
    # reference_point = models.CharField(max_length=150, null=True, blank=True)

    sale_terms = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Sale terms"))
    realtor_notes = models.TextField(null=True, blank=True, verbose_name=_("Realtor notes"))
    comment = models.TextField(verbose_name=_("Comment"), null=True, blank=True)

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

    apartment = models.CharField(max_length=50, verbose_name=_("Apartment"))
    living_square = models.PositiveIntegerField(verbose_name=_("Living square"))
    balcony = models.BooleanField(default=False, verbose_name=_("Balcony"))
    balcony_number = models.PositiveSmallIntegerField(default=0, verbose_name=_("Number of balconies"))
    complex = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="complex_objects_apartment",
        verbose_name=_("Complex")
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

    premises = models.CharField(max_length=50, verbose_name=_("Premises")) # приміщення
    useful_square = models.PositiveIntegerField(verbose_name=_("Useful square"), null=True, blank=True) # корисна площа
    balcony = models.BooleanField(default=False, verbose_name=_("Balcony"))
    balcony_number = models.PositiveSmallIntegerField(default=0, verbose_name=_("Number of balconies"))
    ground_floor = models.BooleanField(default=False, verbose_name=_("Ground floor")) # цоколь
    facade = models.BooleanField(default=False, verbose_name=_("Facade"))
    own_parking = models.BooleanField(default=False, verbose_name=_("Own parking"))
    own_courtyard = models.BooleanField(default=False, verbose_name=_("Own courtyard")) # свій двір
    separate_building = models.BooleanField(default=False, verbose_name=_("Separate building"))
    # office = models.BooleanField(default=False) # квартира під офіс
    complex = models.ForeignKey(
        Handbook, on_delete=models.CASCADE,
        related_name="complex_objects_commerce",
        verbose_name=_("Complex")
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

    housing = models.CharField(max_length=50, verbose_name=_("Housing"), null=True, blank=True) # корпус
    useful_square = models.PositiveIntegerField(verbose_name=_("Useful square"), null=True, blank=True) # корисна площа
    land_square = models.PositiveIntegerField(verbose_name=_("Land's square"), null=True, blank=True) # площа ділянки
    rooms_number = models.PositiveSmallIntegerField(verbose_name=_("Number of rooms"), null=True, blank=True)
    communications = models.BooleanField(default=False, verbose_name=_("Communications"))
    terrace = models.BooleanField(default=False, verbose_name=_("Terrace"))
    facade = models.BooleanField(default=False, verbose_name=_("Facade"))
    own_parking = models.BooleanField(default=False, verbose_name=_("Own parking"))
    # attic = models.BooleanField(default=False)
    # gas = models.BooleanField(default=False)


class Selection(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_("Client")
    )
    date = models.DateField(
        default=datetime.date.today,
        verbose_name=_("Date")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    selected_apartments = models.ManyToManyField(
        Apartment,
        blank=True,
        related_name="related_selected_apartments"
    )
    selected_houses = models.ManyToManyField(
        House,
        blank=True,
        related_name="related_selected_houses"
    )
    selected_commerces = models.ManyToManyField(
        Commerce,
        blank=True,
        related_name="related_selected_commerces"
    )
