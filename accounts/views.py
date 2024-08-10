from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from accounts.forms import LoginForm, AvatarForm
from accounts.models import CustomUser
from django.utils.translation import activate

from utils.mixins.mixins import FormMixin


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

    choice_name = 'profile'

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"lang": self.kwargs['lang'], })

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])
        context = super().get_context_data(**kwargs)

        return context

    def get_object(self, queryset=None):
        return CustomUser.objects.get(email=self.request.user)
