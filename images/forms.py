from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.utils.translation import gettext_lazy as _

from images.models import RealEstateImage
from objects.models import Apartment


class ApartmentImageForm(forms.ModelForm):
    apartment = forms.ModelChoiceField(
        queryset=Apartment.objects.all(),
        widget=forms.HiddenInput()
    )
    image = forms.ImageField(
        label=_("Image"),
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = RealEstateImage
        fields = ["apartment", "image"]


RealEstateImageFormSet = generic_inlineformset_factory(
    RealEstateImage,
    fields=["image"],
    extra=1,
)