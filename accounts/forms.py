from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from accounts.models import CustomUser, CustomGroup
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={"class": "form-control",
                                                                             "placeholder": _("Email")}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"class": "form-control",
                                                                                      "placeholder": _("Password")}))

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
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
    image = forms.ImageField(label=_("image"), widget=forms.FileInput(attrs={"class": "form-control",
                                                                             "placeholder": _("image")}))

    class Meta:
        model = CustomUser
        fields = ["image", ]


class UserForm(forms.ModelForm):
    """Форма для редагування користувача."""
    groups = forms.ChoiceField
    email = forms.CharField(
        label=_("email"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("email")})
    )
    first_name = forms.CharField(
        label=_("first_name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("first_name")})
    )
    last_name = forms.CharField(
        label=_("last_name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("last_name")})
    )

    class Meta:
        model = CustomUser
        exclude = ["on_delete", "image", "last_login",
                   "date_joined", "is_staff", "is_superuser",
                   "is_active", "password"]


class RegisterForm(forms.ModelForm):
    """Форма для створення нового користувача."""
    email = forms.CharField(
        label=_("email"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("email")})
    )
    password = forms.CharField(
        label=_("password"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("password")})
    )
    first_name = forms.CharField(
        label=_("first_name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("first_name")})
    )
    last_name = forms.CharField(
        label=_("last_name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("last_name")})
    )

    class Meta:
        model = CustomUser
        exclude = ["on_delete", "image", "last_login",
                   "date_joined", "is_staff", "is_superuser",
                   "is_active"]


class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label=_("name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("name")}))

    class Meta:
        model = CustomGroup
        exclude = ["on_delete"]
