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
from utils.const import CHOICES, MODEL, HANDBOOKS_QUERYSET, LIST_BY_USER, PERMISSION, OBJECT_COLUMNS
from utils.mixins.mixins import FormMixin, DeleteMixin, \
    HandbookHistoryListMixin, CustomLoginRequiredMixin, HandbookListPermissionMixin
from django.utils.translation import gettext as _
from django.utils.translation import activate


def handbook_redirect(request, lang):
    user = CustomUser.objects.filter(email=request.user).first()

    if user and user.user_type in CHOICES.keys():
        return redirect(f'/{lang}/handbook/base/{CHOICES[user.user_type][1][1]}/', {'lang': lang})
    return render(request, '403.html', {'lang': lang})


class HandbookListView(HandbookListPermissionMixin, ListView):
    handbook_type = None


class RegionCreateView(FormMixin, CreateView):
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'
    permission_required = 'handbooks.add_region'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictCreateView(FormMixin, CreateView):
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'
    permission_required = 'handbooks.add_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityCreateView(FormMixin, CreateView):
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'
    permission_required = 'handbooks.add_locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictCreateView(FormMixin, CreateView):
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'
    permission_required = 'handbooks.add_localitydistrict'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetCreateView(FormMixin, CreateView):
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'
    permission_required = 'handbooks.add_street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientCreateView(FormMixin, CreateView):
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'
    permission_required = 'handbooks.add_client'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookCreateView(FormMixin, CreateView):
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_permission_required(self):
        handbook_type = self.kwargs.get('handbook_type')
        self.permission_required = PERMISSION[handbook_type]
        return super().get_permission_required()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyCreateView(FormMixin, CreateView):
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'
    permission_required = 'handbooks.add_filialagency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportCreateView(FormMixin, CreateView):
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'
    permission_required = 'handbooks.add_filialreport'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class RegionUpdateView(FormMixin, UpdateView):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'
    permission_required = 'handbooks.change_region'

    def get_success_url(self):
        print(Region.objects.first())
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictUpdateView(FormMixin, UpdateView):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'
    permission_required = 'handbooks.change_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityUpdateView(FormMixin, UpdateView):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'
    permission_required = 'handbooks.change_locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictUpdateView(FormMixin, UpdateView):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'
    permission_required = 'handbooks.change_localitydistrict'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetUpdateView(FormMixin, UpdateView):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'
    permission_required = 'handbooks.change_street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientUpdateView(FormMixin, UpdateView):
    queryset = Client.objects.filter(on_delete=False)
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'
    permission_required = 'handbooks.change_client'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookUpdateView(FormMixin, UpdateView):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_permission_required(self):
        handbook_type = self.kwargs.get('handbook_type')
        self.permission_required = PERMISSION[handbook_type]
        return super().get_permission_required()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyUpdateView(FormMixin, UpdateView):
    queryset = FilialAgency.objects.filter(on_delete=False)
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'
    permission_required = 'handbooks.change_filialagency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportUpdateView(FormMixin, UpdateView):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'
    permission_required = 'handbooks.change_filialreport'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class RegionDeleteView(DeleteMixin, DeleteView):
    queryset = Region.objects.filter(on_delete=False)
    form_class = RegionForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'region'
    permission_required = 'handbooks.change_region'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "region"})


class DistrictDeleteView(DeleteMixin, DeleteView):
    queryset = District.objects.filter(on_delete=False)
    form_class = DistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'district'
    permission_required = 'handbooks.change_district'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "district"})


class LocalityDeleteView(DeleteMixin, DeleteView):
    queryset = Locality.objects.filter(on_delete=False)
    form_class = LocalityForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality'
    permission_required = 'handbooks.change_locality'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality"})


class LocalityDistrictDeleteView(DeleteMixin, DeleteView):
    queryset = LocalityDistrict.objects.filter(on_delete=False)
    form_class = LocalityDistrictForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'locality_district'
    permission_required = 'handbooks.change_localitydistrict'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "locality_district"})


class StreetDeleteView(DeleteMixin, DeleteView):
    queryset = Street.objects.filter(on_delete=False)
    form_class = StreetForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'street'
    permission_required = 'handbooks.change_street'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "street"})


class ClientDeleteView(DeleteMixin, DeleteView):
    queryset = Client.objects.filter(on_delete=False)
    form_class = ClientForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'client'
    permission_required = 'handbooks.change_client'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "client"})


class HandbookDeleteView(DeleteMixin, DeleteView):
    queryset = Handbook.objects.filter(on_delete=False)
    form_class = HandbookForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    def get_permission_required(self):
        handbook_type = self.kwargs.get('handbook_type')
        self.permission_required = PERMISSION[handbook_type]
        return super().get_permission_required()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get('data'):
            kwargs['data']._mutable = True
            kwargs['data']['type'] = HANDBOOKS_QUERYSET[self.kwargs['handbook_type']]
        return kwargs

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": self.kwargs['handbook_type']})


class FilialAgencyDeleteView(DeleteMixin, DeleteView):
    queryset = FilialAgency.objects.filter(on_delete=False)
    form_class = FilialForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_agency'
    permission_required = 'handbooks.change_filialagency'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_agency"})


class FilialReportDeleteView(DeleteMixin, DeleteView):
    queryset = FilialReport.objects.filter(on_delete=False)
    form_class = FilialReportForm
    success_url = reverse_lazy("handbooks:handbooks_list")

    choice_name = 'filial_report'
    permission_required = 'handbooks.change_filialreport'

    def get_success_url(self):
        return reverse_lazy("handbooks:handbooks_list", kwargs={"lang": self.kwargs['lang'],
                                                                "handbook_type": "filial_report"})


class HandbookHistoryDetailView(HandbookHistoryListMixin, DetailView):
    context_object_name = 'object'

    handbook_type = None
