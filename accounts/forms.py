from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from accounts.models import CustomUser
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'class': 'form-control',
                                                                             'placeholder': _("Email")}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                      'placeholder': _("Password")}))

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            qs = CustomUser.objects.filter(email=email)
            if not qs.exists():
                raise ValueError(_("There is no user with this email"))
            if not check_password(password, qs[0].password):
                raise ValueError(_("The password is not valid"))
            user = authenticate(email=email, password=password)
            if not user:
                raise ValueError(_("The user is inactive"))
            return super().clean(*args, **kwargs)


class AvatarForm(forms.ModelForm):
    image = forms.ImageField(label=_("image"), widget=forms.FileInput(attrs={'class': 'form-control',
                                                                             'placeholder': _("image")}))

    class Meta:
        model = CustomUser
        fields = ['image', ]
