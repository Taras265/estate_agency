from django.urls import path
from handbooks.views import (HandbookUpdateView, HandbookDeleteView,
                             HandbookHistoryDetailView, handbook_redirect, HandbookCreateView,
                             RegionListView, DistrictListView, LocalityListView,
                             LocalityDistrictListView, StreetListView,
                             ClientListView, WithdrawalReasonListView, ConditionListView,
                             MaterialListView, SeparationListView, AgencyListView,
                             AgencySalesListView, NewBuildingNameListView, StairListView,
                             HeatingListView, LayoutListView, HouseTypeListView, FilialAgencyListView,
                             FilialReportListView)

urlpatterns = [
    path('base/', handbook_redirect, name='handbook_redirect'),

    path('base/region/', RegionListView.as_view(), name='region_list'),
    path('base/district/', DistrictListView.as_view(), name='district_list'),
    path('base/locality/', LocalityListView.as_view(), name='locality_list'),
    path('base/localitydistrict/', LocalityDistrictListView.as_view(), name='localitydistrict_list'),
    path('base/street/', StreetListView.as_view(), name='street_list'),
    path('base/client/', ClientListView.as_view(), name='client_list'),
    path('base/client/<str:filter>/', ClientListView.as_view(), name='client_list'),
    path('base/withdrawalreason/', WithdrawalReasonListView.as_view(), name='withdrawalreason_list'),
    path('base/condition/', ConditionListView.as_view(), name='condition_list'),
    path('base/material/', MaterialListView.as_view(), name='material_list'),
    path('base/separation/', SeparationListView.as_view(), name='separation_list'),
    path('base/agency/', AgencyListView.as_view(), name='agency_list'),
    path('base/agencysales/', AgencySalesListView.as_view(), name='agencysales_list'),
    path('base/newbuildingname/', NewBuildingNameListView.as_view(), name='newbuildingname_list'),
    path('base/stair/', StairListView.as_view(), name='stair_list'),
    path('base/heating/', HeatingListView.as_view(), name='heating_list'),
    path('base/layout/', LayoutListView.as_view(), name='layout_list'),
    path('base/housetype/', HouseTypeListView.as_view(), name='housetype_list'),
    path('base/filialagency/', FilialAgencyListView.as_view(), name='filialagency_list'),
    path('base/filialreport/', FilialReportListView.as_view(), name='filialreport_list'),

    path('base/create/<str:handbook_type>/', HandbookCreateView.as_view(), name='create_handbook'),

    path('base/update/<str:handbook_type>/<int:pk>/', HandbookUpdateView.as_view(), name='update_handbook'),

    path('base/delete/<str:handbook_type>/<int:pk>/', HandbookDeleteView.as_view(), name='delete_handbook'),

    path('base/history/<str:handbook_type>/<int:pk>/', HandbookHistoryDetailView.as_view(), name='handbook_history'),
]
