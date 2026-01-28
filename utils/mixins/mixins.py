from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from handbooks.forms import IdSearchForm


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Використовуємо замість звичайного LoginRequiredMixin, бо в нас трохи інше посилання на
    сторінку входу.
    """

    def get_login_url(self):
        lang = self.kwargs["lang"]
        return reverse("accounts:login", kwargs={"lang": lang})


class CustomPaginateOnPageMixin:
    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page and per_page.isdigit():
            return int(per_page)
        return self.paginate_by


class SearchByIdMixin:
    form = IdSearchForm

    def get_queryset(self):
        form = self.form(self.request.GET)
        queryset = super().get_queryset()
        if not form.is_valid():
            return queryset.none()
        
        if (id := form.cleaned_data.get("id")):
            queryset = queryset.filter(id=id)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"form": self.form(self.request.GET)})
        return context