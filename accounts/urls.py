from django.urls import path

from accounts.views import login_view, logout_view, ProfileView, users_list_redirect, UserListView, GroupListView, \
    HandbookUpdateView, HandbookCreateView, HandbookHistoryDetailView, HandbookDeleteView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('accounts/users_list_redirect/', users_list_redirect, name='users_list_redirect'),
    path('accounts/user/', UserListView.as_view(), name='user_list'),
    path('accounts/group/', GroupListView.as_view(), name='group_list'),

    path('base/history/<str:handbook_type>/<int:pk>/', HandbookHistoryDetailView.as_view(),
         name='handbook_history'),
    path('base/create/<str:handbook_type>/', HandbookCreateView.as_view(), name='create_handbook'),
    path('base/update/<str:handbook_type>/<int:pk>/', HandbookUpdateView.as_view(), name='update_handbook'),
    path('base/delete/<str:handbook_type>/<int:pk>/', HandbookDeleteView.as_view(), name='delete_handbook'),
]
