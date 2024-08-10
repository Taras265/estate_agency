from django.urls import path
from handbooks.views import (HandbookListView, RegionCreateView, LocalityCreateView, DistrictCreateView,
                             LocalityDistrictCreateView, StreetCreateView, ClientCreateView, FilialAgencyCreateView,
                             FilialReportCreateView, HandbookCreateView, RegionUpdateView, DistrictUpdateView,
                             LocalityUpdateView, LocalityDistrictUpdateView, StreetUpdateView, ClientUpdateView,
                             FilialAgencyUpdateView, FilialReportUpdateView, HandbookUpdateView, RegionDeleteView,
                             DistrictDeleteView, LocalityDeleteView, LocalityDistrictDeleteView, StreetDeleteView,
                             ClientDeleteView, FilialAgencyDeleteView, FilialReportDeleteView, HandbookDeleteView,
                             HandbookHistoryDetailView
                             )

urlpatterns = [
    path('base/<str:handbook_type>/', HandbookListView.as_view(), name='handbooks_list'),
    path('base/create/region/', RegionCreateView.as_view(), name='create_region'),
    path('base/create/district/', DistrictCreateView.as_view(), name='create_district'),
    path('base/create/locality/', LocalityCreateView.as_view(), name='create_locality'),
    path('base/create/locality_district/', LocalityDistrictCreateView.as_view(), name='create_locality_district'),
    path('base/create/street/', StreetCreateView.as_view(), name='create_street'),
    path('base/create/client/', ClientCreateView.as_view(), name='create_client'),
    path('base/create/filial_agency/', FilialAgencyCreateView.as_view(), name='create_filial_agency'),
    path('base/create/filial_report/', FilialReportCreateView.as_view(), name='create_filial_report'),

    path('base/create/<str:handbook_type>/', HandbookCreateView.as_view(), name='create_handbook'),

    path('base/update/region/<int:pk>/', RegionUpdateView.as_view(), name='update_region'),
    path('base/update/district/<int:pk>/', DistrictUpdateView.as_view(), name='update_district'),
    path('base/update/locality/<int:pk>/', LocalityUpdateView.as_view(), name='update_locality'),
    path('base/update/locality_district/<int:pk>/', LocalityDistrictUpdateView.as_view(), name='update_locality_district'),
    path('base/update/street/<int:pk>/', StreetUpdateView.as_view(), name='update_street'),
    path('base/update/client/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),
    path('base/update/filial_agency/<int:pk>/', FilialAgencyUpdateView.as_view(), name='update_filial_agency'),
    path('base/update/filial_report/<int:pk>/', FilialReportUpdateView.as_view(), name='update_filial_report'),

    path('base/update/<str:handbook_type>/<int:pk>/', HandbookUpdateView.as_view(), name='update_handbook'),

    path('base/delete/region/<int:pk>/', RegionDeleteView.as_view(), name='delete_region'),
    path('base/delete/district/<int:pk>/', DistrictDeleteView.as_view(), name='delete_district'),
    path('base/delete/locality/<int:pk>/', LocalityDeleteView.as_view(), name='delete_locality'),
    path('base/delete/locality_district/<int:pk>/', LocalityDistrictDeleteView.as_view(),
         name='delete_locality_district'),
    path('base/delete/street/<int:pk>/', StreetDeleteView.as_view(), name='delete_street'),
    path('base/delete/client/<int:pk>/', ClientDeleteView.as_view(), name='delete_client'),
    path('base/delete/filial_agency/<int:pk>/', FilialAgencyDeleteView.as_view(), name='delete_filial_agency'),
    path('base/delete/filial_report/<int:pk>/', FilialReportDeleteView.as_view(), name='delete_filial_report'),

    path('base/delete/<str:handbook_type>/<int:pk>/', HandbookDeleteView.as_view(), name='delete_handbook'),

    path('base/history/<str:handbook_type>/<int:pk>/', HandbookHistoryDetailView.as_view(), name='handbook_history'),
]
