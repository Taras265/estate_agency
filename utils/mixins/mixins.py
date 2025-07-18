from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse

from accounts.services import user_get
from handbooks.forms import IdSearchForm
from handbooks.models import Client
from handbooks.services import client_filter
from utils.const import SALE_CHOICES
from utils.utils import by_user_queryset, get_office_context


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

    def get_queryset(self):
        form = self.form(self.request.GET)
        queryset = super().get_queryset()
        # далі перевіряємо формочку і змінюємо в залежності від неї кверісет
        if form.is_valid():
            for field in form.cleaned_data.keys():
                if form.cleaned_data.get(field):
                    queryset = queryset.filter(**{field: form.cleaned_data.get(field)})
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)

        context.update({"form": self.form(self.request.GET)})

        return context


# змінити на UserPassesTestMixin (потім, не зараз)
class ByUserMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    perms = None

    def get_permission_required(self):
        user = self.request.user

        if user.has_perm(f"{self.app}.{self.perm}_{self.handbook_type}"):
            return (f"{self.app}.{self.perm}_{self.handbook_type}",)
        if user.has_perm(f"{self.app}.{self.perm}_filial_{self.handbook_type}"):
            return (f"{self.app}.{self.perm}_filial_{self.handbook_type}",)
        return (f"{self.app}.{self.perm}_own_{self.handbook_type}",)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        perm = self.get_permission_required()[0]

        if perm.find("own") != -1:
            queryset = by_user_queryset(queryset, self.handbook_type, user)
        elif perm.find("filial") != -1:
            queryset = by_user_queryset(
                queryset, self.handbook_type, user.filials.all(), "filials__in"
            )
        return queryset


class ClientListMixin:
    """
    Міксін, який об"єднує повторювані параметри. Використовувати разом з CustomListView
    """

    choices = SALE_CHOICES
    permission_required = "handbooks.view_client"
    template_name = "handbooks/client_list.html"

    app = "handbooks"
    handbook_type = "client"

    filters = ["all", "new", "in_selection", "with_show", "decided", "deferred_demand"]

    queryset: QuerySet[Client]

    own = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context["object_list"]:
            return context

        # у полі object_type замінюємо число на відповідний текст
        for index, obj in enumerate(context["object_values"]):
            client: Client = context["object_list"][index]
            obj["object_type"] = client.get_object_type_display()

        return context


class UserClientListMixin(ClientListMixin):
    """
    Міксін використувуємо для випадків коли ми показумємо список клієнтів, але нам треба що список залежав від того,
    який користувач дивиться (бачити тільки своїх клієнтів у БУДЬ ЯКОМУ випадку)
    """

    template_name = "handbooks/office_client_list.html"
    permission_required = "handbooks.view_own_office_client"

    def get_queryset(self):
        return client_filter(self.queryset, realtor=user_get(email=self.request.user))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_office_context(self.request.user))

        return context


class FilialClientListMixin(ClientListMixin):
    """
    Міксін використувуємо для випадків коли ми показумємо список клієнтів, але нам треба що список залежав від того,
    які є філіали має користувач, який дивиться (бачити тільки клієнтів свого філіалу у БУДЬ ЯКОМУ випадку)
    """

    template_name = "handbooks/office_filial_client_list.html"
    permission_required = "handbooks.view_own_office_client"

    def get_queryset(self):
        return client_filter(
            self.queryset,
            realtor__filials__in=user_get(email=self.request.user).filials.all(),
        ).distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_office_context(self.request.user))

        return context
