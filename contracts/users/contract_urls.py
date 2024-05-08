from django.urls import path

from .contract_views import (
    ContractListView,
    ContractCreateView,
    ContractDetailView,
    PermissionRequestCreateView,
    PermissionRequestListView,
    PermissionRequestDoneView,
)

app_name = "contracts"

urlpatterns = [
    path("", ContractListView.as_view(), name="contract-list"),
    path(
        "permission-requests/",
        PermissionRequestListView.as_view(),
        name="permission-request-list",
    ),
    path("add/", ContractCreateView.as_view(), name="contract-add"),
    path(
        "permission-request-add/<int:pk>/",
        PermissionRequestCreateView.as_view(),
        name="permission-request-add",
    ),
    path(
        "permission-request-done/<int:pk>/",
        PermissionRequestDoneView.as_view(),
        name="permission-request-done",
    ),
    path("<int:pk>/", ContractDetailView.as_view(), name="contract-detail"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]
