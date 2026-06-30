from django.urls import path

from . import views_admin

app_name = "accounts_users"

urlpatterns = [
    # GET/POST /users/ — lister/créer des utilisateurs de l’organisation
    path("", views_admin.OrgUserCreate.as_view(), name="user_create"),
    # GET /users/<uuid:user_id>/ — détail d’un utilisateur de l’organisation
    path("<uuid:user_id>/", views_admin.OrgUserDetail.as_view(), name="user_detail"),
]

