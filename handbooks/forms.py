from django import forms

from accounts.models import CustomUser
from handbooks.models import Region, District, Locality, LocalityDistrict, FilialAgency, Street, Client, Handbook, \
    FilialReport
from django.utils.translation import gettext_lazy as _


class RegionForm(forms.ModelForm):
    region = forms.CharField(label=_('region'), widget=forms.TextInput(attrs={'class': 'customtxt',
                                                                              'placeholder': _("region")}))

    class Meta:
        model = Region
        exclude = ('on_delete',)


class DistrictForm(forms.ModelForm):
    district = forms.CharField(label=_('district'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                  'placeholder': _("district")}))
    region = forms.ModelChoiceField(queryset=Region.objects.filter(on_delete=False), label=_('region'),
                                    widget=forms.Select(attrs={'class': 'form-control',
                                                               'placeholder': _('region')}))

    class Meta:
        model = District
        exclude = ('on_delete',)


class LocalityForm(forms.ModelForm):
    locality = forms.CharField(label=_('locality'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                  'placeholder': _("locality")}))
    district = forms.ModelChoiceField(queryset=District.objects.filter(on_delete=False), label=_('district'),
                                      widget=forms.Select(attrs={'class': 'form-control',
                                                                 'placeholder': _('district')}))
    city_type = forms.ChoiceField(choices=((1, "село"), (2, "смт"), (3, "місто")), label=_('city_type'),
                                  widget=forms.Select(attrs={'class': 'form-control',
                                                             'placeholder': _('city_type')}))
    center_type = forms.ChoiceField(choices=((1, "районий"), (2, "обласний"), (3, "")),
                                    label=_('center_type'),
                                    widget=forms.Select(attrs={'class': 'form-control',
                                                               'placeholder': _('center_type')}), required=False)

    class Meta:
        model = Locality
        exclude = ('on_delete',)


class LocalityDistrictForm(forms.ModelForm):
    district = forms.CharField(label=_('district'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                  'placeholder': _("district")}))
    locality = forms.ModelChoiceField(queryset=Locality.objects.filter(on_delete=False), label=_('locality'),
                                      widget=forms.Select(attrs={'class': 'form-control',
                                                                 'placeholder': _('locality')}))
    description = forms.CharField(label=_("description"), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                        'placeholder': _(
                                                                                            'description')}),
                                  required=False)
    group_on_site = forms.CharField(label=_('group_on_site'), required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control',
                                                                  'placeholder': _("group_on_site")}))
    hot_deals_limit = forms.FloatField(label=_("hot_deals_limit"),
                                       widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                       'placeholder': _("hot_deals_limit")}),
                                       required=False)
    prefix_to_site = forms.CharField(label=_('prefix_to_site'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                              'placeholder': _(
                                                                                                  "prefix_to_site")}))
    is_subdistrict = forms.BooleanField(label=_('is_subdistrict'),
                                        widget=forms.CheckboxInput(attrs={'class': 'form-control',
                                                                          'placeholder': _("is_subdistrict")}),
                                        required=False)
    new_building_district = forms.ChoiceField(choices=((1, "Приморский+Центр"), (2, "Киевский+Малиновский"),
                                                       (3, "Суворовский"), (4, "")),
                                              label=_('new_building_district'),
                                              widget=forms.Select(attrs={'class': 'form-control',
                                                                         'placeholder': _('new_building_district')}))

    class Meta:
        model = LocalityDistrict
        exclude = ('on_delete',)


class StreetForm(forms.ModelForm):
    street = forms.CharField(label=_('street'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                              'placeholder': _("street")}))
    locality_district = forms.ModelChoiceField(queryset=LocalityDistrict.objects.filter(on_delete=False),
                                               label=_('locality_district'),
                                               widget=forms.Select(attrs={'class': 'form-control',
                                                                          'placeholder': _('locality_district')}))

    class Meta:
        model = Street
        exclude = ('on_delete',)


