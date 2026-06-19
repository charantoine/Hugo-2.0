from django.urls import path
from . import views

urlpatterns = [
    path("", views.ReferentialListView.as_view(), name="referential_list"),
    path("import-v2/", views.ImportV2View.as_view(), name="import_v2"),
    path("<uuid:ref_id>/activities/", views.ReferentialActivityListView.as_view(), name="referential_activity_list"),
    path(
        "<uuid:ref_id>/activities/<uuid:activity_id>/tasks/",
        views.ReferentialActivityTaskListView.as_view(),
        name="referential_activity_task_list",
    ),
    path("<uuid:ref_id>/items/", views.ReferentialItemListView.as_view(), name="referential_item_list"),
    path(
        "<uuid:ref_id>/items/<uuid:item_id>/tasks/",
        views.ReferentialItemTaskListView.as_view(),
        name="referential_item_task_list",
    ),
    path(
        "<uuid:ref_id>/items/<uuid:item_id>/criteria/",
        views.ReferentialCriterionListCreateView.as_view(),
        name="referential_criterion_list_create",
    ),
    path(
        "<uuid:ref_id>/items/<uuid:item_id>/criteria/<uuid:criterion_id>/",
        views.ReferentialCriterionDetailView.as_view(),
        name="referential_criterion_detail",
    ),
]
