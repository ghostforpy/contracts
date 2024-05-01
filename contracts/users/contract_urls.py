from django.urls import path

from .contract_views import ContractListView, ContractCreateView

app_name = "contracts"

urlpatterns = [
    path("", ContractListView.as_view(), name="contract-list"),
    path("add/", ContractCreateView.as_view(), name="contract-add"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]
