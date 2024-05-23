from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from typing import Any
from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import (
    User,
    Town,
    Company,
    Contract,
    UserContractFolders,
    PermissionRequest,
    EndDateContractChange,
)

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.site.login = login_required(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (_("Status"), {"fields": ("supervisor", "it_staff")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser", "supervisor", "it_staff"]
    search_fields = ["name"]


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_display_links = ("name",)
    search_fields = ("name",)


class UserContractFoldersInline(admin.TabularInline):
    model = UserContractFolders


class PermissionRequestInline(admin.TabularInline):
    model = PermissionRequest


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["number"]
    list_display_links = ("number",)
    search_fields = (
        "number",
        "object",
    )
    inlines = [UserContractFoldersInline, PermissionRequestInline]
    autocomplete_fields = (
        "company",
        "town",
        "creator",
        "gip",
    )
    filter_horizontal = ("users",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "company",
                "town",
                "creator",
                "gip",
            )
        )


@admin.register(UserContractFolders)
class UserContractFoldersAdmin(admin.ModelAdmin):
    list_display = ["id", "contract", "user", "ada", "mpm", "mpe"]
    list_display_links = ("id",)
    search_fields = ("contract__number",)
    list_editable = (
        "ada",
        "mpm",
        "mpe",
    )
    autocomplete_fields = (
        "contract",
        "user",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "contract",
                "user",
            )
        )


@admin.register(PermissionRequest)
class PermissionRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "contract",
        "user",
        "ada",
        "mpe",
        "mpm",
        "creator",
        "created",
        "done",
    ]
    list_display_links = ("id",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "contract",
                "user",
                "creator",
            )
        )


@admin.register(EndDateContractChange)
class EndDateContractChangeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "contract",
        "user",
        "new_date",
        "created",
    ]
    list_display_links = ("id",)
    list_select_related = (
        "contract",
        "user",
    )
