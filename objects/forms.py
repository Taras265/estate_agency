from django import forms
from django.utils.translation import gettext_lazy as _

from handbooks.models import Handbook
from objects.models import Apartment, Commerce, House


class BaseRealEstateForm(forms.ModelForm):
    """
    Базова форма для створення або редагування обʼєкту нерухомості.
    Дана форма містить лише спільні для всіх типів обʼєктів поля,
    які потрібно перевизначити (наприклад, передати кастомний queryset).
    """
    agency = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=5, on_delete=False),
    )
    house_type = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=11, on_delete=False),
    )
    material = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=3, on_delete=False),
    )
    condition = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=2, on_delete=False),
    )
    layout = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=10, on_delete=False),
    )
    stair = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=8, on_delete=False),
    )


class ApartmentForm(BaseRealEstateForm):
    """Форма для створення або редагування квартири."""
    template_name = "objects/_apartment_form.html"

    complex = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(type=12, on_delete=False),
    )

    class Meta:
        model = Apartment
        fields = (
            "room_types", "realtor", "deposit_date", "status",
            "locality", "street", "house", "apartment", "agency",
            "square", "living_square", "kitchen_square", "height",
            "price", "exclusive", "e_home", "document",
            "house_type", "material", "complex", "condition",
            "floor", "layout", "balcony", "stair",
            "storeys_number", "parking", "generator", "creation_date",
            "realtor_notes", "sale_terms", "owner", "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
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
            "realtor_notes": forms.Textarea(attrs={"class": "form-control"}),
            "sale_terms": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control"}),
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
            "room_types", "realtor", "deposit_date", "status",
            "locality", "street", "house", "premises", "agency",
            "square", "useful_square", "kitchen_square", "height",
            "price", "exclusive", "e_home", "document",
            "house_type", "material", "complex", "condition",
            "floor", "layout", "balcony", "stair",
            "storeys_number", "parking", "generator", "creation_date",
            "ground_floor", "facade", "own_parking", "separate_building",
            "own_courtyard",
            "realtor_notes", "sale_terms", "owner", "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
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
            "room_types", "realtor", "deposit_date", "status",
            "locality", "street", "house", "housing", "agency",
            "square", "useful_square", "kitchen_square", "height",
            "land_square", "rooms_number", "communications",
            "price", "exclusive", "e_home", "document",
            "house_type", "material", "condition",
            "floor", "layout", "terrace", "stair",
            "storeys_number", "parking", "generator", "creation_date",
            "facade", "own_parking",
            "realtor_notes", "sale_terms", "owner", "comment",
        )
        widgets = {
            "deposit_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
            "creation_date": forms.SelectDateWidget(attrs={"class": "form-control"}),
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


class SearchForm(forms.Form):
    locality = forms.CharField(
        label=_("Locality"),
        required=False,
        widget=forms.TextInput(attrs={"class": "customtxt", "placeholder": _("Locality")})
    )
    street = forms.CharField(
        label=_("Street"),
        required=False,
        widget=forms.TextInput(attrs={"class": "customtxt", "placeholder": _("Street")})
    )
    price_min = forms.IntegerField(
        label=_("Min price"),
        widget=forms.NumberInput(attrs={"class": "customtxt", "placeholder": _("Min price")}),
        required=False
    )
    price_max = forms.IntegerField(
        label=_("Max price"),
        widget=forms.NumberInput(attrs={"class": "customtxt", "placeholder": _("Max price")}),
        required=False
    )


class HandbooksSearchForm(forms.Form):
    id = forms.IntegerField(
        label=_("Id"),
        widget=forms.NumberInput(attrs={"class": "customtxt",}),
        required=False
    )
    exclusive = forms.BooleanField(
        label=_("Exclusive"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )
    in_selection = forms.BooleanField(
        label=_("In selection"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
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
    house = forms.CharField(
        error_messages={"required": _("You did not specify a house")}
    )


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
