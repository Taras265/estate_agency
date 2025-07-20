from django.urls import path

from . import views
from .choices import RealEstateType

urlpatterns = [
    path(
        "verify-address/",
        views.verify_real_estate_address,
        name="verify_real_estate_address",
    ),
    path(
        "fill-address/", views.fill_real_estate_address, name="fill_real_estate_address"
    ),
    path(
        "set-status-sold/<int:id>",
        views.set_real_estate_status_sold,
        name="set_status_sold",
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
        "sale/real-estate/",
        views.RealEstateListRedirect.as_view(),
        name="real_estate_list_redirect",
    ),
    path("sale/apartments/", views.ApartmentListView.as_view(), name="apartment_list"),
    path("sale/commerces/", views.CommerceListView.as_view(), name="commerce_list"),
    path("sale/houses/", views.HouseListView.as_view(), name="house_list"),
    path("sale/land/", views.LandListView.as_view(), name="land_list"),

    path("sale/report/changes/", views.HistoryReportListView.as_view(), name="changes_report_list"),

    path("sale/apartments/reports/new/", views.NewApartmentReportListView.as_view(), name="new_apartment_reports"),
    path("sale/apartments/reports/all/", views.AllApartmentReportListView.as_view(), name="all_apartment_reports"),
    path("sale/apartments/reports/my/", views.MyApartmentReportListView.as_view(), name="my_apartment_reports"),
    path("sale/commerces/reports/new/", views.NewCommerceReportListView.as_view(), name="new_commerce_reports"),
    path("sale/houses/reports/new/", views.NewHouseReportListView.as_view(), name="new_house_reports"),

    path(
        "sale/apartments/contracts/",
        views.BaseContractListView.as_view(type=RealEstateType.APARTMENT),
        name="apartment_contracts",
    ),
    path(
        "sale/commerces/contracts/",
        views.BaseContractListView.as_view(type=RealEstateType.COMMERCE),
        name="commerce_contracts",
    ),
    path(
        "sale/houses/contracts/",
        views.BaseContractListView.as_view(type=RealEstateType.HOUSE),
        name="house_contracts",
    ),
    path(
        "office/apartments/",
        views.MyApartmentListView.as_view(),
        name="office_apartment_list",
    ),
    path(
        "office/commerces/",
        views.MyCommerceListView.as_view(),
        name="office_commerce_list",
    ),
    path("office/houses/", views.MyHouseListView.as_view(), name="office_house_list"),
    path("office/land/", views.MyLandListView.as_view(), name="office_land_list"),

    path("office/filial/apartments/", views.FilialApartmentListView.as_view(), name="office_filial_apartment_list"),
    path("office/filial/commerces/", views.FilialCommerceListView.as_view(), name="office_filial_commerce_list"),
    path("office/filial/houses/", views.FilialHouseListView.as_view(), name="office_filial_house_list"),
    path("office/filial/land/", views.FilialLandListView.as_view(), name="office_filial_land_list"),
    path("office/report/changes/", views.OfficeHistoryReportListView.as_view(), name="office_changes_report_list"),

    path("office/apartments/reports/new/", views.OfficeNewApartmentReportListView.as_view(), name="office_new_apartment_reports"),
    path("office/apartments/reports/all/", views.OfficeAllApartmentReportListView.as_view(), name="office_all_apartment_reports"),
    path("office/apartments/reports/my/", views.OfficeMyApartmentReportListView.as_view(), name="office_my_apartment_reports"),
    path("office/commerces/reports/new/", views.OfficeNewCommerceReportListView.as_view(), name="office_new_commerce_reports"),
    path("office/houses/reports/new/", views.OfficeNewHouseReportListView.as_view(), name="office_new_house_reports"),
    path("office/land/reports/new/", views.OfficeNewLandReportListView.as_view(), name="office_new_land_reports"),

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
    path("showing_act/pdf/", views.PdfView.as_view(), name="generate_pdf"),
    path(
        "base/selection/history/<int:pk>/",
        views.SelectionHistoryView.as_view(),
        name="selection_history",
    ),
]
