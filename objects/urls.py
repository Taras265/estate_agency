from django.urls import path
from objects.views import ApartmentListView, ApartmentCreateView, ApartmentUpdateView, ApartmentDeleteView, \
    CatalogListView, ApartmentDetailView, ObjectHistoryDetailView, PdfView, ReportListView, HistoryReportListView, \
    SelectionListView, ShowingActView, ContractListView

urlpatterns = [
    path('catalog/', CatalogListView.as_view(), name='catalog'),
    path('catalog/<int:pk>/', ApartmentDetailView.as_view(), name='apartment_detail'),

    path('sale/apartment/', ApartmentListView.as_view(), name='apartment_list'),
    path('sale/apartment/<str:filter>/', ApartmentListView.as_view(), name='apartment_list'),

    path('sale/report/changes/', HistoryReportListView.as_view(), name='changes_report_list'),
    path('sale/report/', ReportListView.as_view(), name='report_list'),
    path('sale/report/<str:filter>/', ReportListView.as_view(), name='report_list'),

    path('sale/contract/', ContractListView.as_view(), name='contract_list'),
    path('sale/contract/<str:filter>/', ContractListView.as_view(), name='contract_list'),

    path('base/create/', ApartmentCreateView.as_view(), name='create_apartment'),
    path('base/update/<int:pk>/', ApartmentUpdateView.as_view(), name='update_apartment'),
    path('base/delete/<int:pk>/', ApartmentDeleteView.as_view(), name='delete_apartment'),

    path('catalog/pdf/', PdfView.as_view(), name='generate_pdf'),

    path('base/history/<int:pk>/', ObjectHistoryDetailView.as_view(), name='history_apartment'),

    path('base/selection/<int:client_id>/', SelectionListView.as_view(), name='selection'),
    path('showing_act/', ShowingActView.as_view(), name='showing_act'),
]