class ClientForm(forms.ModelForm):
    email = forms.CharField(label=_('email'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                            'placeholder': _("email")}))
    first_name = forms.CharField(label=_('first_name'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _("first_name")}))
    last_name = forms.CharField(label=_('last_name'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                    'placeholder': _("last_name")}))
    phone = forms.CharField(label=_('phone'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                            'placeholder': _("phone")}))

    realtor = forms.ModelChoiceField(queryset=CustomUser.objects.all(),
                                     label=_('realtor'),
                                     widget=forms.Select(attrs={'class': 'form-control',
                                                                'placeholder': _('realtor')}))

    status = forms.ChoiceField(choices=((1, "В подборе"),
                                        (2, "С показом"),
                                        (3, "Определившиеся"),
                                        (4, "Отложенный спрос")),
                               label=_('status'),
                               widget=forms.Select(attrs={'class': 'form-control',
                                                          'placeholder': _('status')}))

    rooms_number = forms.IntegerField(label=_("rooms_number"), required=False,
                                      widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                      "placeholder": _("rooms_number")}))
    locality = forms.ModelChoiceField(queryset=Locality.objects.filter(on_delete=False),
                                      label=_('locality'), required=False,
                                      widget=forms.Select(attrs={'class': 'form-control',
                                                                 'placeholder': _('locality')}))
    locality_district = forms.ModelChoiceField(queryset=LocalityDistrict.objects.filter(on_delete=False),
                                               label=_('locality_district'), required=False,
                                               widget=forms.Select(attrs={'class': 'form-control',
                                                                          'placeholder': _('locality_district')}))
    street = forms.ModelChoiceField(queryset=Street.objects.filter(on_delete=False),
                                    label=_('street'), required=False,
                                    widget=forms.Select(attrs={'class': 'form-control',
                                                               'placeholder': _('street')}))
    house = forms.CharField(label=_('house'), required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': _("house")}))
    floor_min = forms.IntegerField(label=_("floor_min"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("floor_min")}))
    floor_max = forms.IntegerField(label=_("floor_max"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("floor_max")}))
    not_first = forms.BooleanField(label=_('not_first'),
                                   widget=forms.CheckboxInput(attrs={'class': '',
                                                                     'placeholder': _("not_first")}),
                                   required=False)
    not_last = forms.BooleanField(label=_('not_last'),
                                  widget=forms.CheckboxInput(attrs={'class': '',
                                                                    'placeholder': _("not_last")}),
                                  required=False)
    storeys_num_min = forms.IntegerField(label=_("storeys_num_min"), required=False,
                                         widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                         "placeholder": _("storeys_num_min")}))
    storeys_num_max = forms.IntegerField(label=_("storeys_num_max"), required=False,
                                         widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                         "placeholder": _("storeys_num_max")}))
    price_min = forms.IntegerField(label=_("price_min"), required=False,
                                      widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                      "placeholder": _("price_min")}))
    price_max = forms.IntegerField(label=_("price_max"), required=False,
                                      widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                      "placeholder": _("price_max")}))
    square_meter_price_max = forms.IntegerField(label=_("square_meter_price_max"), required=False,
                                      widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                      "placeholder": _("square_meter_price_max")}))
    condition = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=2).all(),
        required=False,
        label=_("condition"),
        widget=forms.Select(attrs={'class': 'form-control',
                                   "placeholder": _("condition")}))

    class Meta:
        model = Client
        exclude = ('date_of_add', 'on_delete')


class HandbookForm(forms.ModelForm):
    handbook = forms.CharField(label=_('handbook'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                  'placeholder': _("handbook")}))
    type = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Handbook
        exclude = ('on_delete',)


class FilialForm(forms.ModelForm):
    filial_agency = forms.CharField(label=_('filial_agency'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                            'placeholder': _(
                                                                                                "filial_agency")}))

    class Meta:
        model = FilialAgency
        exclude = ('on_delete',)


class FilialReportForm(forms.ModelForm):
    report = forms.CharField(label=_('report'), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                              'placeholder': _("report")}))

    filial_agency = forms.ModelChoiceField(queryset=FilialAgency.objects.filter(on_delete=False),
                                           label=_('filial_agency'),
                                           widget=forms.Select(attrs={'class': 'form-control',
                                                                      'placeholder': _('filial_agency')}))

    class Meta:
        model = FilialReport
        exclude = ('on_delete',)


class SelectionForm(forms.Form):
    rooms_number = forms.IntegerField(label=_("rooms_number"), required=False,
                                      widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                      "placeholder": _("rooms_number")}))
    locality = forms.ModelChoiceField(queryset=Locality.objects.filter(on_delete=False),
                                      label=_('locality'), required=False,
                                      widget=forms.Select(attrs={'class': 'form-control',
                                                                 'placeholder': _('locality')}))
    locality_district = forms.ModelChoiceField(queryset=LocalityDistrict.objects.filter(on_delete=False),
                                               label=_('locality_district'), required=False,
                                               widget=forms.Select(attrs={'class': 'form-control',
                                                                          'placeholder': _('locality_district')}))
    street = forms.ModelChoiceField(queryset=Street.objects.filter(on_delete=False),
                                    label=_('street'), required=False,
                                    widget=forms.Select(attrs={'class': 'form-control',
                                                               'placeholder': _('street')}))
    house = forms.CharField(label=_('house'), required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': _("house")}))
    floor_min = forms.IntegerField(label=_("floor_min"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("floor_min")}))
    floor_max = forms.IntegerField(label=_("floor_max"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("floor_max")}))
    not_first = forms.BooleanField(label=_('not_first'),
                                   widget=forms.CheckboxInput(attrs={'class': '',
                                                                     'placeholder': _("not_first")}),
                                   required=False)
    not_last = forms.BooleanField(label=_('not_last'),
                                  widget=forms.CheckboxInput(attrs={'class': '',
                                                                    'placeholder': _("not_last")}),
                                  required=False)
    storeys_num_min = forms.IntegerField(label=_("storeys_num_min"), required=False,
                                         widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                         "placeholder": _("storeys_num_min")}))
    storeys_num_max = forms.IntegerField(label=_("storeys_num_max"), required=False,
                                         widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                         "placeholder": _("storeys_num_max")}))
    price_min = forms.IntegerField(label=_("price_min"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("price_min")}))
    price_max = forms.IntegerField(label=_("price_max"), required=False,
                                   widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                   "placeholder": _("price_max")}))
    square_meter_price_max = forms.IntegerField(label=_("square_meter_price_max"), required=False,
                                                widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                                "placeholder": _(
                                                                                    "square_meter_price_max")}))
    condition = forms.ModelChoiceField(
        queryset=Handbook.objects.filter(on_delete=False).filter(type=2).all(),
        required=False,
        label=_("condition"),
        widget=forms.Select(attrs={'class': 'form-control',
                                   "placeholder": _("condition")}))


class IdSearchForm(forms.Form):
    id = forms.IntegerField(label=_("id"),
                            widget=forms.NumberInput(attrs={'class': 'customtxt',
                                                            "placeholder": _("id")}),
                            required=False)

