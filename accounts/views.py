from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, CreateView, DetailView, DeleteView

from accounts.forms import LoginForm, AvatarForm, UserForm, RegisterForm
from accounts.models import CustomUser, CustomGroup
from django.utils.translation import activate

from handbooks.models import UserFilial
from utils.const import USER_CHOICES
from utils.mixins.mixins import FormMixin, HandbookListMixin, FormHandbooksMixin, HandbookHistoryListMixin, \
    DeleteHandbooksMixin


def login_view(request, lang):
    form = LoginForm(request.POST or None)
    _next = request.GET.get('next')
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        login(request, user)
        _next = _next or f'/{lang}/'
        return redirect(_next)
    return render(request, 'accounts/login.html', {'form': form, 'lang': lang})


def logout_view(request, lang):
    logout(request)
    return redirect(f'/{lang}/accounts/login/', {'lang': lang})


class ProfileView(FormMixin, UpdateView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'accounts/profile.html'
    form_class = AvatarForm
    success_url = reverse_lazy("accounts:profile")

    permission_required = 'accounts.profile'

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"lang": self.kwargs['lang'], })

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])
        context = super().get_context_data(**kwargs)
        context['filial'] = UserFilial.objects.filter(user=context['user']).first()

        return context

    def get_object(self, queryset=None):
        return CustomUser.objects.get(email=self.request.user)


def users_list_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    if user:
        if user.has_perm('accounts.view_customuser'):
            return redirect(f'/{lang}/accounts/accounts/user/', {'lang': lang})
        elif user.has_perm('auth.view_group'):
            return redirect(f'/{lang}/accounts/accounts/group/', {'lang': lang})
    return redirect(reverse_lazy('accounts:login', kwargs={'lang': lang}))


class UserListView(HandbookListMixin, ListView):
    model = CustomUser
    handbook_type = 'user'
    choices = USER_CHOICES


class GroupListView(HandbookListMixin, ListView):
    model = CustomGroup
    handbook_type = 'group'
    choices = USER_CHOICES


class HandbookCreateView(FormHandbooksMixin, CreateView):
    handbook_type = None
    perm_type = 'add'

    def get_form(self, form_class=None):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if handbook_type == 'user':
            return super().get_form(RegisterForm)
        return super().get_form()

    def form_valid(self, form):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if handbook_type == 'user' and form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
        return super().form_valid(form)


class HandbookUpdateView(FormHandbooksMixin, UpdateView):
    handbook_type = None
    perm_type = 'change'


class HandbookDeleteView(DeleteHandbooksMixin, DeleteView):
    handbook_type = None


class HandbookHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'
    handbook_type = None

    def dispatch(self, request, *args, **kwargs):
        print("Dispatch вызван")
        form = self.get_form()  # Это гарантирует вызов вашего `get_form`
        print("Form вызван в dispatch")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        print(HandbookCreateView.__mro__)
        return super().get_object()
