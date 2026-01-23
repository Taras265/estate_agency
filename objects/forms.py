from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from handbooks.models import Handbook, FilialAgency, LocalityDistrict, Street
from objects.models import Apartment, Commerce, House, Land
from objects.choices import (
    RealEstateStatus,
    ApartmentRubric,
    CommerceRubric,
    HouseRubric,
    LandRubric
)


class BaseRealEstateForm(forms.ModelForm):
    """
    Базова форма для створення або редагування обʼєкту нерухомості.
    Дана форма містить лише спільні для всіх типів обʼєктів поля,
    які потрібно перевизначити (наприклад, передати кастомний queryset).
    """

    agency = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=5, on_delete=False),
    )
    filial = forms.ModelChoiceField(
        queryset=FilialAgency.objects.none(),
    )
    house_type = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=11, on_delete=False),
        required=False,
    )
    material = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=3, on_delete=False),
        required=False,
    )
    condition = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=2, on_delete=False),
        required=False,
    )
    layout = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=10, on_delete=False),
        required=False,
    )
    stair = forms.ModelChoiceField(
        required=False,
        queryset=Handbook.objects.filter(type=8, on_delete=False),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["realtor"].initial = user
            self.fields["filial"].queryset = self.fields["realtor"].initial.filials.all()

        if (realtor_id := self.data.get("realtor")):
            if isinstance(realtor_id, CustomUser):
                self.fields["filial"].queryset = realtor_id.filials.all()
            else:
                self.fields["filial"].queryset = CustomUser.objects.get(id=realtor_id).filials.all()
        elif hasattr(self.instance, "realtor"):
            self.fields["filial"].queryset = self.instance.realtor.filials.all()

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False

        cleaned_data = super().clean()
        realtor = cleaned_data.get("realtor")
        filial = cleaned_data.get("filial")

        if filial not in realtor.filials.all():
            self.add_error("filial", "Realtor doesn't have filial " + filial)
            return False
        return True


class ApartmentForm(BaseRealEstateForm):
    """Форма для створення або редагування квартири."""

    template_name = "objects/_apartment_form.html"

    complex = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=12, on_delete=False),
    )

    class Meta:
        model = Apartment
        fields = (
            "rubric",
            "realtor",
            "deposit_date",
            "status",
            "locality",
            "street",
            "house",
            "apartment",
            "agency",
            "filial",
            "square",
            "living_square",
            "kitchen_square",
            "height",
            "price",
            "exclusive",
            "e_home",
            "document",
            "house_type",
            "material",
            "complex",
            "condition",
            "floor",
            "layout",
            "balcony",
            "stair",
            "storeys_number",
            "parking",
            "generator",
            "creation_date",
            "realtor_notes",
            "sale_terms",
            "owner",
            "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "locality": forms.Select(attrs={"data-live-search": "true"}),
            "street": forms.Select(attrs={"data-live-search": "true"}),
            "house": forms.TextInput(attrs={"class": "form-control"}),
            "apartment": forms.TextInput(attrs={"class": "form-control"}),
            "square": forms.TextInput(attrs={"class": "form-control"}),
            "living_square": forms.TextInput(attrs={"class": "form-control"}),
            "kitchen_square": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.TextInput(attrs={"class": "form-control"}),
            "document": forms.TextInput(attrs={"class": "form-control"}),
            "floor": forms.TextInput(attrs={"class": "form-control"}),
            "storeys_number": forms.TextInput(attrs={"class": "form-control"}),
            "realtor_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "sale_terms": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class CommerceForm(BaseRealEstateForm):
    """Форма для створення або редагування комерції."""

    template_name = "objects/_commerce_form.html"

    complex = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=12, on_delete=False),
    )

    class Meta:
        model = Commerce
        fields = (
            "rubric",
            "realtor",
            "deposit_date",
            "status",
            "locality",
            "street",
            "house",
            "premises",
            "agency",
            "filial",
            "square",
            "useful_square",
            "kitchen_square",
            "height",
            "price",
            "exclusive",
            "e_home",
            "document",
            "house_type",
            "material",
            "complex",
            "condition",
            "floor",
            "layout",
            "balcony",
            "stair",
            "storeys_number",
            "parking",
            "generator",
            "creation_date",
            "ground_floor",
            "facade",
            "own_parking",
            "separate_building",
            "own_courtyard",
            "realtor_notes",
            "sale_terms",
            "owner",
            "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "locality": forms.Select(attrs={"data-live-search": "true"}),
            "street": forms.Select(attrs={"data-live-search": "true"}),
            "house": forms.TextInput(attrs={"class": "form-control"}),
            "premises": forms.TextInput(attrs={"class": "form-control"}),
            "square": forms.TextInput(attrs={"class": "form-control"}),
            "useful_square": forms.TextInput(attrs={"class": "form-control"}),
            "kitchen_square": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.TextInput(attrs={"class": "form-control"}),
            "document": forms.TextInput(attrs={"class": "form-control"}),
            "floor": forms.TextInput(attrs={"class": "form-control"}),
            "storeys_number": forms.TextInput(attrs={"class": "form-control"}),
            "realtor_notes": forms.Textarea(attrs={"class": "form-control"}),
            "sale_terms": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control"}),
        }


