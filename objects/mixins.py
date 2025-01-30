from django.views.generic.base import ContextMixin
from django.utils.translation import activate

from .choices import RealEstateType
from .services import has_any_perm_form_list
from images.models import RealEstateImage
from images.forms import RealEstateImageFormSet


class RealEstateCreateContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок 
    з формою створення обʼєкту нерухомості.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "real_estate_choices": RealEstateType.choices,
            "can_add_apartment": self.request.user.has_perm("objects.add_apartment"),
            "can_add_own_apartment": self.request.user.has_perm("objects.add_own_apartment"),
            "can_add_commerce": self.request.user.has_perm("objects.add_commerce"),
            "can_add_own_commerce": self.request.user.has_perm("objects.add_own_commerce"),
            "can_add_house": self.request.user.has_perm("objects.add_house"),
            "can_add_own_house": self.request.user.has_perm("objects.add_own_house"),
            "formset": RealEstateImageFormSet(
                queryset=RealEstateImage.objects.none(),
                prefix="images",
            ),
        })
        return context


class RealEstateUpdateContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок 
    з формою редагування обʼєкту нерухомості.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "formset": RealEstateImageFormSet(
                instance=self.object,
                prefix="images",
            ),
        })
        return context


class SaleListContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок 
    зі списком (таблицею) клієнтів, обʼєктів, звітів та контрактів.
    """
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self.form_class(self.request.GET),
            "can_view_client": has_any_perm_form_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": has_any_perm_form_list(
                self.request.user,
                "objects.view_apartment",
                "objects.view_own_apartment",
                "objects.view_commerce",
                "objects.view_own_commerce",
                "objects.view_house",
                "objects.view_own_house",
            ),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
        })
        return context