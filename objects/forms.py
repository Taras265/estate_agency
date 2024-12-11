from django import forms
from django.forms import inlineformset_factory

# from django.contrib.admin.widgets import AdminSplitDateTime

from accounts.models import CustomUser
from handbooks.models import Region, District, Locality, LocalityDistrict, Street, Handbook, Client
from images.models import ApartmentImage
from objects.models import Apartment
from django.utils.translation import gettext_lazy as _


class ApartmentForm(forms.ModelForm):
    creation_date = forms.DateField(
        label=_("creation_date"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'})
    )
    """
    date_before_temporarily_removed = forms.DateField(
        label=_("date_before_temporarily_removed"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )"""
    deposit_date = forms.DateField(
        label=_("deposit_date"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )
    """purchase_date = forms.DateField(
        label=_("purchase_date"), widget=forms.SelectDateWidget(attrs={'class': ''})
    )
    sale_date = forms.DateField(
        label=_("sale_date"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )
    date_of_next_call = forms.DateField(
        label=_("date_of_next_call"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )
    inspection_form = forms.SplitDateTimeField(
        label=_("inspection_form (2020-03-06, 12:32:38)"),
        widget=forms.SplitDateTimeWidget(attrs={'class': "form-control"}),
        required=False
    )"""
    exclusive = forms.BooleanField(
        label=_("exclusive"),
        widget=forms.CheckboxInput(),
        required=False
    )
    """exclusive_to = forms.DateField(
        label=_("exclusive_to"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )
    exclusive_from = forms.DateField(
        label=_("exclusive_from"),
        widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        required=False
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(on_delete=False),
        label=_("region"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('region')})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.filter(on_delete=False),
        label=_("district"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('district')})
    )"""
    locality = forms.ModelChoiceField(
        queryset=Locality.objects.filter(on_delete=False),
        label=_("locality"),
        widget=forms.Select(attrs={'class': 'form-control','placeholder': _('locality')})
    )
    """locality_district = forms.ModelChoiceField(
        queryset=LocalityDistrict.objects.filter(on_delete=False),
        label=_("locality_district"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('locality_district')})
    )"""
    street = forms.ModelChoiceField(
        queryset=Street.objects.filter(on_delete=False), label=_("street"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('street')}))
    house = forms.CharField(
        label=_("house"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('house')}),
        required=False
    )
    apartment = forms.CharField(
        label=_("apartment"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('apartment')}),
        required=False
    )
    """on_site = forms.BooleanField(
        label=_("on_site"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    """inspection_flag = forms.BooleanField(
        label=_("inspection_flag"),
        widget=forms.CheckboxInput(),
        required=False
    )
    paid_exclusive_flag = forms.BooleanField(
        label=_("paid_exclusive_flag"),
        widget=forms.CheckboxInput(),
        required=False
    )
    terrace_flag = forms.BooleanField(
        label=_("terrace_flag"),
        widget=forms.CheckboxInput(),
        required=False
    )
    sea_flag = forms.BooleanField(
        label=_("sea_flag"),
        widget=forms.CheckboxInput(),
        required=False
    )
    vip = forms.BooleanField(
        label=_("vip"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    """withdrawal_reason = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=1).all(),
        label=_("withdrawal_reason"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('withdrawal_reason')}),
        required=False
    )
    independent = forms.BooleanField(
        label=_("independent"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    condition = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(on_delete=False).filter(type=2).all(),
        label=_("condition"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('condition')})
    )
    """special = forms.BooleanField(
        label=_("special"),
        widget=forms.CheckboxInput(),
        required=False
    )
    urgently = forms.BooleanField(
        label=_("urgently"),
        widget=forms.CheckboxInput(),
        required=False
    )
    trade = forms.BooleanField(
        label=_("trade"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    material = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=3).all(),
        label=_("material"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('material')})
    )
    complex = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False, type=12).all(),
        label=_("complex"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('complex')})
    )
    status = forms.ChoiceField(
        choices=Apartment.STATUS_CHOICES,
        label=_("status"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('status')})
    )
    object_type = forms.ChoiceField(
        choices=Apartment.OBJECT_TYPE_CHOICES,
        label=_("add"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('object_type')})
    )
    square = forms.IntegerField(
        label=_("square"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('square')})
    )
    price = forms.IntegerField(
        label=_("price"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('price')})
    )
    """site_price = forms.IntegerField(
        label=_('site_price'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('site_price')})
    )"""
    """square_meter_price = forms.IntegerField(
        label=_("square_meter_price"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('square_meter_price')})
    )"""
    realtor = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label=_("realtor"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('realtor')})
    )
    """site_realtor1 = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label=_("site_realtor1"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('site_realtor1')})
    )
    site_realtor2 = forms.ModelChoiceField(
        queryset=CustomUser.objects.all().all(),
        label=_("site_realtor2"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('site_realtor2')}),
        required=False
    )
    realtor_5_5 = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label=_("realtor_5_5"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('realtor_5_5')}),
        required=False
    )"""
    """for_trainee = forms.BooleanField(
        label=_("for_trainee"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    realtor_notes = forms.CharField(
        label=_("realtor_notes"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('realtor_notes')}),
        required=False
    )
    """reference_point = forms.CharField(
        label=_("reference_point"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('reference_point')}),
        required=False
    )
    author = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label=_("author"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('author')})
    )"""
    owner = forms.ModelChoiceField(
        queryset=Client.objects.filter(on_delete=False),
        label=_("owner"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('owner')})
    )
    """client = forms.ModelChoiceField(
        queryset=Client.objects.filter(on_delete=False),
        label=_("client"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('client')}),
        required=False
    )
    owners_number = forms.IntegerField(
        label=_("owners_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('owners_number')})
    )"""
    comment = forms.CharField(
        label=_("comment"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('comment')})
    )
    """separation = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=4).all(),
        label=_("separation"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('separation')})
    )"""
    agency = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=5).all(),
        label=_("agency"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('agency')})
    )
    """agency_sales = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=6).all(),
        label=_("agency_sales"),
        widget=forms.Select(attrs={'class': 'form-control','placeholder': _('agency_sales')})
    )"""
    sale_terms = forms.CharField(
        label=_("sale_terms"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('sale_terms')}),
        required=False
    )
    """filename_of_exclusive_agreement = forms.CharField(
        label=_("filename_of_exclusive_agreement"),
        widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': _('filename_of_exclusive_agreement')}),
        required=False
    )
    inspection_file_name = forms.CharField(
        label=_("inspection_file_name"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('inspection_file_name')}),
        required=False
    )"""
    document = forms.CharField(
        label=_("document"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('document')}),
        required=False
    )
    """filename_forbid_sale = forms.CharField(
        label=_("filename_forbid_sale"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('filename_forbid_sale')}),
        required=False
    )
    new_building_name = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=7).all(),
        label=_("new_building_name"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('new_building_name')}),
        required=False
    )
    new_building = forms.BooleanField(
        label=_("new_building"),
        widget=forms.CheckboxInput(),
        required=False
    )
    new_building_type = forms.ChoiceField(
        choices=Apartment.NEW_BUILDING_TYPE_CHOICES,
        label=_("new_building_type"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('new_building_type')}),
        required=False
    )
    rooms_number = forms.IntegerField(
        label=_("rooms_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('rooms_number')})
    )"""
    room_types = forms.ChoiceField(
        choices=Apartment.ROOM_TYPE_CHOICES,
        label=_("rubric"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('room_types')})
    )
    height = forms.FloatField(
        label=_("height"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('height')})
    )
    kitchen_square = forms.IntegerField(
        label=_("kitchen_square"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('kitchen_square')})
    )
    living_square = forms.IntegerField(
        label=_("living_square"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('living_square')})
    )
    """gas = forms.BooleanField(
        label=_("gas"),
        widget=forms.CheckboxInput(),
        required=False
    )
    courtyard = forms.BooleanField(
        label=_("courtyard"),
        widget=forms.CheckboxInput(),
        required=False
    )
    balcony_number = forms.IntegerField(
        label=_("balcony_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('balcony_number')}),
        required=False
    )
    registered_number = forms.IntegerField(
        label=_("registered_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('registered_number')}),
        required=False
    )
    child_registered_number = forms.IntegerField(
        label=_("child_registered_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('child_registered_number')}),
        required=False
    )
    loggias_number = forms.IntegerField(
        label=_("loggias_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('loggias_number')}),
        required=False
    )
    bay_windows_number = forms.IntegerField(
        label=_("bay_windows_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('bay_windows_number')}),
        required=False
    )"""
    """commune = forms.BooleanField(label=_("commune"), widget=forms.CheckboxInput(), required=False)
    frame = forms.CharField(
        label=_("frame"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('frame')})
    )"""
    stair = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=8).all(),
        label=_("stair"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('stair')})
    )
    balcony = forms.BooleanField(label=_("balcony"), widget=forms.CheckboxInput(), required=False)
    """heating = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=9).all(),
        label=_("heating"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('heating')})
    )
    office = forms.BooleanField(label=_("office"), widget=forms.CheckboxInput(), required=False)
    penthouse = forms.BooleanField(label=_("penthouse"), widget=forms.CheckboxInput(), required=False)"""
    parking = forms.BooleanField(label=_("parking"), widget=forms.CheckboxInput(), required=False)
    generator = forms.BooleanField(label=_("generator"), widget=forms.CheckboxInput(), required=False)
    e_home = forms.BooleanField(label=_("EHome"), widget=forms.CheckboxInput(), required=False)
    """redevelopment = forms.ChoiceField(
        choices=Apartment.REDEVELOPMENT_CHOICES,
        label=_("redevelopment"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('redevelopment')})
    )"""
    layout = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=10).all(),
        label=_("layout"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('layout')})
    )
    """construction_number = forms.CharField(
        label=_("construction_number"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('construction_number')})
    )"""
    house_type = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=11).all(),
        label=_("house_type"),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': _('house_type')})
    )
    """two_level_apartment = forms.BooleanField(
        label=_("two_level_apartment"),
        widget=forms.CheckboxInput(),
        required=False
    )
    loggia = forms.IntegerField(
        label=_("loggia"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('loggia')}),
        required=False
    )
    attic = forms.BooleanField(
        label=_("attic"),
        widget=forms.CheckboxInput(),
        required=False
    )
    electric_stove = forms.BooleanField(
        label=_("electric_stove"),
        widget=forms.CheckboxInput(),
        required=False
    )"""
    floor = forms.IntegerField(
        label=_("floor"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('floor')})
    )
    storeys_number = forms.IntegerField(
        label=_("storeys_number"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('storeys_number')}),
        required=False
    )

    class Meta:
        model = Apartment
        fields = ('object_type', 'room_types', 'realtor', 'deposit_date',
                  'status', 'locality', 'street',
                  'house', 'apartment', 'agency', 'square', 'living_square',
                  'kitchen_square', 'height', 'price', 'exclusive',
                  'e_home', 'document', 'house_type', 'material',
                  'complex', 'condition', 'floor', 'layout',
                  'balcony', 'stair', 'storeys_number', 'parking',
                  'generator', 'creation_date', 'realtor_notes',
                  'sale_terms', 'owner', 'comment')
        # exclude = ('on_delete',)


ApartmentImageFormSet = inlineformset_factory(
    Apartment,
    ApartmentImage,
    form=forms.ModelForm,
    fields=['image', ],
    extra=1,
    can_delete=True
)


class SearchForm(forms.Form):
    locality = forms.CharField(label=_("locality"), required=False,
                               widget=forms.TextInput(attrs={'class': 'customtxt',
                                                             "placeholder": _("locality")}))
    street = forms.CharField(label=_("street"), required=False,
                             widget=forms.TextInput(attrs={'class': 'customtxt',
                                                           "placeholder": _("street")}))
    price_min = forms.IntegerField(label=_("price_min"),
                                   widget=forms.NumberInput(attrs={'class': 'customtxt',
                                                                   "placeholder": _("price_min")}),
                                   required=False)
    price_max = forms.IntegerField(label=_("price_max"),
                                   widget=forms.NumberInput(attrs={'class': 'customtxt',
                                                                   "placeholder": _("price_max")}),
                                   required=False)


class HandbooksSearchForm(forms.Form):
    id = forms.IntegerField(label=_("id"),
                            widget=forms.NumberInput(attrs={'class': 'customtxt',
                                                            "placeholder": _("id")}),
                            required=False)
    exclusive = forms.BooleanField(label=_("exclusive"), widget=forms.CheckboxInput(),
                                   required=False)
