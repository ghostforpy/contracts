from typing import Any
from datetime import datetime
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect

from django.utils.timezone import now
from .forms import ContarctFilterForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
    # TemplateView,
)

# from django.views.generic.list import BaseListView

from .models import Contract, UserContractFolders, PermissionRequest

# Topic views


class ContractListView(ListView):
    model = Contract
    # template_name = "themes/index.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "contracts"
    # form_class = ContarctFilterForm
    # paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        self.form = ContarctFilterForm(self.request.GET)
        qs = super().get_queryset().select_related("company", "creator").order_by("-id")
        query = self.request.GET.get("query", None)
        if query:
            qs = qs.filter(
                Q(number__icontains=query)
                | Q(object__icontains=query)
                | Q(description__icontains=query)
                | Q(company__name__icontains=query)
                | Q(town__name__icontains=query)
            ).distinct()
        start = self.request.GET.get("start", None)
        if start:
            qs = qs.filter(start=datetime.strptime(start, "%d.%m.%Y"))
        end = self.request.GET.get("end", None)
        if end:
            qs = qs.filter(end=datetime.strptime(end, "%d.%m.%Y"))
        return qs

    def get_context_data(self, **kwargs):
        context = super(ContractListView, self).get_context_data(**kwargs)
        context["form"] = self.form
        return context


class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    fields = [
        "number",
        "object",
        "state",
        "company",
        "town",
        "description",
        "start",
        "end",
        "gip",
        "users",
        "ada",
        "mpe",
        "mpm",
    ]
    # success_url = "/contracts/"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        p = super().post(request, *args, **kwargs)
        if self.request.user not in self.object.users.all():
            self.object.users.add(self.request.user)
        if self.object.gip not in self.object.users.all():
            self.object.users.add(self.object.gip)
        UserContractFolders.objects.bulk_create(
            [
                UserContractFolders(
                    user=i,
                    contract=self.object,
                    ada=i == self.object.gip and self.object.ada,
                    mpe=i == self.object.gip and self.object.mpe,
                    mpm=i == self.object.gip and self.object.mpm,
                )
                for i in self.object.users.all()
            ]
        )
        return p


class ContractDetailView(DetailView):
    model = Contract

    def get_context_data(self, **kwargs):
        context = super(ContractDetailView, self).get_context_data(**kwargs)
        context["user_folders"] = UserContractFolders.objects.filter(
            contract=self.kwargs.get("pk")
        ).select_related("user")
        context["permission_requests"] = (
            PermissionRequest.objects.filter(contract=self.kwargs.get("pk"))
            .select_related("user", "creator")
            .order_by("-id")
        )
        return context


class PermissionRequestCreateView(LoginRequiredMixin, CreateView):
    model = PermissionRequest
    fields = ["user", "ada", "mpe", "mpm"]

    def get_success_url(self) -> str:
        return self.object.contract.get_absolute_url()

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.contract_id = self.kwargs.get("pk")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        p = super().dispatch(request, *args, **kwargs)
        if p:
            if not Contract.objects.filter(
                id=self.kwargs.get("pk"), gip=request.user
            ).exists():
                return self.handle_no_permission()
        return p

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        contract = Contract.objects.get(id=self.kwargs.get("pk"))
        if not contract.ada:
            del context["form"].fields["ada"]
        if not contract.mpe:
            del context["form"].fields["mpe"]
        if not contract.mpm:
            del context["form"].fields["mpm"]
        return context


class PermissionRequestListView(LoginRequiredMixin, ListView):
    model = PermissionRequest
    context_object_name = "permission_requests"

    def get_queryset(self) -> QuerySet[Any]:
        qs = (
            super()
            .get_queryset()
            .select_related("user", "creator", "contract")
            .order_by("-id")
        )
        return qs

    def dispatch(self, request, *args, **kwargs):
        p = super().dispatch(request, *args, **kwargs)
        if p:
            if not self.request.user.it_staff:
                return self.handle_no_permission()
        return p


class PermissionRequestDoneView(LoginRequiredMixin, View):
    success_url = "/contracts/permission-requests/"

    def post(self, request, *args, **kwargs):
        pr = PermissionRequest.objects.filter(id=self.kwargs.get("pk")).first()
        ucf = UserContractFolders.objects.filter(
            user_id=pr.user_id, contract_id=pr.contract_id
        ).first()
        if ucf:
            ucf.ada = pr.ada
            ucf.mpe = pr.mpe
            ucf.mpm = pr.mpm
            ucf.save()
        else:
            UserContractFolders.objects.create(
                user_id=pr.user_id,
                contract_id=pr.contract_id,
                ada=pr.ada,
                mpe=pr.mpe,
                mpm=pr.mpm,
            )
        PermissionRequest.objects.filter(id=self.kwargs.get("pk")).update(done=now())
        return HttpResponseRedirect(self.request.META["HTTP_REFERER"])

    def dispatch(self, request, *args, **kwargs):
        p = super().dispatch(request, *args, **kwargs)
        if p:
            if not self.request.user.it_staff:
                return self.handle_no_permission()
        return p
