from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.translation import activate

from accounts.services import user_get
from handbooks.forms import IdSearchForm
from handbooks.models import Client
from handbooks.services import client_filter
from utils.const import SALE_CHOICES, LIST_BY_USER


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Використовуємо замість звичайного LoginRequiredMixin, бо в нас трохи інше посилання на
    сторінку входу.
    """

    def get_login_url(self):
        lang = self.kwargs["lang"]
        return reverse("accounts:login", kwargs={"lang": lang})


class SearchByIdMixin:
    form = IdSearchForm
    main_service = None

    def get_queryset(self):
        form = self.form(self.request.GET)
        queryset = super().get_queryset()
        # далі перевіряємо формочку і змінюємо в залежності від неї кверісет
        if form.is_valid():
            for field in form.cleaned_data.keys():
                if form.cleaned_data.get(field):
                    queryset = self.main_service["objects_filter"](
                        queryset,
                        **{field: form.cleaned_data.get(field)}
                    )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)

        context.update({"form": self.form(self.request.GET)})

        return context


# змінити на UserPassesTestMixin (потім, не зараз)
class ByUserMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    perm = None

    def get_permission_required(self):
        user = user_get(email=self.request.user)

        if user.has_perm(f"{self.app}.{self.perm}_{self.handbook_type}"):
            return (f"{self.app}.{self.perm}_{self.handbook_type}", )
        return (f"{self.app}.{self.perm}_own_{self.handbook_type}", )

    def get_queryset(self):
        queryset = super().get_queryset()
        user = user_get(email=self.request.user)
        perm = self.get_permission_required()[0]

        if perm.find("own") != -1:
            if isinstance(LIST_BY_USER[self.handbook_type], str):
                queryset = queryset.filter(**{LIST_BY_USER[self.handbook_type]: user})
            else:
                new_queryset = None
                for field in LIST_BY_USER[self.handbook_type]:
                    if new_queryset:
                        new_queryset = new_queryset | self.queryset.filter(**{field: user})
                    else:
                        new_queryset = queryset.filter(**{field: user})
                queryset = new_queryset

        return queryset


class ClientListMixin:
    """
    Міксін, який об"єднує повторювані параметри. Використовувати разом з CustomListView
    """
    main_service = {"objects_filter": client_filter, }
    choices = SALE_CHOICES
    permission_required = "handbooks.view_client"
    template_name = "handbooks/client_list.html"

    app = "handbooks"
    handbook_type = "client"

    filters = ["all", "new", "in_selection", "with_show", "decided", "deferred_demand"]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context["object_list"]:
            return context

        # у полі object_type замінюємо число на відповідний текст
        for index, obj in enumerate(context["object_values"]):
            client: Client = context["object_list"][index]
            obj["object_type"] = client.get_object_type_display()

        return context


class GetQuerysetMixin:
    """
    Міксін, який виконує найпоширінішу варіацію функції get_queryset
    """
    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        raise ImproperlyConfigured(
            "%(cls)s is missing a Queryset. Define "
            "%(cls)s.queryset or %(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
        )


class StandardContextDataMixin:
    """
    Міксін, який виконує найпоширінішу варіацію функції get_context_data. Використовувати, мабуть, завжди
    """
    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context
