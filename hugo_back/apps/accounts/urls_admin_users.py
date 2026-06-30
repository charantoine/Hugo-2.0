from django.urls import path
from . import views_admin

urlpatterns = [
    path("", views_admin.UserCreate.as_view(), name="admin_users"),
]
