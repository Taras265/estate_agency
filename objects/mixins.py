from django.views.generic.base import ContextMixin
from django.utils.translation import activate

from images.forms import RealEstateImageFormSet
from images.models import RealEstateImage

from .choices import RealEstateType


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


class RealEstateListContextMixin(ContextMixin):
    """
    Додає додаткові значеня до контексту для сторінок
    зі списком (таблицею) нерухомості.
    """

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            "lang": self.kwargs["lang"],
            "form": self.form_class(self.request.GET) if self.form_class else None,
            "can_view_report": user.has_perm("objects.view_changes_report"),
            "can_create": user.has_perm("objects.add_own_real_estate"),
        })
        return context


class DefaultUserInCreateViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
