from django.urls import path
from . import views_admin

urlpatterns = [
    path("", views_admin.OrganisationCreateList.as_view(), name="admin_organisations"),
]
