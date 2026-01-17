from django.urls import path

from . import views


urlpatterns = [
    path(
        "verify-address/",
        views.verify_real_estate_address,
        name="verify_real_estate_address",
    ),
    path(
        "fill-address/", views.fill_real_estate_address, name="fill_real_estate_address"
    ),
    path("catalog/", views.CatalogListView.as_view(), name="catalog"),
    path(
        "catalog/apartments/<int:pk>/",
        views.ApartmentDetailView.as_view(),
        name="apartment_detail",
    ),
    path(
        "catalog/commerces/<int:pk>/",
        views.CommerceDetailView.as_view(),
        name="commerce_detail",
    ),
    path(
        "catalog/houses/<int:pk>/", views.HouseDetailView.as_view(), name="house_detail"
    ),
    path(
        "catalog/lands/<int:pk>/", views.LandDetailView.as_view(), name="land_detail"
    ),
    path("sale/apartments/", views.AccessibleApartmentListView.as_view(), name="apartment_list"),
    path("sale/commerces/", views.AccessibleCommerceListView.as_view(), name="commerce_list"),
    path("sale/houses/", views.AccessibleHouseListView.as_view(), name="house_list"),
    path("sale/lands/", views.AccessibleLandListView.as_view(), name="land_list"),

    path("sale/report/changes/", views.HistoryReportListView.as_view(), name="changes_report_list"),

    path("base/create/apartment/", views.ApartmentCreateView.as_view(), name="create_apartment"),
    path("base/create/commerce/", views.CommerceCreateView.as_view(), name="create_commerce"),
    path("base/create/house/", views.HouseCreateView.as_view(), name="create_house"),
    path("base/create/land/", views.LandCreateView.as_view(), name="create_land"),

    path("base/update/apartment/<int:pk>/", views.ApartmentUpdateView.as_view(), name="update_apartment"),
    path("base/update/commerce/<int:pk>/", views.CommerceUpdateView.as_view(), name="update_commerce"),
    path("base/update/house/<int:pk>/", views.HouseUpdateView.as_view(), name="update_house"),
    path("base/update/land/<int:pk>/", views.LandUpdateView.as_view(), name="update_land"),

    path("base/delete/apartment/<int:pk>/", views.ApartmentDeleteView.as_view(), name="delete_apartment"),
    path("base/delete/commerce/<int:pk>/", views.CommerceDeleteView.as_view(), name="delete_commerce"),
    path("base/delete/house/<int:pk>/", views.HouseDeleteView.as_view(), name="delete_house"),
    path("base/delete/land/<int:pk>/", views.LandDeleteView.as_view(), name="delete_land"),

    path("base/history/apartment/<int:pk>/", views.ApartmentHistoryView.as_view(), name="history_apartment"),
    path("base/history/commerce/<int:pk>/", views.CommerceHistoryView.as_view(), name="history_commerce"),
    path("base/history/house/<int:pk>/", views.HouseHistoryView.as_view(), name="history_house"),
    path("base/history/land/<int:pk>/", views.LandHistoryView.as_view(), name="history_land"),

    path("base/selection/<int:client_id>/", views.SelectionListView.as_view(), name="selection"),

    path("pre/showing_act/", views.showing_act_redirect, name="showing_act_redirect"),
    path("showing_act/", views.ShowingActView.as_view(), name="showing_act"),
    path("pre/showing_act/pdf/", views.pdf_redirect, name="generate_pdf_redirect"),
    path("showing_act/pdf/", views.ShowingActPDFView.as_view(), name="generate_pdf"),
    path(
        "base/selection/history/<int:pk>/",
        views.SelectionHistoryView.as_view(),
        name="selection_history",
    ),
]
