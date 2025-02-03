from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import LoginForm, AvatarForm, UserForm, RegisterForm, GroupForm
from accounts.models import CustomUser

from handbooks.models import UserFilial
from accounts.services import user_all_visible, user_filter, group_filter, group_all_visible, user_get
from utils.const import USER_CHOICES
from utils.mixins.new_mixins import CustomLoginRequiredMixin, StandardContextDataMixin, GetQuerysetMixin
from utils.views import CustomListView, CustomCreateView, CustomUpdateView, CustomDeleteView, HistoryView


def login_view(request, lang):
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


class ProfileView(StandardContextDataMixin, GetQuerysetMixin, CustomLoginRequiredMixin, UpdateView):
    queryset = user_all_visible()
    context_object_name = "user"
    template_name = "accounts/profile.html"
    form_class = AvatarForm
    success_url = reverse_lazy("accounts:profile")
    success_message = "Success"

    permission_required = "accounts.profile"

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"lang": self.kwargs["lang"], })

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filial"] = UserFilial.objects.filter(user=context["user"]).first()
        return context

    def get_object(self, queryset=None):
        return user_get(email=self.request.user)


def users_list_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    if user:
        if user.has_perm("accounts.view_customuser"):
            return redirect(f"/{lang}/accounts/accounts/user/", {"lang": lang})
        elif user.has_perm("auth.view_group"):
            return redirect(f"/{lang}/accounts/accounts/group/", {"lang": lang})
    return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))


class UserListView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomListView):
    queryset = user_all_visible()
    main_service = {"objects_filter": user_filter, }
    choices = USER_CHOICES
    permission_required = "accounts.view_user"

    handbook_type = "user"


class GroupListView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomListView):
    queryset = group_all_visible()
    main_service = {"objects_filter": group_filter, }
    choices = USER_CHOICES
    permission_required = "accounts.view_group"

    handbook_type = "group"


class UserCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView):
    form_class = RegisterForm
    permission_required = "accounts.add_user"

    handbook_type = "user"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        return super().form_valid(form)


class GroupCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomCreateView):
    form_class = GroupForm
    permission_required = "auth.add_group"

    handbook_type = "group"


class UserUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CustomUpdateView):
    queryset = user_all_visible()
    form_class = UserForm
    permission_required = "accounts.change_user"
    handbook_type = "user"


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
