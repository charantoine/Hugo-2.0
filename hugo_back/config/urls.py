"""Root URL configuration — POC Hugo."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("users/", include("apps.accounts.urls_users")),
    path("admin/organisations/", include("apps.accounts.urls_admin_organisations")),
    path("admin/users/", include("apps.accounts.urls_admin_users")),
    path("groups/", include("apps.referentials.urls_groups")),
    path("hugo/", include("apps.hugo.urls")),
    path("traces/", include("apps.hugo.urls_traces")),
    path("learners/", include("apps.hugo.urls_learners")),
    path("documents/", include("apps.library.urls")),
    path("referentials/", include("apps.referentials.urls")),
    path("exports/", include("apps.exports.urls")),
    path("dashboard/", include("apps.hugo.urls_dashboard")),
    path("evidence/", include("apps.hugo.urls_evidence")),
    path("quality/", include("apps.quality.urls")),
    path("internal/", include("apps.hugo.urls_internal")),
    path("admin/", admin.site.urls),
]
