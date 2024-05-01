from typing import Any
from datetime import datetime
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Q
from .forms import ContarctFilterForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    # TemplateView,
)

# from django.views.generic.list import BaseListView

from .models import Contract, UserContractFolders

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
    ]
    success_url = "/contracts/"

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
                UserContractFolders(user=i, contract=self.object)
                for i in self.object.users.all()
            ]
        )
        return p


# class TopicDetailView(DetailView):
#     model = Topic

#     def get_context_data(self, **kwargs):
#         context = super(TopicDetailView, self).get_context_data(**kwargs)
#         context["posts"] = Post.objects.filter(topic=self.kwargs.get("pk"))
#         return context


# class TopicCreateView(LoginRequiredMixin, CreateView):
#     model = Topic
#     fields = ["title", "description", "subsection"]

#     def form_valid(self, form):
#         return super().form_valid(form)


# # Post views


# class PostDetailView(LoginRequiredMixin, FormMixin, DetailView):
#     model = Post
#     form_class = CreateCommentForm

#     def get_context_data(self, **kwargs):
#         context = super(PostDetailView, self).get_context_data(**kwargs)
#         context["comments"] = Comment.objects.filter(post=self.kwargs.get("pk"))
#         context["form"] = CreateCommentForm(
#             initial={"post": self.object, "author": self.request.user}
#         )

#         return context

#     def get_success_url(self):
#         return reverse("post-detail", kwargs={"pk": self.object.id})

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_valid(self, form):
#         form.save()
#         return super(PostDetailView, self).form_valid(form)


# class PostCreateView(LoginRequiredMixin, CreateView):
#     model = Post
#     fields = ["body"]

#     def get_success_url(self) -> str:

#         return self.object.topic.get_absolute_url()

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.topic = Topic.objects.get(pk=self.kwargs["pk"])
#         return super().form_valid(form)


# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     fields = ["title", "body"]

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)

#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False


# class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Post
#     success_url = "/"

#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False