class HouseForm(BaseRealEstateForm):
    """Форма для створення або редагування будинку."""

    template_name = "objects/_house_form.html"

    class Meta:
        model = House
        fields = (
            "rubric",
            "realtor",
            "deposit_date",
            "status",
            "locality",
            "street",
            "house",
            "housing",
            "agency",
            "filial",
            "square",
            "useful_square",
            "kitchen_square",
            "height",
            "land_square",
            "rooms_number",
            "communications",
            "price",
            "exclusive",
            "e_home",
            "document",
            "house_type",
            "material",
            "condition",
            "floor",
            "layout",
            "terrace",
            "stair",
            "storeys_number",
            "parking",
            "generator",
            "creation_date",
            "facade",
            "own_parking",
            "realtor_notes",
            "sale_terms",
            "owner",
            "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "locality": forms.Select(attrs={"data-live-search": "true"}),
            "street": forms.Select(attrs={"data-live-search": "true"}),
            "house": forms.TextInput(attrs={"class": "form-control"}),
            "housing": forms.TextInput(attrs={"class": "form-control"}),
            "square": forms.TextInput(attrs={"class": "form-control"}),
            "useful_square": forms.TextInput(attrs={"class": "form-control"}),
            "kitchen_square": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.TextInput(attrs={"class": "form-control"}),
            "land_square": forms.TextInput(attrs={"class": "form-control"}),
            "rooms_number": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.TextInput(attrs={"class": "form-control"}),
            "document": forms.TextInput(attrs={"class": "form-control"}),
            "floor": forms.TextInput(attrs={"class": "form-control"}),
            "storeys_number": forms.TextInput(attrs={"class": "form-control"}),
            "realtor_notes": forms.Textarea(attrs={"class": "form-control"}),
            "sale_terms": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control"}),
        }


class LandForm(BaseRealEstateForm):
    """Форма для створення або редагування будинку."""

    template_name = "objects/_land_form.html"

    class Meta:
        model = Land
        fields = (
                "creation_date",
                "deposit_date",
                "exclusive",
                "locality",
                "street",
                "house",
                "realtor",
                "condition",
                "material",
                "agency",
                "filial",
                "house_type",
                "layout",
                "stair",

                "owner",
                "parking",
                "generator",
                "e_home",
                "price",
                "status",
                "rubric",
                "document",
                "sale_terms",
                "realtor_notes",
                "comment",
                "in_selection",
                "housing",
                "land_square",
                "communications" ,
                "target",
                "disposition",
                "own_parking",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "locality": forms.Select(attrs={"data-live-search": "true"}),
            "street": forms.Select(attrs={"data-live-search": "true"}),
            "house": forms.TextInput(attrs={"class": "form-control"}),
            "housing": forms.TextInput(attrs={"class": "form-control"}),
            "useful_square": forms.TextInput(attrs={"class": "form-control"}),
            "land_square": forms.TextInput(attrs={"class": "form-control"}),
            "rooms_number": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.TextInput(attrs={"class": "form-control"}),
            "document": forms.TextInput(attrs={"class": "form-control"}),
            "realtor_notes": forms.Textarea(attrs={"class": "form-control"}),
            "sale_terms": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control"}),
        }


class SearchForm(forms.Form):
    locality = forms.CharField(
        label=_("Locality"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": "customtxt", "placeholder": _("Locality")}
        ),
    )
    street = forms.CharField(
        label=_("Street"),
        required=False,
        widget=forms.TextInput(attrs={"class": "customtxt", "placeholder": _("Street")}),
    )
    price_min = forms.IntegerField(
        label=_("Min price"),
        widget=forms.NumberInput(
            attrs={"class": "customtxt", "placeholder": _("Min price")}
        ),
        required=False,
    )
    price_max = forms.IntegerField(
        label=_("Max price"),
        widget=forms.NumberInput(
            attrs={"class": "customtxt", "placeholder": _("Max price")}
        ),
        required=False,
    )


