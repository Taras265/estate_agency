from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from handbooks.forms import RegionForm, DistrictForm, LocalityForm, LocalityDistrictForm, StreetForm, ClientForm, \
    HandbookForm, FilialForm, FilialReportForm
from handbooks.models import (Region, District, Locality, LocalityDistrict,
                              Street, ObjectType, Client, Handbook, FilialAgency, FilialReport)
from utils.const import CHOICES, MODEL, HANDBOOKS_QUERYSET, LIST_BY_USER, OBJECT_COLUMNS
from utils.mixins.mixins import FormMixin, DeleteMixin, \
    HandbookHistoryListMixin, CustomLoginRequiredMixin, HandbookListPermissionMixin, FormHandbooksMixin, \
    DeleteHandbooksMixin
from django.utils.translation import gettext as _
from django.utils.translation import activate


def handbook_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    for choice in CHOICES:
        cleaned_choice = ''.join(choice[1].split('_'))
        if (user.has_perm(f'handbooks.view_{cleaned_choice}')
                or user.has_perm(f'handbooks.view_own_{cleaned_choice}')):
            return redirect(f'/{lang}/handbook/base/{choice[1]}/', {'lang': lang})
        if (user.has_perm(f'objects.view_{cleaned_choice}')
                or user.has_perm(f'objects.view_own_{cleaned_choice}')):
            return redirect(f'/{lang}/objects/base/{choice[1]}/', {'lang': lang})
    return render(request, '403.html', {'lang': lang})


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
