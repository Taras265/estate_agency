from django import forms
from django.core.validators import RegexValidator
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from .models import (
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
from handbooks.choices import (
    CenterType,
    CityType,
    NewBuildingDistrictType,
)


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
        label=_("Phone number"),
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
        label=_("Open date date"),
        widget=forms.DateInput(attrs={"type": "date", "class": "customtxt"})
    )
    open_date_time = forms.TimeField(
        label=_("Open date time"),
        widget=forms.TimeInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.open_date:
            self.fields["open_date_date"].initial = self.instance.open_date.date().strftime("%Y-%m-%d")
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
