from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from utils.utils import  table_to_app
from django.utils.translation import activate


class CustomCreateView(CreateView):
    template_name = "form.html"
    success_message = "Success"

    form_class = None
    model = None
    permission_required = None

    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type or self.kwargs.get("handbook_type")
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(
            f"{table_to_app(handbook_type)}:{handbook_type}_list", kwargs=kwargs
        )


class CustomUpdateView(UpdateView):
    template_name = "form.html"
    success_message = "Success"

    form_class = None
    model = None
    permission_required = None

    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(
            f"{table_to_app(handbook_type)}:{handbook_type}_list", kwargs=kwargs
        )


class CustomDeleteView(DeleteView):
    template_name = "delete_form.html"
    success_message = "Success"
    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context

    def get_success_url(self):
        handbook_type = self.handbook_type
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy(
            f"{table_to_app(handbook_type)}:{handbook_type}_list", kwargs=kwargs
        )


class HistoryView(DetailView):
    """
    Вьюшка щоб подивитись історію змін
    """

    template_name = "handbooks/history_list.html"
    model = None
    handbook_type = None

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

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
                        changes.append(
                            {
                                "date": record.history_date,
                                "user": record.history_user,
                                "field": field.verbose_name,
                                "old_value": old_value,
                                "new_value": new_value,
                            }
                        )
        context["history"] = changes
        context["handbook"] = self.handbook_type
        context["list_url"] = (
            f"{table_to_app(self.handbook_type)}:{self.handbook_type}_list"
        )

        return context
