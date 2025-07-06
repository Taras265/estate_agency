from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.utils.translation import activate

from accounts.models import CustomUser
from handbooks.forms import IdSearchForm
from utils.const import (
    BASE_CHOICES,
    LIST_BY_USER,
    OBJECT_COLUMNS,
    OBJECT_FIELDS,
)
from utils.utils import have_permission_to_do, table_to_app


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Використовуємо замість звичайного LoginRequiredMixin, бо в нас трохи інше посилання на
    сторінку входу.
    """

    def get_login_url(self):
        lang = self.kwargs["lang"]
        return reverse("accounts:login", kwargs={"lang": lang})


class HandbookListMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    paginate_by = 5
    template_name = "handbooks/list.html"
    context_object_name = "objects"

    handbook_type = None
    model = None
    form = IdSearchForm
    choices = BASE_CHOICES

    custom = False

    def get_queryset(self):
        form = self.form(self.request.GET)
        queryset = self.model.objects.filter(on_delete=False)
        if form.is_valid():
            for field in form.cleaned_data.keys():
                if form.cleaned_data.get(field):
                    queryset = queryset.filter(**{field: form.cleaned_data.get(field)})
        return queryset

    def get_permission_required(
        self,
    ):  # Отримаємо яке нам потрібно право для цієї сторінки
        if not self.permission_required:
            self.permission_required = (
                f"{table_to_app(self.handbook_type)}.view_{self.handbook_type}"
            )
        return super().get_permission_required()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # переклад

        user = CustomUser.objects.filter(email=self.request.user).first()

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        context["form"] = self.form(self.request.GET)

        context["choice"] = self.handbook_type
        context.update({"choices": self.choices_by_user(user)})

        """
        Ми можемо бачити дату, але, наприклад, не можемо її додавати чи продивлятись історію змін.
        Тому ми тут робимо перевірку
        """
        if not self.custom:
            context["can_create"] = user.has_perm(
                f"handbooks.add_{self.handbook_type}"
            ) or user.has_perm(f"objects.add_{self.handbook_type}")
            context["can_view_history"] = user.has_perm(
                f"handbooks.view_historical{self.handbook_type}"
            ) or user.has_perm(f"handbooks.view_historical{self.handbook_type}")

        """
        Обробляємо список з ДІЙСНО потрібними для клієнта даними 
        (районами, квартирами ітд).
        """
        # Якщо нам немає з чим працювати
        if not context["object_list"]:
            context["object_columns"] = None
            return context

        # беремо список назв стовпців, які потрібно відображати на вебсторінці
        object_columns: list[str] | None = OBJECT_COLUMNS.get(self.handbook_type)

        # Якщо ми налаштували, які дані потрібно відображати в таблиці
        if object_columns:
            context["object_columns"] = object_columns  # Назви стовпців
        else:
            # Теж саме, що і в частині коду вище, але нам потрібні всі дані, тож ми нічого не викидуємо
            context["object_columns"] = list(context["object_list"].values()[0])

        # беремо список полів таблиці, значення яких потрібно відображати на вебсторінці
        object_fields: list[str] | None = OBJECT_FIELDS.get(self.handbook_type)

        if object_fields:
            context["object_values"] = context["object_list"].values(*object_fields)
        else:
            context["object_values"] = context["object_list"].values()

        for obj in context["object_values"]:
            # Перевірка того, що клієнт взагалі щось ще може, крім як дивитись на дані
            can_update = have_permission_to_do(user, "change", self.handbook_type, obj)
            can_view_history = have_permission_to_do(
                user, "view", self.handbook_type, obj, "historical"
            )

            if not self.custom:
                obj.update(
                    {
                        "user_permissions": {
                            "can_update": can_update,
                            "can_view_history": can_view_history,
                        }
                    }
                )

        return context

    def choices_by_user(self, user):
        choices = []
        for choice in self.choices:
            app = table_to_app(choice) or "objects"
            if (
                user.has_perm(f"{app}.view_{choice}")
                or user.has_perm(f"{app}.view_own_{choice}")
                or user.has_perm(f"{app}.view_filial_{choice}")
            ):
                choices.append(choice)
        return choices


class HandbookOwnPermissionListMixin(HandbookListMixin):
    def get_queryset(self):
        self.queryset = HandbookListMixin.get_queryset(self)

        if self.permission_required.find("own") != -1:
            user = CustomUser.objects.filter(email=self.request.user).first()
            if isinstance(LIST_BY_USER[self.handbook_type], str):
                self.queryset = self.queryset.filter(
                    **{LIST_BY_USER[self.handbook_type]: user}
                )
            else:
                new_queryset = None
                for field in LIST_BY_USER[self.handbook_type]:
                    if new_queryset:
                        new_queryset = new_queryset | self.queryset.filter(
                            **{field: user}
                        )
                    else:
                        new_queryset = self.queryset.filter(**{field: user})
                self.queryset = new_queryset
        return self.queryset

    def get_permission_required(
        self,
    ):  # Отримаємо яке нам потрібно право для цієї сторінки
        if not self.permission_required:
            user = CustomUser.objects.filter(email=self.request.user).first()

            if user.has_perm(
                f"{table_to_app(self.handbook_type)}.view_{self.handbook_type}"
            ):
                self.permission_required = (
                    f"{table_to_app(self.handbook_type)}.view_{self.handbook_type}"
                )
            else:
                self.permission_required = (
                    f"{table_to_app(self.handbook_type)}.view_own_{self.handbook_type}"
                )
        return (self.permission_required,)


class HandbookWithFilterListMixin(HandbookListMixin):
    filters = []
    queryset_filters = {}

    def get_queryset(self):
        f = (
            self.kwargs.get("filter") or list(self.queryset_filters.keys())[0]
        )  # просто вір - так і має бути
        queryset = self.queryset_filters[f].all()
        if queryset.model != self.model:
            self.model = queryset.model
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        f = (
            self.kwargs.get("filter") or list(self.queryset_filters.keys())[0]
        )  # просто вір - так і має бути

        context = super().get_context_data(**kwargs)
        context["filters"] = self.filters
        context["filter"] = f
        context["app"] = table_to_app(context["choice"])

        return context
