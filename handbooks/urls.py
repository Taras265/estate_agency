from django.urls import path

from handbooks import views


urlpatterns = [
    path("sale/", views.sale_redirect, name="sale_redirect"),

    path("base/region/", views.RegionListView.as_view(), name="region_list"),
    path("base/district/", views.DistrictListView.as_view(), name="district_list"),
    path("base/locality/", views.LocalityListView.as_view(), name="locality_list"),
    path(
        "base/localitydistrict/",
        views.LocalityDistrictListView.as_view(),
        name="localitydistrict_list",
    ),
    path("base/street/", views.StreetListView.as_view(), name="street_list"),
    path(
        "base/withdrawalreason/",
        views.WithdrawalReasonListView.as_view(),
        name="withdrawalreason_list",
    ),
    path("base/condition/", views.ConditionListView.as_view(), name="condition_list"),
    path("base/material/", views.MaterialListView.as_view(), name="material_list"),
    path("base/separation/", views.SeparationListView.as_view(), name="separation_list"),
    path("base/agency/", views.AgencyListView.as_view(), name="agency_list"),
    path("base/agencysales/", views.AgencySalesListView.as_view(), name="agencysales_list"),
    path(
        "base/newbuildingname/",
        views.NewBuildingNameListView.as_view(),
        name="newbuildingname_list",
    ),
    path("base/stair/", views.StairListView.as_view(), name="stair_list"),
    path("base/heating/", views.HeatingListView.as_view(), name="heating_list"),
    path("base/layout/", views.LayoutListView.as_view(), name="layout_list"),
    path("base/housetype/", views.HouseTypeListView.as_view(), name="housetype_list"),
    path("base/complex/", views.ComplexListView.as_view(), name="complex_list"),
    path("base/filialagency/", views.FilialAgencyListView.as_view(), name="filialagency_list"),
    path("base/filialreport/", views.FilialReportListView.as_view(), name="filialreport_list"),
    path("base/create/region/", views.RegionCreateView.as_view(), name="region_create"),
    path("base/create/district/", views.DistrictCreateView.as_view(), name="district_create"),
    path("base/create/locality/", views.LocalityCreateView.as_view(), name="locality_create"),
    path(
        "base/create/localitydistrict/",
        views.LocalityDistrictCreateView.as_view(),
        name="localitydistrict_create",
    ),
    path("base/create/street/", views.StreetCreateView.as_view(), name="street_create"),
    path(
        "base/create/withdrawalreason/",
        views.WithdrawalReasonCreateView.as_view(),
        name="withdrawalreason_create",
    ),
    path(
        "base/create/condition/", views.ConditionCreateView.as_view(), name="condition_create"
    ),
    path("base/create/material/", views.MaterialCreateView.as_view(), name="material_create"),
    path(
        "base/create/separation/",
        views.SeparationCreateView.as_view(),
        name="separation_create",
    ),
    path("base/create/agency/", views.AgencyCreateView.as_view(), name="agency_create"),
    path(
        "base/create/agencysales/",
        views.AgencySalesCreateView.as_view(),
        name="agencysales_create",
    ),
    path(
        "base/create/newbuildingname/",
        views.NewBuildingNameCreateView.as_view(),
        name="newbuildingname_create",
    ),
    path("base/create/stair/", views.StairCreateView.as_view(), name="stair_create"),
    path("base/create/heating/", views.HeatingCreateView.as_view(), name="heating_create"),
    path("base/create/layout/", views.LayoutCreateView.as_view(), name="layout_create"),
    path(
        "base/create/housetype/", views.HouseTypeCreateView.as_view(), name="housetype_create"
    ),
    path("base/create/complex/", views.ComplexCreateView.as_view(), name="complex_create"),
    path(
        "base/create/filialagency/",
        views.FilialAgencyCreateView.as_view(),
        name="filialagency_create",
    ),
    path(
        "base/create/filialreport/",
        views.FilialReportCreateView.as_view(),
        name="filialreport_create",
    ),
    path(
        "base/update/region/<int:pk>/", views.RegionUpdateView.as_view(), name="region_update"
    ),
    path(
        "base/update/district/<int:pk>/",
        views.DistrictUpdateView.as_view(),
        name="district_update",
    ),
    path(
        "base/update/locality/<int:pk>/",
        views.LocalityUpdateView.as_view(),
        name="locality_update",
    ),
    path(
        "base/update/localitydistrict/<int:pk>/",
        views.LocalityDistrictUpdateView.as_view(),
        name="localitydistrict_update",
    ),
    path(
        "base/update/street/<int:pk>/", views.StreetUpdateView.as_view(), name="street_update"
    ),
    path(
        "base/update/withdrawalreason/<int:pk>/",
        views.WithdrawalReasonUpdateView.as_view(),
        name="withdrawalreason_update",
    ),
    path(
        "base/update/condition/<int:pk>/",
        views.ConditionUpdateView.as_view(),
        name="condition_update",
    ),
    path(
        "base/update/material/<int:pk>/",
        views.MaterialUpdateView.as_view(),
        name="material_update",
    ),
    path(
        "base/update/separation/<int:pk>/",
        views.SeparationUpdateView.as_view(),
        name="separation_update",
    ),
    path(
        "base/update/agency/<int:pk>/", views.AgencyUpdateView.as_view(), name="agency_update"
    ),
    path(
        "base/update/agencysales/<int:pk>/",
        views.AgencySalesUpdateView.as_view(),
        name="agencysales_update",
    ),
    path(
        "base/update/newbuildingname/<int:pk>/",
        views.NewBuildingNameUpdateView.as_view(),
        name="newbuildingname_update",
    ),
    path("base/update/stair/<int:pk>/", views.StairUpdateView.as_view(), name="stair_update"),
    path(
        "base/update/heating/<int:pk>/",
        views.HeatingUpdateView.as_view(),
        name="heating_update",
    ),
    path(
        "base/update/layout/<int:pk>/", views.LayoutUpdateView.as_view(), name="layout_update"
    ),
    path(
        "base/update/housetype/<int:pk>/",
        views.HouseTypeUpdateView.as_view(),
        name="housetype_update",
    ),
    path(
        "base/update/complex/<int:pk>/",
        views.ComplexUpdateView.as_view(),
        name="complex_update",
    ),
    path(
        "base/update/filialagency/<int:pk>/",
        views.FilialAgencyUpdateView.as_view(),
        name="filialagency_update",
    ),
    path(
        "base/update/filialreport/<int:pk>/",
        views.FilialReportUpdateView.as_view(),
        name="filialreport_update",
    ),
    path(
        "base/delete/region/<int:pk>/", views.RegionDeleteView.as_view(), name="region_delete"
    ),
    path(
        "base/delete/district/<int:pk>/",
        views.DistrictDeleteView.as_view(),
        name="district_delete",
    ),
    path(
        "base/delete/locality/<int:pk>/",
        views.LocalityDeleteView.as_view(),
        name="locality_delete",
    ),
    path(
        "base/delete/localitydistrict/<int:pk>/",
        views.LocalityDistrictDeleteView.as_view(),
        name="localitydistrict_delete",
    ),
    path(
        "base/delete/street/<int:pk>/", views.StreetDeleteView.as_view(), name="street_delete"
    ),
    path(
        "base/delete/withdrawalreason/<int:pk>/",
        views.WithdrawalReasonDeleteView.as_view(),
        name="withdrawalreason_delete",
    ),
    path(
        "base/delete/condition/<int:pk>/",
        views.ConditionDeleteView.as_view(),
        name="condition_delete",
    ),
    path(
        "base/delete/material/<int:pk>/",
        views.MaterialDeleteView.as_view(),
        name="material_delete",
    ),
    path(
        "base/delete/separation/<int:pk>/",
        views.SeparationDeleteView.as_view(),
        name="separation_delete",
    ),
    path(
        "base/delete/agency/<int:pk>/", views.AgencyDeleteView.as_view(), name="agency_delete"
    ),
    path(
        "base/delete/agencysales/<int:pk>/",
        views.AgencySalesDeleteView.as_view(),
        name="agencysales_delete",
    ),
    path(
        "base/delete/newbuildingname/<int:pk>/",
        views.NewBuildingNameDeleteView.as_view(),
        name="newbuildingname_delete",
    ),
    path("base/delete/stair/<int:pk>/", views.StairDeleteView.as_view(), name="stair_delete"),
    path(
        "base/delete/heating/<int:pk>/",
        views.HeatingDeleteView.as_view(),
        name="heating_delete",
    ),
    path(
        "base/delete/layout/<int:pk>/", views.LayoutDeleteView.as_view(), name="layout_delete"
    ),
    path(
        "base/delete/housetype/<int:pk>/",
        views.HouseTypeDeleteView.as_view(),
        name="housetype_delete",
    ),
    path(
        "base/delete/complex/<int:pk>/",
        views.ComplexDeleteView.as_view(),
        name="complex_delete",
    ),
    path(
        "base/delete/filialagency/<int:pk>/",
        views.FilialAgencyDeleteView.as_view(),
        name="filialagency_delete",
    ),
    path(
        "base/delete/filialreport/<int:pk>/",
        views.FilialReportDeleteView.as_view(),
        name="filialreport_delete",
    ),
    path(
        "base/history/region/<int:pk>/",
        views.RegionHistoryView.as_view(),
        name="region_history",
    ),
    path(
        "base/history/district/<int:pk>/",
        views.DistrictHistoryView.as_view(),
        name="district_history",
    ),
    path(
        "base/history/locality/<int:pk>/",
        views.LocalityHistoryView.as_view(),
        name="locality_history",
    ),
    path(
        "base/history/localitydistrict/<int:pk>/",
        views.LocalityDistrictHistoryView.as_view(),
        name="localitydistrict_history",
    ),
    path(
        "base/history/street/<int:pk>/",
        views.StreetHistoryView.as_view(),
        name="street_history",
    ),
    path(
        "base/history/withdrawalreason/<int:pk>/",
        views.WithdrawalReasonHistoryView.as_view(),
        name="withdrawalreason_history",
    ),
    path(
        "base/history/condition/<int:pk>/",
        views.ConditionHistoryView.as_view(),
        name="condition_history",
    ),
    path(
        "base/history/material/<int:pk>/",
        views.MaterialHistoryView.as_view(),
        name="material_history",
    ),
    path(
        "base/history/separation/<int:pk>/",
        views.SeparationHistoryView.as_view(),
        name="separation_history",
    ),
    path(
        "base/history/agency/<int:pk>/",
        views.AgencyHistoryView.as_view(),
        name="agency_history",
    ),
    path(
        "base/history/agencysales/<int:pk>/",
        views.AgencySalesHistoryView.as_view(),
        name="agencysales_history",
    ),
    path(
        "base/history/newbuildingname/<int:pk>/",
        views.NewBuildingNameHistoryView.as_view(),
        name="newbuildingname_history",
    ),
    path(
        "base/history/stair/<int:pk>/", views.StairHistoryView.as_view(), name="stair_history"
    ),
    path(
        "base/history/heating/<int:pk>/",
        views.HeatingHistoryView.as_view(),
        name="heating_history",
    ),
    path(
        "base/history/layout/<int:pk>/",
        views.LayoutHistoryView.as_view(),
        name="layout_history",
    ),
    path(
        "base/history/housetype/<int:pk>/",
        views.HouseTypeHistoryView.as_view(),
        name="housetype_history",
    ),
    path(
        "base/history/complex/<int:pk>/",
        views.ComplexHistoryView.as_view(),
        name="complex_history",
    ),
    path(
        "base/history/filialagency/<int:pk>/",
        views.FilialAgencyHistoryView.as_view(),
        name="filialagency_history",
    ),
    path(
        "base/history/filialreport/<int:pk>/",
        views.FilialReportHistoryView.as_view(),
        name="filialreport_history",
    ),
    path("load_filials/", views.load_filials, name="load_filials"),
    path("load_locality_districts/", views.load_locality_districts, name="load_locality_districts"),
    path("load_streets/", views.load_streets, name="load_streets"),
]