class RealEstateSearchForm(forms.Form):
    class Meta:
        widgets = {
            "locality_district": forms.Select(attrs={"data-live-search": "true"}),
            "street": forms.Select(attrs={"data-live-search": "true"}),
        }

    YES_NO_CHOICES = (
        (True, _("Yes")),
        (False, _("No"))
    )

    def str_to_bool(val: str) -> bool:
        if val == "True":
            return True
        if val == "False":
            return False
        return None

    id = forms.IntegerField(
        label=_("Id"),
        widget=forms.NumberInput(attrs={"class": "customtxt"}),
        required=False,
    )
    locality_district = forms.ModelMultipleChoiceField(
        label=_("Locality District"),
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        required=False,
        widget=forms.SelectMultiple(attrs={
            "data-live-search": "true"
        })
    )
    street = forms.ModelMultipleChoiceField(
        label=_("Street"),
        queryset=Street.objects.filter(on_delete=False),
        required=False,
        widget=forms.SelectMultiple(attrs={
            "data-live-search": "true"
        })
    )
    status = forms.TypedMultipleChoiceField(
        coerce=int,
        label=_("Status"),
        choices=RealEstateStatus.choices,
        initial=RealEstateStatus.ON_SALE,
        required=False
    )
    exclusive = forms.TypedMultipleChoiceField(
        coerce=str_to_bool,
        label=_("Exclusive"),
        choices=YES_NO_CHOICES,
        required=False,
    )
    in_selection = forms.TypedMultipleChoiceField(
        coerce=str_to_bool,
        label=_("In selection"),
        choices=YES_NO_CHOICES,
        required=False,
    )
    price_min = forms.IntegerField(
        label=_("Min price"),
        widget=forms.NumberInput(attrs={"class": "customtxt"}),
        min_value=0,
        required=False,
    )
    price_max = forms.IntegerField(
        label=_("Max price"),
        widget=forms.NumberInput(attrs={"class": "customtxt"}),
        min_value=0,
        required=False,
    )
    whose_objects = forms.ChoiceField(
        choices=(("own", _("My objects")), ("all", _("All objects"))),
        initial="own",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        price_min = cleaned_data.get("price_min")
        price_max = cleaned_data.get("price_max")
        if price_min and price_max and price_min > price_max:
            print("MIN > MAX")
            raise ValidationError(
                _("Min price must be less than or equal to the max price"),
                code="invalid"
            )


class ApartmentSearchForm(RealEstateSearchForm):
    rubric = forms.TypedMultipleChoiceField(
        coerce=int,
        label=_("Rubric"),
        choices=ApartmentRubric,
        required=False
    )


class CommerceSearchForm(RealEstateSearchForm):
    rubric = forms.TypedMultipleChoiceField(
        coerce=int,
        label=_("Rubric"),
        choices=CommerceRubric,
        required=False
    )


class HouseSearchForm(RealEstateSearchForm):
    rubric = forms.TypedMultipleChoiceField(
        coerce=int,
        label=_("Rubric"),
        choices=HouseRubric,
        required=False
    )


class LandSearchForm(RealEstateSearchForm):
    rubric = forms.TypedMultipleChoiceField(
        coerce=int,
        label=_("Rubric"),
        choices=LandRubric,
        required=False
    )


class BaseVerifyAddressForm(forms.Form):
    """
    Базова форма для перевірки чи існує обʼєкт нерухомості
    за вказаною адресою. Дана форма містить лише спільні
    для всіх типів обʼєктів поля.
    """

    locality = forms.IntegerField(
        error_messages={"required": _("You did not specify a locality")}
    )
    street = forms.IntegerField(
        error_messages={"required": _("You did not specify a street")}
    )
    house = forms.CharField(error_messages={"required": _("You did not specify a house")})


class ApartmentVerifyAddressForm(BaseVerifyAddressForm):
    """Форма для перевірки чи існує квартира за вказаною адресою."""

    apartment = forms.CharField(
        error_messages={"required": _("You did not specify an apartment")}
    )


class CommerceVerifyAddressForm(BaseVerifyAddressForm):
    """Форма для перевірки чи існує комерція за вказаною адресою."""

    premises = forms.CharField(
        error_messages={"required": _("You did not specify a premises")}
    )


class HouseVerifyAddressForm(BaseVerifyAddressForm):
    """Форма для перевірки чи існує будинок за вказаною адресою."""

    housing = forms.CharField(
        error_messages={"required": _("You did not specify a housing")}
    )
