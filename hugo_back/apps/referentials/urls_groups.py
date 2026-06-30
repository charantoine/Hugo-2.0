from django.urls import path
from . import views_groups
from . import views
from apps.library import views as library_views

urlpatterns = [
    path("", views_groups.GroupListCreate.as_view(), name="group_list_create"),
    path("<uuid:group_id>/", views_groups.GroupRetrieveUpdate.as_view(), name="group_detail"),
    path("<uuid:group_id>/members/", views_groups.GroupMembershipListCreate.as_view(), name="group_members"),
    path("<uuid:group_id>/tutor-links/", views_groups.TutorLinkListCreate.as_view(), name="group_tutor_links"),
    path("<uuid:group_id>/referential-config/", views.ReferentialConfigView.as_view(), name="referential_config"),
    path("<uuid:group_id>/referentials/<uuid:ref_id>/items/<uuid:item_id>/overlay/", views.ReferentialItemOverlayView.as_view(), name="referential_item_overlay"),
    path(
        "<uuid:group_id>/library/documents/<uuid:document_id>/content/",
        library_views.GroupLibraryDocumentContentView.as_view(),
        name="group_library_document_content",
    ),
    path("<uuid:group_id>/library/", library_views.GroupLibraryListCreate.as_view(), name="group_library"),
    path("<uuid:group_id>/library/<uuid:group_document_id>/", library_views.GroupLibraryUpdate.as_view(), name="group_library_update"),
]
