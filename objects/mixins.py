from django.views.generic.base import ContextMixin

from .choices import RealEstateType
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
