from django.urls import path
from . import views


urlpatterns = [
    path("sale/client/all/", views.ClientListView.as_view(), name="all_client_list"),
    path("sale/client/new/", views.NewClientListView.as_view(), name="new_client_list"),
    path(
        "sale/client/in_selection/",
        views.InSelectionClientListView.as_view(),
        name="in_selection_client_list",
    ),
    path(
        "sale/client/with_show/",
        views.WithShowClientListView.as_view(),
        name="with_show_client_list",
    ),
    path(
        "sale/client/decided/",
        views.DecidedClientListView.as_view(),
        name="decided_client_list",
    ),
    path(
        "sale/client/deferred_demand/",
        views.DeferredDemandClientListView.as_view(),
        name="deferred_demand_client_list",
    ),

    path("sale/create/client/", views.ClientCreateView.as_view(), name="client_create"),
    path(
        "sale/update/client/<int:pk>/", views.ClientUpdateView.as_view(), name="client_update"
    ),
    path(
        "sale/delete/client/<int:pk>/", views.ClientDeleteView.as_view(), name="client_delete"
    ),
    path(
        "sale/history/client/<int:pk>/",
        views.ClientHistoryView.as_view(),
        name="client_history",
    ),

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