from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from django.utils.translation import activate

from accounts.forms import LoginForm, AvatarForm, UserForm, RegisterForm, GroupForm
from accounts.models import CustomUser
from accounts.services import (
    user_all_visible, user_filter, group_filter, group_all_visible,
    user_can_create_user, user_can_update_user, user_can_view_custom_group,
    user_can_view_user_history, user_get
)
from handbooks.forms import PhoneNumberFormSet, IdSearchForm
from utils.const import USER_CHOICES
from utils.mixins.new_mixins import CustomLoginRequiredMixin, StandardContextDataMixin, GetQuerysetMixin
from utils.utils import get_office_context
from utils.views import CustomListView, CustomCreateView, CustomUpdateView, CustomDeleteView, HistoryView


def login_view(request, lang):
    activate(lang)
    form = LoginForm(request.POST or None)
    _next = request.GET.get("next")
    if form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(email=email, password=password)
        login(request, user)
        _next = _next or f"/{lang}/"
        return redirect(_next)
    return render(request, "accounts/login.html", {"form": form, "lang": lang})


def logout_view(request, lang):
    logout(request)
    return redirect(f"/{lang}/accounts/login/", {"lang": lang})


def office_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()
    kwargs = {"lang": lang}
    if user:
        if user.has_perm(f"handbooks.view_own_office_client"):
            return redirect(reverse_lazy("handbooks:office_client_list", kwargs=kwargs))
        elif user.has_perm(f"objects.view_own_office_objects"):
            return redirect(reverse_lazy("objects:office_apartment_list", kwargs=kwargs))
        elif user.has_perm(f"accounts.view_office_user"):
            return redirect(reverse_lazy("accounts:office_user_list", kwargs=kwargs))
        return render(request, "403.html", kwargs)
    return redirect(reverse_lazy("accounts:login", kwargs=kwargs))


class ProfileView(CustomLoginRequiredMixin, StandardContextDataMixin, UpdateView):
    context_object_name = "user"
    template_name = "accounts/profile.html"
    form_class = AvatarForm
    success_message = "Success"

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"lang": self.kwargs["lang"]})

    def get_object(self, queryset=None):
        return CustomUser.objects.prefetch_related("filials").get(email=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = user_get(email=self.request.user)

        return context


def users_list_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()
    kwargs = {"lang": lang}

    if user:
        if user.has_perm(f"accounts.view_customuser"):
            return redirect(reverse_lazy("accounts:user_list", kwargs=kwargs))
        if user.has_perm(f"accounts.view_group"):
            return redirect(reverse_lazy("accounts:group_list", kwargs=kwargs))
        return render(request, "403.html", kwargs)
    return redirect(reverse_lazy("accounts:login", kwargs=kwargs))


class UserListView(CustomLoginRequiredMixin, PermissionRequiredMixin, ListView):
    paginate_by = 5
    permission_required = "accounts.view_user"
    template_name = "accounts/user_list.html"
    context_object_name = "user_list"

    def get_queryset(self):
        queryset = user_all_visible().prefetch_related("phone_numbers")

        return queryset
    
    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context.update({
            "lang": self.kwargs["lang"],
            "can_view_customgroup": user_can_view_custom_group(self.request.user),
            "can_create": user_can_create_user(self.request.user),
            "can_update": user_can_update_user(self.request.user),
            "can_view_history": user_can_view_user_history(self.request.user),
        })
        return context


class MyUserListView(UserListView):
    permission_required = "accounts.view_office_user"
    template_name = "accounts/office_user_list.html"

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        user = user_get(email=self.request.user)
        context = get_office_context(user, super().get_context_data(**kwargs))
        context.update({
            "lang": self.kwargs["lang"],
            "can_create": user_can_create_user(self.request.user),
            "can_update": user_can_update_user(self.request.user),
            "can_view_history": user_can_view_user_history(self.request.user),
        })
        return context


class GroupListView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomListView):
    queryset = group_all_visible()
    main_service = {"objects_filter": group_filter, }
    choices = USER_CHOICES
    permission_required = "accounts.view_group"

    handbook_type = "group"


class UserCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView):
    template_name = "accounts/user_form.html"
    form_class = RegisterForm
    permission_required = "accounts.add_user"

    handbook_type = "user"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.POST:
            context["formset"] = PhoneNumberFormSet(self.request.POST)
        else:
            context["formset"] = PhoneNumberFormSet()
        return context

    def form_valid(self, form):
        formset = PhoneNumberFormSet(self.request.POST)
        if not formset.is_valid():
            return super().form_invalid(form)

        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        form.save_m2m()

        for phone_number in formset.save(commit=False):
            phone_number.user = user
            phone_number.save()

        return redirect(super().get_success_url())


class GroupCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView):
    form_class = GroupForm
    permission_required = "auth.add_group"

    handbook_type = "group"


class UserUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView):
    template_name = "accounts/user_form.html"
    queryset = user_all_visible()
    form_class = UserForm
    permission_required = "accounts.change_user"
    handbook_type = "user"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.POST:
            context["formset"] = PhoneNumberFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = PhoneNumberFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        formset = PhoneNumberFormSet(self.request.POST, instance=self.object)
        if not formset.is_valid():
            return super().form_invalid(form)

        form.save()
        formset.save()
        return redirect(super().get_success_url())


class GroupUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView):
    queryset = group_all_visible()
    form_class = GroupForm
    permission_required = "auth.change_group"
    handbook_type = "group"


class UserDeleteView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView):
    queryset = user_all_visible()
    permission_required = "accounts.delete_user"
    handbook_type = "user"


class GroupDeleteView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomDeleteView):
    queryset = group_all_visible()
    permission_required = "auth.delete_group"
    handbook_type = "group"

class UserHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    queryset = user_all_visible()
    permission_required = "accounts.view_user"
    handbook_type = "user"


class GroupHistoryView(CustomLoginRequiredMixin, PermissionRequiredMixin, HistoryView):
    queryset = group_all_visible()
    permission_required = "auth.view_group"
    handbook_type = "group"
