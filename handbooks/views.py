from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from handbooks.models import (Region, District, Locality, LocalityDistrict, Street,
                              Client, Handbook, FilialAgency, FilialReport)
from utils.const import CHOICES, HANDBOOKS_QUERYSET
from utils.mixins.mixins import (HandbookHistoryListMixin,
                                 FormHandbooksMixin, DeleteHandbooksMixin, HandbookListMixin,
                                 HandbooksListMixin, HandbookOwnPermissionListMixin)


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


class RegionListView(HandbookListMixin, ListView):
    model = Region
    handbook_type = 'region'


class DistrictListView(HandbookListMixin, ListView):
    model = District
    handbook_type = 'district'


class LocalityListView(HandbookListMixin, ListView):
    model = Locality
    handbook_type = 'locality'


class LocalityDistrictListView(HandbookListMixin, ListView):
    model = LocalityDistrict
    handbook_type = 'localitydistrict'


class StreetListView(HandbookListMixin, ListView):
    model = Street
    handbook_type = 'street'


class ClientListView(HandbookOwnPermissionListMixin, ListView):
    model = Client
    handbook_type = 'client'


class WithdrawalReasonListView(HandbooksListMixin, ListView):
    handbook_type = 'withdrawalreason'


class ConditionListView(HandbooksListMixin, ListView):
    handbook_type = 'condition'


class MaterialListView(HandbooksListMixin, ListView):
    handbook_type = 'material'


class SeparationListView(HandbooksListMixin, ListView):
    handbook_type = 'separation'


class AgencyListView(HandbooksListMixin, ListView):
    handbook_type = 'agency'


class AgencySalesListView(HandbooksListMixin, ListView):
    handbook_type = 'agencysales'


class NewBuildingNameListView(HandbooksListMixin, ListView):
    handbook_type = 'newbuildingname'


class StairListView(HandbooksListMixin, ListView):
    handbook_type = 'stair'


class HeatingListView(HandbooksListMixin, ListView):
    handbook_type = 'heating'


class LayoutListView(HandbooksListMixin, ListView):
    handbook_type = 'layout'


class HouseTypeListView(HandbooksListMixin, ListView):
    handbook_type = 'housetype'


class FilialAgencyListView(HandbookListMixin, ListView):
    model = FilialAgency
    handbook_type = 'filialagency'


class FilialReportListView(HandbookListMixin, ListView):
    model = FilialReport
    handbook_type = 'filialreport'


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
