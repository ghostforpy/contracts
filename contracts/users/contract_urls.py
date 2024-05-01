from django.urls import path

from .contract_views import ContractListView, ContractCreateView, ContractDetailView

app_name = "contracts"

urlpatterns = [
    path("", ContractListView.as_view(), name="contract-list"),
    path("add/", ContractCreateView.as_view(), name="contract-add"),
    path("<int:pk>/", ContractDetailView.as_view(), name="contract-detail"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]
