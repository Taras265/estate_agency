from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from .models import Client
from handbooks.models import (
    Locality,
    LocalityDistrict,
    Street,
    Handbook
)
from .choices import (
    ClientStatusType,
    IncomeSourceType
)
from objects.choices import RealEstateType
from handbooks.choices import RealtorType


class ClientForm(forms.ModelForm):
    email = forms.CharField(
        label=_("Email"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label=_("Last name"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        label=_("Phone number"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    messenger = forms.CharField(
        required=False,
        label=_("Messenger"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    telegram = forms.BooleanField(
        label=_("Telegram"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )
    viber = forms.BooleanField(
        label=_("Viber"),
        widget=forms.CheckboxInput(),
        required=False,
        initial=False
    )
    income_source = forms.ChoiceField(
        choices=IncomeSourceType.choices,
        label=_("Income source"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    object_type = forms.ChoiceField(
        choices=RealEstateType.choices,
        label=_("Real estate type"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    realtor_type = forms.ChoiceField(
        choices=RealtorType.choices,
        label=_("Realtor type"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    realtor = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label=_("Realtor"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        choices=ClientStatusType.choices,
        label=_("Status"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    rooms_number = forms.IntegerField(
        label=_("Rooms number"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    locality = forms.ModelMultipleChoiceField(
        queryset=Locality.objects.filter(on_delete=False),
        label=_("Locality"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={"class": "form-control", "data-live-search": "true"}
        ),
    )
    locality_district = forms.ModelMultipleChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={"class": "form-control", "data-live-search": "true"}
        ),
    )
    street = forms.ModelMultipleChoiceField(
        queryset=Street.objects.filter(on_delete=False),
        label=_("Street"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={"class": "form-control", "data-live-search": "true"}
        ),
    )
    house = forms.CharField(
        label=_("House"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    floor_min = forms.IntegerField(
        label=_("Min floor"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    floor_max = forms.IntegerField(
        label=_("Max floor"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    not_first = forms.BooleanField(
        label=_("Not first"),
        widget=forms.CheckboxInput(attrs={"class": ""}),
        required=False,
    )
    not_last = forms.BooleanField(
        label=_("Not last"),
        widget=forms.CheckboxInput(attrs={"class": ""}),
        required=False,
    )
    price_from = forms.IntegerField(
        label=_("Price from"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_to = forms.IntegerField(
        label=_("Price to"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    square_meter_price_max = forms.IntegerField(
        label=_("Square meter max price"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    condition = forms.ModelMultipleChoiceField(
        queryset=Handbook.objects.filter(on_delete=False, type=2),
        required=False,
        label=_("Condition"),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["realtor"].initial = user

        if self.instance and self.instance.pk and self.instance.locality.exists():
            self.fields["locality_district"].queryset = LocalityDistrict.objects.filter(
                locality__in=self.instance.locality.all()
            )
            self.fields["street"].queryset = Street.objects.filter(
                locality_district__in=self.fields["locality_district"].queryset
            )
        if self.instance and self.instance.pk and self.instance.locality_district.exists():
            self.fields["street"].queryset = Street.objects.filter(
                locality_district__in=self.instance.locality_district.all()
            )

    class Meta:
        model = Client
        exclude = ("date_of_add", "on_delete")


class SelectionForm(forms.Form):
    key_word = forms.CharField(
        label=_("Key word"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    rooms_number = forms.IntegerField(
        label=_("Rooms number"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    locality = forms.ModelMultipleChoiceField(
        queryset=Locality.objects.filter(on_delete=False),
        label=_("Locality"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control", "data-live-search": "true"}),
    )
    locality_district = forms.ModelMultipleChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control", "data-live-search": "true"}),
    )
    street = forms.ModelMultipleChoiceField(
        queryset=Street.objects.filter(on_delete=False),
        label=_("Street"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control", "data-live-search": "true"}),
    )
    house = forms.CharField(
        label=_("House"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    floor_min = forms.IntegerField(
        label=_("Min floor"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    floor_max = forms.IntegerField(
        label=_("Max floor"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    not_first = forms.BooleanField(
        label=_("Not first"), widget=forms.CheckboxInput(), required=False
    )
    not_last = forms.BooleanField(
        label=_("Not last"), widget=forms.CheckboxInput(), required=False
    )
    price_from = forms.IntegerField(
        label=_("Price from"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_to = forms.IntegerField(
        label=_("Price to"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    square_meter_price_max = forms.IntegerField(
        label=_("Square meter max price"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    condition = forms.ModelMultipleChoiceField(
        queryset=Handbook.objects.filter(on_delete=False, type=2),
        required=False,
        label=_("Condition"),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    object_type = forms.ChoiceField(
        choices=RealEstateType.choices,
        label=_("Real estate type"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "locality" in self.data:
            locality_ids = self.data.get("locality")
            self.fields["locality_district"].queryset = LocalityDistrict.objects.filter(
                locality_id__in=locality_ids
            )
        elif "locality" in self.initial:
            locality_ids = self.initial.get("locality", [])
            self.fields["locality_district"].queryset = LocalityDistrict.objects.filter(
                locality_id__in=locality_ids
            )

            # ----- для улиц -----
        if "locality_district" in self.data:
            district_ids = self.data.get("locality_district")
            self.fields["street"].queryset = Street.objects.filter(
                locality_district_id__in=district_ids
            )
        elif "locality_district" in self.initial:
            district_ids = self.initial.get("locality_district", [])
            self.fields["street"].queryset = Street.objects.filter(
                locality_district_id__in=district_ids
            )
