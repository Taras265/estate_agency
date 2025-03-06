from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from handbooks.forms import IdSearchForm
from handbooks.models import Handbook
from accounts.services import get_user_choices, user_get
from handbooks.services import handbook_filter
from utils.const import TABLE_TO_APP, OBJECT_COLUMNS, BASE_CHOICES
from utils.mixins.new_mixins import GetQuerysetMixin, StandardContextDataMixin
from utils.utils import model_to_dict


class CustomListView(StandardContextDataMixin, GetQuerysetMixin, ListView):
    """
    Вьюшка для списку

    filters і filter вказувати, якщо в нас є підвиди списку
    (приклад: у вкладці клієнта є вкладки "всі клієнти", "нові клієнти" ітд)
    """
    paginate_by = 5
    template_name = "handbooks/list.html"
    context_object_name = "objects"

    model = None
    choices = None
    main_service = None

    app = None
    handbook_type = None

    filters = None
    filter = None

    own = False

    def get_context_data(self, *, object_list=None, **kwargs):
        user = user_get(email=self.request.user)

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)

        context.update({
            "choice": self.handbook_type,
            "choices": get_user_choices(user, self.choices),
            "can_create": user.has_perm(f"{self.app}.add_{self.handbook_type}"),
            "filters": self.filters,
            "filter": self.filter,
            "handbook": self.handbook_type,
        })

        if context.get("objects"):
            object_columns = (OBJECT_COLUMNS.get(self.handbook_type)
                              or list(context["object_list"].values()[0]))

            context.update({
                "object_columns": object_columns,
                "object_values": model_to_dict(
                    user,
                    context["page_obj"].object_list,
                    self.app,
                    self.handbook_type,
                    self.own
                )
            })

        return context


class CustomHandbookListView(CustomListView):
    """
    Вьюшка для списку з бд Handbook
    """
    main_service = {"objects_filter": handbook_filter, }
    choices = BASE_CHOICES

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context["object_list"]:
            return context

        # у полі new_building_district замінюємо число на відповідний йому текст
        for index, obj in enumerate(context["object_values"]):
            handbook: Handbook = context["object_list"][index]
            obj["type"] = handbook.get_type_display()

        return context


class CustomCreateView(StandardContextDataMixin, CreateView):
    template_name = "form.html"
    success_message = "Success"

    form_class = None
    model = None
    main_service = None
    permission_required = None

    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type or self.kwargs.get("handbook_type")
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:{handbook_type}_list", kwargs=kwargs)


class CustomUpdateView(StandardContextDataMixin, GetQuerysetMixin, UpdateView):
    template_name = "form.html"
    success_message = "Success"

    form_class = None
    model = None
    main_service = None
    permission_required = None

    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:{handbook_type}_list", kwargs=kwargs)


class CustomDeleteView(StandardContextDataMixin, GetQuerysetMixin, DeleteView):
    template_name = "delete_form.html"
    success_message = "Success"
    model = None
    main_service = None
    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:{handbook_type}_list", kwargs=kwargs)


class HistoryView(StandardContextDataMixin, GetQuerysetMixin, DetailView):
    """
    Вьюшка щоб подивитись історію змін
    """
    template_name = "handbooks/history_list.html"
    model = None
    main_service = None
    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        history = context["object"].history.all()
        changes = []
        for record in history:
            if record.prev_record:
                prev_record = record.prev_record
                for field in context["object"]._meta.fields:
                    field_name = field.name
                    old_value = getattr(prev_record, field_name)
                    new_value = getattr(record, field_name)
                    if old_value != new_value:
                        changes.append({
                            "date": record.history_date,
                            "user": record.history_user,
                            "field": field.verbose_name,
                            "old_value": old_value,
                            "new_value": new_value
                        })
        context["history"] = changes
        context["handbook"] = self.handbook_type
        context["list_url"] = f"{TABLE_TO_APP[self.handbook_type]}:{self.handbook_type}_list"

        return context
