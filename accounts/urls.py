from django.urls import path

from accounts.views import (
    GroupCreateView,
    GroupDeleteView,
    GroupHistoryView,
    GroupListView,
    GroupUpdateView,
    MyUserListView,
    ProfileView,
    UserCreateView,
    UserDeleteView,
    UserHistoryView,
    UserListView,
    UserUpdateView,
    login_view,
    logout_view,
    office_redirect,
    users_list_redirect,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("office/profile/", ProfileView.as_view(), name="profile"),
    path("office/", office_redirect, name="office"),
    path(
        "accounts/users_list_redirect/", users_list_redirect, name="users_list_redirect"
    ),
    path("accounts/user/", UserListView.as_view(), name="user_list"),
    path("office/user/", MyUserListView.as_view(), name="office_user_list"),
    path(
        "office/user/<int:group_id>/", MyUserListView.as_view(), name="office_user_list"
    ),
    path("accounts/group/", GroupListView.as_view(), name="group_list"),
    path("accounts/create/user/", UserCreateView.as_view(), name="user_create"),
    path("accounts/create/group/", GroupCreateView.as_view(), name="group_create"),
    path("accounts/update/user/<int:pk>/", UserUpdateView.as_view(), name="user_update"),
    path(
        "accounts/update/group/<int:pk>/", GroupUpdateView.as_view(), name="group_update"
    ),
    path("accounts/delete/user/<int:pk>/", UserDeleteView.as_view(), name="user_delete"),
    path(
        "accounts/delete/group/<int:pk>/", GroupDeleteView.as_view(), name="group_delete"
    ),
    path(
        "accounts/history/user/<int:pk>/", UserHistoryView.as_view(), name="user_history"
    ),
    path(
        "accounts/history/group/<int:pk>/",
        GroupHistoryView.as_view(),
        name="group_history",
    ),
]
