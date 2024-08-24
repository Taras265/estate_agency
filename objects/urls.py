from django.urls import path
from objects.views import HandbookListView, ApartmentCreateView, ApartmentUpdateView, ApartmentDeleteView, \
    CatalogListView, ApartmentDetailView, ObjectHistoryDetailView

urlpatterns = [
    path('catalog/', CatalogListView.as_view(), name='catalog'),
    path('catalog/<int:pk>/', ApartmentDetailView.as_view(), name='apartment_detail'),
    path('base/apartment/', HandbookListView.as_view(), name='handbooks_list'),
    path('base/create/', ApartmentCreateView.as_view(), name='create_apartment'),
    path('base/update/<int:pk>/', ApartmentUpdateView.as_view(), name='update_apartment'),
    path('base/delete/<int:pk>/', ApartmentDeleteView.as_view(), name='delete_apartment'),

    path('base/history/<int:pk>/', ObjectHistoryDetailView.as_view(), name='history_apartment'),
]
