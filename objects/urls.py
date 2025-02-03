from django.urls import path
from objects.views import (
    RealEstateListRedirect, ApartmentListView, CommerceListView, HouseListView,
    ApartmentCreateView, CommerceCreateView, HouseCreateView,
    ApartmentUpdateView, CommerceUpdateView, HouseUpdateView,
    ApartmentDeleteView, CommerceDeleteView, HouseDeleteView,
    CatalogListView, ApartmentDetailView, ObjectHistoryDetailView,
    PdfView, ReportListView, HistoryReportListView,
    SelectionListView, ShowingActView, ContractListView,
    verify_real_estate_address, fill_real_estate_address,
)

urlpatterns = [
    path("verify-address/", verify_real_estate_address, name="verify_real_estate_address"),
    path("fill-address/", fill_real_estate_address, name="fill_real_estate_address"),
    path("catalog/", CatalogListView.as_view(), name="catalog"),
    path("catalog/<int:pk>/", ApartmentDetailView.as_view(), name="apartment_detail"),

    path("sale/real-estate/", RealEstateListRedirect.as_view(), name="real_estate_list_redirect"),
    path("sale/apartments/", ApartmentListView.as_view(), name="apartment_list"),
    path("sale/commerces/", CommerceListView.as_view(), name="commerce_list"),
    path("sale/houses/", HouseListView.as_view(), name="house_list"),

    path("sale/report/changes/", HistoryReportListView.as_view(), name="changes_report_list"),
    path("sale/report/", ReportListView.as_view(), name="report_list"),
    path("sale/report/<str:filter>/", ReportListView.as_view(), name="report_list"),

    path("sale/contract/", ContractListView.as_view(), name="contract_list"),
    path("sale/contract/<str:filter>/", ContractListView.as_view(), name="contract_list"),

    path("base/create/apartment/", ApartmentCreateView.as_view(), name="create_apartment"),
    path("base/create/commerce/", CommerceCreateView.as_view(), name="create_commerce"),
    path("base/create/house/", HouseCreateView.as_view(), name="create_house"),
    path("base/update/apartment/<int:pk>/", ApartmentUpdateView.as_view(), name="update_apartment"),
    path("base/update/commerce/<int:pk>/", CommerceUpdateView.as_view(), name="update_commerce"),
    path("base/update/house/<int:pk>/", HouseUpdateView.as_view(), name="update_house"),
    path("base/delete/apartment/<int:pk>/", ApartmentDeleteView.as_view(), name="delete_apartment"),
    path("base/delete/commerce/<int:pk>/", CommerceDeleteView.as_view(), name="delete_commerce"),
    path("base/delete/house/<int:pk>/", HouseDeleteView.as_view(), name="delete_house"),

    path("base/history/<int:pk>/", ObjectHistoryDetailView.as_view(), name="history_apartment"),

    path("base/selection/<int:client_id>/", SelectionListView.as_view(), name="selection"),
    path("showing_act/", ShowingActView.as_view(), name="showing_act"),
    path("showing_act/pdf/", PdfView.as_view(), name="generate_pdf"),
]
