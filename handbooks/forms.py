from django import forms
from django.core.validators import RegexValidator
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from handbooks.choices import (
    CenterType,
    CityType,
    ClientStatusType,
    IncomeSourceType,
    NewBuildingDistrictType,
    RealtorType,
)
from handbooks.models import (
    Client,
    District,
    FilialAgency,
    FilialReport,
    Handbook,
    Locality,
    LocalityDistrict,
    PhoneNumber,
    Region,
    Street,
)
from objects.choices import RealEstateType


class RegionForm(forms.ModelForm):
    region = forms.CharField(
        label=_("Region"), widget=forms.TextInput(attrs={"class": "customtxt"})
    )

    class Meta:
        model = Region
        exclude = ("on_delete",)


class DistrictForm(forms.ModelForm):
    district = forms.CharField(
        label=_("District"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(on_delete=False),
        label=_("Region"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = District
        exclude = ("on_delete",)


class LocalityForm(forms.ModelForm):
    locality = forms.CharField(
        label=_("Locality"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.filter(on_delete=False),
        label=_("District"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    city_type = forms.ChoiceField(
        choices=CityType.choices,
        label=_("City type"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    center_type = forms.ChoiceField(
        choices=CenterType.choices,
        label=_("Center type"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = Locality
        exclude = ("on_delete",)


class LocalityDistrictForm(forms.ModelForm):
    district = forms.CharField(
        label=_("District"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    locality = forms.ModelChoiceField(
        queryset=Locality.objects.filter(on_delete=False),
        label=_("Locality"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    group_on_site = forms.CharField(
        required=False,
        label=_("Group on site"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    hot_deals_limit = forms.FloatField(
        label=_("Hot deals limit"),
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
    )
    prefix_to_site = forms.CharField(
        label=_("prefix_to_site"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    is_subdistrict = forms.BooleanField(
        label=_("Is subdistrict"),
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
        required=False,
    )
    new_building_district = forms.ChoiceField(
        choices=NewBuildingDistrictType.choices,
        label=_("New building district"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = LocalityDistrict
        exclude = ("on_delete",)


class StreetForm(forms.ModelForm):
    street = forms.CharField(
        label=_("Street"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    locality = forms.ModelChoiceField(
        queryset=Locality.objects.filter(on_delete=False),
        label=_("Locality"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    locality_district = forms.ModelChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Street
        exclude = ("on_delete",)


class ClientForm(forms.ModelForm):
    email = forms.CharField(
        label=_("Email"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label=_("First name"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label=_("Last name"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        label=_("Phone number"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    messenger = forms.CharField(
        required=False,
        label=_("Messenger"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    telegram = forms.BooleanField(
        label=_("Telegram"), widget=forms.CheckboxInput(), required=False, initial=False
    )
    viber = forms.BooleanField(
        label=_("Viber"), widget=forms.CheckboxInput(), required=False, initial=False
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
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    locality_district = forms.ModelMultipleChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    street = forms.ModelMultipleChoiceField(
        queryset=Street.objects.filter(on_delete=False),
        label=_("Street"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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
        queryset=Handbook.objects.filter(on_delete=False).filter(type=2).all(),
        required=False,
        label=_("Condition"),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["realtor"].initial = user

    class Meta:
        model = Client
        exclude = ("date_of_add", "on_delete")


class HandbookForm(forms.ModelForm):
    handbook = forms.CharField(
        label=_("Handbook"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    type = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Handbook
        exclude = ("on_delete",)


class FilialForm(forms.ModelForm):
    filial_agency = forms.CharField(
        label=_("Filial agency"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    locality_district = forms.ModelChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        label=_("Filial agency"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    address = forms.CharField(
        label=_("Address"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    type = forms.CharField(
        label=_("Type"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    new_build_area = forms.CharField(
        label=_("New build area"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    open_date_date = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=("Год", "Месяц", "День"), years=range(1900, 2100)
        ),
    )
    open_date_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.open_date:
            self.fields["open_date_date"].initial = self.instance.open_date.date()
            self.fields["open_date_time"].initial = self.instance.open_date.time()

    def save(self, commit=True):
        instance = super().save(commit=False)
        date = self.cleaned_data.get("open_date_date")
        time = self.cleaned_data.get("open_date_time")
        if date and time:
            from datetime import datetime

            instance.open_date = datetime.combine(date, time)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = FilialAgency
        exclude = (
            "open_date",
            "on_delete",
        )


class FilialReportForm(forms.ModelForm):
    report = forms.CharField(
        label=_("Report"), widget=forms.TextInput(attrs={"class": "form-control"})
    )
    filial_agency = forms.ModelChoiceField(
        queryset=FilialAgency.objects.filter(on_delete=False),
        label=_("Filial agency"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = FilialReport
        exclude = ("on_delete",)


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
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    locality_district = forms.ModelMultipleChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("Locality district"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    street = forms.ModelMultipleChoiceField(
        queryset=Street.objects.filter(on_delete=False),
        label=_("Street"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
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
        queryset=Handbook.objects.filter(on_delete=False).filter(type=2).all(),
        required=False,
        label=_("Condition"),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    object_type = forms.ChoiceField(
        choices=RealEstateType.choices,
        label=_("Real estate type"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class IdSearchForm(forms.Form):
    id = forms.IntegerField(
        label=_("Id"),
        widget=forms.NumberInput(attrs={"class": "customtxt"}),
        required=False,
    )


class PhoneNumberForm(forms.ModelForm):
    number = forms.CharField(
        label=_("Phone number"),
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control mb-2"}),
        validators=[
            RegexValidator(
                regex=r"^\+?\d{9,15}$",
                message=_("Phone number must contain 9 to 15 digits without spaces."),
            )
        ],
    )

    class Meta:
        model = PhoneNumber
        fields = ("number",)


PhoneNumberFormSet = inlineformset_factory(
    CustomUser,
    PhoneNumber,
    PhoneNumberForm,
    fields=["number"],
    extra=1,
)
