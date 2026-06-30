from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Organisation, User


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request.user, "role", None) == "SUPERADMIN":
            return qs
        if request.user.is_authenticated:
            return qs.filter(id=request.user.organisation_id)
        return qs.none()

    def has_add_permission(self, request):
        return getattr(request.user, "role", None) == "SUPERADMIN"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "email", "role", "organisation", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "organisation")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Organisation", {"fields": ("organisation", "role")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "organisation",
                    "role",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request.user, "role", None) == "SUPERADMIN":
            return qs
        if request.user.is_authenticated:
            return qs.filter(organisation_id=request.user.organisation_id)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if getattr(request.user, "role", None) != "SUPERADMIN":
            obj.organisation_id = request.user.organisation_id
        super().save_model(request, obj, form, change)

