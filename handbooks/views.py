from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from accounts.models import CustomUser
from handbooks.forms import RegionForm, DistrictForm, LocalityForm, LocalityDistrictForm, StreetForm, ClientForm, \
    HandbookForm, FilialForm, FilialReportForm
from handbooks.models import (Region, District, Locality, LocalityDistrict,
                              Street, ObjectType, Client, Handbook, FilialAgency, FilialReport)
from utils.const import CHOICES, QUERYSET, HANDBOOKS_QUERYSET, LIST_BY_USER
from utils.mixins.mixins import FormMixin, DeleteMixin, SpecialRightFormMixin, SpecialRightDeleteMixin, \
    HandbookListMixin, HandbookHistoryListMixin
from django.utils.translation import gettext as _
from django.utils.translation import activate


def handbook_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    if user and user.user_type in CHOICES.keys():
        return redirect(f'/{lang}/handbook/base/{CHOICES[user.user_type][1][1]}/', {'lang': lang})
    return render(request, '403.html', {'lang': lang})


class HandbookListView(HandbookListMixin, ListView):
    handbook_type = None
    object_columns = None


class RegionCreateView(FormMixin, CreateView):
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictCreateView(FormMixin, CreateView):
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityCreateView(FormMixin, CreateView):
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictCreateView(FormMixin, CreateView):
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetCreateView(FormMixin, CreateView):
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientCreateView(FormMixin, CreateView):
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookCreateView(FormMixin, CreateView):
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            if self.kwargs['handbook_type'] == 'withdrawal_reason':
                kwargs['data']['type'] = 1
            elif self.kwargs['handbook_type'] == 'condition':
                kwargs['data']['type'] = 2
            elif self.kwargs['handbook_type'] == 'material':
                kwargs['data']['type'] = 3
            elif self.kwargs['handbook_type'] == 'separation':
                kwargs['data']['type'] = 4
            elif self.kwargs['handbook_type'] == 'agency':
                kwargs['data']['type'] = 5
            elif self.kwargs['handbook_type'] == 'agency_sales':
                kwargs['data']['type'] = 6
            elif self.kwargs['handbook_type'] == 'new_building_name':
                kwargs['data']['type'] = 7
            elif self.kwargs['handbook_type'] == 'stair':
                kwargs['data']['type'] = 8
            elif self.kwargs['handbook_type'] == 'heating':
                kwargs['data']['type'] = 9
            elif self.kwargs['handbook_type'] == 'layout':
                kwargs['data']['type'] = 10
            elif self.kwargs['handbook_type'] == 'house_type':
                kwargs['data']['type'] = 11
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyCreateView(FormMixin, CreateView):
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportCreateView(FormMixin, CreateView):
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class RegionUpdateView(FormMixin, UpdateView):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'

    def get_success_url(self):
        print(Region.objects.first())
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictUpdateView(FormMixin, UpdateView):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityUpdateView(FormMixin, UpdateView):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictUpdateView(FormMixin, UpdateView):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetUpdateView(FormMixin, UpdateView):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientUpdateView(SpecialRightFormMixin, UpdateView):
    queryset = Client.objects.filter(on_delete=False)
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'
    user_field = 'realtor'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookUpdateView(FormMixin, UpdateView):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            if self.kwargs['handbook_type'] == 'withdrawal_reason':
                kwargs['data']['type'] = 1
            elif self.kwargs['handbook_type'] == 'condition':
                kwargs['data']['type'] = 2
            elif self.kwargs['handbook_type'] == 'material':
                kwargs['data']['type'] = 3
            elif self.kwargs['handbook_type'] == 'separation':
                kwargs['data']['type'] = 4
            elif self.kwargs['handbook_type'] == 'agency':
                kwargs['data']['type'] = 5
            elif self.kwargs['handbook_type'] == 'agency_sales':
                kwargs['data']['type'] = 6
            elif self.kwargs['handbook_type'] == 'new_building_name':
                kwargs['data']['type'] = 7
            elif self.kwargs['handbook_type'] == 'stair':
                kwargs['data']['type'] = 8
            elif self.kwargs['handbook_type'] == 'heating':
                kwargs['data']['type'] = 9
            elif self.kwargs['handbook_type'] == 'layout':
                kwargs['data']['type'] = 10
            elif self.kwargs['handbook_type'] == 'house_type':
                kwargs['data']['type'] = 11
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyUpdateView(FormMixin, UpdateView):
    queryset = FilialAgency.objects.filter(on_delete=False)
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportUpdateView(FormMixin, UpdateView):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class RegionDeleteView(DeleteMixin, DeleteView):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictDeleteView(DeleteMixin, DeleteView):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityDeleteView(DeleteMixin, DeleteView):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictDeleteView(DeleteMixin, DeleteView):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetDeleteView(DeleteMixin, DeleteView):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientDeleteView(SpecialRightDeleteMixin, DeleteView):
    queryset = Client.objects.filter(on_delete=False)
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'
    user_field = 'realtor'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookDeleteView(DeleteMixin, DeleteView):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            if self.kwargs['handbook_type'] == 'withdrawal_reason':
                kwargs['data']['type'] = 1
            elif self.kwargs['handbook_type'] == 'condition':
                kwargs['data']['type'] = 2
            elif self.kwargs['handbook_type'] == 'material':
                kwargs['data']['type'] = 3
            elif self.kwargs['handbook_type'] == 'separation':
                kwargs['data']['type'] = 4
            elif self.kwargs['handbook_type'] == 'agency':
                kwargs['data']['type'] = 5
            elif self.kwargs['handbook_type'] == 'agency_sales':
                kwargs['data']['type'] = 6
            elif self.kwargs['handbook_type'] == 'new_building_name':
                kwargs['data']['type'] = 7
            elif self.kwargs['handbook_type'] == 'stair':
                kwargs['data']['type'] = 8
            elif self.kwargs['handbook_type'] == 'heating':
                kwargs['data']['type'] = 9
            elif self.kwargs['handbook_type'] == 'layout':
                kwargs['data']['type'] = 10
            elif self.kwargs['handbook_type'] == 'house_type':
                kwargs['data']['type'] = 11
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyDeleteView(DeleteMixin, DeleteView):
    queryset = FilialAgency.objects.filter(on_delete=False)
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportDeleteView(DeleteMixin, DeleteView):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class HandbookHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = None
