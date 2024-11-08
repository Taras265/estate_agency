from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from utils.const import CHOICES, HANDBOOKS_QUERYSET
from utils.mixins.mixins import (HandbookHistoryListMixin, HandbookListPermissionMixin,
                                 FormHandbooksMixin, DeleteHandbooksMixin)


def handbook_redirect(request, lang):
    # Функція, яка перебрасує користувача на довідник,
    # з яким він моєе взаємодіяти
    user = CustomUser.objects.filter(email=request.user).first()

    if user:
        for choice in CHOICES:
            cleaned_choice = ''.join(choice[1].split('_'))
            if (user.has_perm(f'handbooks.view_{cleaned_choice}')
                    or user.has_perm(f'handbooks.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/handbook/base/{choice[1]}/', {'lang': lang})
            if (user.has_perm(f'objects.view_{cleaned_choice}')
                    or user.has_perm(f'objects.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/objects/base/{choice[1]}/', {'lang': lang})
        return render(request, '403.html', {'lang': lang})
    return redirect(reverse_lazy('accounts:login', kwargs={'lang': 'en'}))


class HandbookListView(HandbookListPermissionMixin, ListView):
    handbook_type = None


class HandbookCreateView(FormHandbooksMixin, CreateView):
    handbook_type = None
    perm_type = 'add'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data') and kwargs.get('data').get('handbook'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs


class HandbookUpdateView(FormHandbooksMixin, UpdateView):
    handbook_type = None
    perm_type = 'change'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data') and kwargs.get('data').get('handbook'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs


class HandbookDeleteView(DeleteHandbooksMixin, DeleteView):
    handbook_type = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs


class HandbookHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = None

    def get_object(self, queryset=None):
        return super().get_object()
