from django import forms

from images.models import RealEstateImage
from objects.models import Apartment
from django.utils.translation import gettext_lazy as _


class ApartmentImageForm(forms.ModelForm):
    apartment = forms.ModelChoiceField(queryset=Apartment.objects.all(), widget=forms.HiddenInput())
    image = forms.ImageField(label=_("image"), widget=forms.FileInput(attrs={'class': 'form-control',
                                                                             'placeholder': _("image")}))

    class Meta:
        model = RealEstateImage
        fields = ['apartment', 'image']
