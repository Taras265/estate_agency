from django.urls import path
from images.views import ApartmentImageListView, ApartmentImageCreateView, ApartmentImageDeleteView

urlpatterns = [
    path('base/<int:pk>/', ApartmentImageListView.as_view(), name='apartment_images_list'),
    path('base/<int:pk>/add/', ApartmentImageCreateView.as_view(), name='apartment_image_add'),
    path('base/<int:pk>/delete/', ApartmentImageDeleteView.as_view(), name='apartment_image_delete'),
]
