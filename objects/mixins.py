from django.views.generic.base import ContextMixin
from django.utils.translation import activate

from images.forms import RealEstateImageFormSet
from images.models import RealEstateImage

from .choices import RealEstateType
from .services import user_can_view_report


class RealEstateCreateContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок
    з формою створення обʼєкту нерухомості.
    """

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "lang": self.kwargs["lang"],
                "real_estate_choices": RealEstateType.choices,
                "can_add_apartment": user.has_perm("objects.add_apartment"),
                "can_add_own_apartment": user.has_perm("objects.add_own_apartment"),
                "can_add_commerce": user.has_perm("objects.add_commerce"),
                "can_add_own_commerce": user.has_perm("objects.add_own_commerce"),
                "can_add_house": user.has_perm("objects.add_house"),
                "can_add_own_house": user.has_perm("objects.add_own_house"),
                "can_add_land": user.has_perm("objects.add_land"),
                "can_add_own_land": user.has_perm("objects.add_own_land"),
                "formset": RealEstateImageFormSet(
                    queryset=RealEstateImage.objects.none(),
                    prefix="images",
                ),
            }
        )
        return context


class RealEstateUpdateContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок
    з формою редагування обʼєкту нерухомості.
    """

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "lang": self.kwargs["lang"],
                "formset": RealEstateImageFormSet(
                    instance=self.object,
                    prefix="images",
                ),
            }
        )
        return context


class SaleListContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок
    зі списком (таблицею) нерухомості.
    """

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "form": self.form_class(self.request.GET) if self.form_class else None,
            "can_view_report": user_can_view_report(self.request.user),
        })
        return context


class DefaultUserInCreateViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
