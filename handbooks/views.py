from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from handbooks.models import (Region, District, Locality, LocalityDistrict, Street,
                              Client, Handbook, FilialAgency, FilialReport)
from utils.const import CHOICES, HANDBOOKS_QUERYSET, BASE_CHOICES, SALE_CHOICES
from utils.mixins.mixins import (HandbookHistoryListMixin,
                                 FormHandbooksMixin, DeleteHandbooksMixin, HandbookListMixin,
                                 HandbooksListMixin, HandbookOwnPermissionListMixin, HandbookWithFilterListMixin)
from objects.services import has_any_perm_from_list, user_can_view_real_estate_list

def handbook_redirect(request, lang):
    # Функція, яка перебрасує користувача на довідник,
    # з яким він моєе взаємодіяти
    user = CustomUser.objects.filter(email=request.user).first()

    if user:
        for choice in BASE_CHOICES:
            cleaned_choice = ''.join(choice[1].split('_'))
            if (user.has_perm(f'handbooks.view_{cleaned_choice}')
                    or user.has_perm(f'handbooks.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/handbooks/base/{choice[1]}/', {'lang': lang})
            if (user.has_perm(f'objects.view_{cleaned_choice}')
                    or user.has_perm(f'objects.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/objects/base/{choice[1]}/', {'lang': lang})
        return render(request, '403.html', {'lang': lang})
    return redirect(reverse_lazy('accounts:login', kwargs={'lang': 'en'}))


def sale_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    if user:
        for choice in SALE_CHOICES:
            cleaned_choice = ''.join(choice[1].split('_'))
            if (user.has_perm(f'handbooks.view_{cleaned_choice}')
                    or user.has_perm(f'handbooks.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/handbooks/sale/{choice[1]}/', {'lang': lang})
            if (user.has_perm(f'objects.view_{cleaned_choice}')
                    or user.has_perm(f'objects.view_own_{cleaned_choice}')):
                return redirect(f'/{lang}/objects/sale/{choice[1]}/', {'lang': lang})
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context['object_list']:
            return context

        # у полях city_type і center_type замінюємо число на відповідний їм текст
        for index, obj in enumerate(context['object_values']):
            locality: Locality = context['object_list'][index]
            obj['city_type'] = locality.get_city_type_display()
            obj['center_type'] = locality.get_center_type_display()

        return context


class LocalityDistrictListView(HandbookListMixin, ListView):
    model = LocalityDistrict
    handbook_type = 'localitydistrict'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if not context['object_list']:
            return context

        # у полі new_building_district замінюємо число на відповідний йому текст
        for index, obj in enumerate(context['object_values']):
            locality_district: LocalityDistrict = context['object_list'][index]
            obj['new_building_district'] = locality_district.get_new_building_district_display()

        return context


class StreetListView(HandbookListMixin, ListView):
    model = Street
    handbook_type = 'street'


class ClientListView(HandbookOwnPermissionListMixin, HandbookWithFilterListMixin, ListView):
    model = Client
    template_name = "handbooks/client_list.html"
    handbook_type = 'client'
    filters = ['all', 'new', 'in_selection', 'with_show', 'decided', 'deferred_demand']
    queryset_filters = {'all': Client.objects.filter(on_delete=False),
                        'new': Client.objects.filter(date_of_add__gte=timezone.now()-relativedelta(months=1)).filter(on_delete=False),
                        'in_selection': Client.objects.filter(status=1).filter(on_delete=False),
                        'with_show': Client.objects.filter(status=2).filter(on_delete=False),
                        'decided': Client.objects.filter(status=3).filter(on_delete=False),
                        'deferred_demand': Client.objects.filter(status=4).filter(on_delete=False)}
    choices = SALE_CHOICES

    def get_queryset(self):
        return HandbookWithFilterListMixin.get_queryset(self).intersection(HandbookOwnPermissionListMixin.get_queryset(self))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context.update({
            "can_view_client": has_any_perm_from_list(
                self.request.user, "handbooks.view_client", "handbooks.view_own_client"
            ),
            "can_view_real_estate": user_can_view_real_estate_list(self.request.user),
            "can_view_report": self.request.user.has_perm("objects.view_report"),
            "can_view_contract": self.request.user.has_perm("objects.view_contract"),
            "can_update": {item.id: True for item in context["object_list"]},
            "can_view_history": {item.id: True for item in context["object_list"]},
        })
        return context


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


class ComplexListView(HandbooksListMixin, ListView):
    handbook_type = 'complex'


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
