from django.urls import path
from handbooks.views import (HandbookListView, HandbookUpdateView, HandbookDeleteView,
                             HandbookHistoryDetailView, handbook_redirect, HandbookCreateView)

urlpatterns = [
    path('base/', handbook_redirect, name='handbook_redirect'),

    path('base/<str:handbook_type>/', HandbookListView.as_view(), name='handbooks_list'),

    path('base/create/<str:handbook_type>/', HandbookCreateView.as_view(), name='create_handbook'),

    path('base/update/<str:handbook_type>/<int:pk>/', HandbookUpdateView.as_view(), name='update_handbook'),

    path('base/delete/<str:handbook_type>/<int:pk>/', HandbookDeleteView.as_view(), name='delete_handbook'),

    path('base/history/<str:handbook_type>/<int:pk>/', HandbookHistoryDetailView.as_view(), name='handbook_history'),
]
