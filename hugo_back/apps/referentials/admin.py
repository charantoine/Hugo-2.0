from django.contrib import admin

from .models import (
    Group,
    GroupMembership,
    TutorLearnerLink,
    Scale,
    ScaleLevel,
    Referential,
    ReferentialItem,
    ReferentialConfig,
    ReferentialItemOverlay,
)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organisation", "created_at")
    list_filter = ("organisation",)
    search_fields = ("name",)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "user", "organisation", "created_at")
    list_filter = ("organisation", "group")
    search_fields = ("user__username",)


@admin.register(TutorLearnerLink)
class TutorLearnerLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "tutor", "learner", "organisation", "created_at")
    list_filter = ("organisation",)
    search_fields = ("tutor__username", "learner__username")


@admin.register(Scale)
class ScaleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organisation", "created_at")
    list_filter = ("organisation",)
    search_fields = ("name",)


@admin.register(ScaleLevel)
class ScaleLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "scale", "level_order", "label", "organisation", "created_at")
    list_filter = ("organisation", "scale")
    search_fields = ("label",)
    ordering = ("scale", "level_order")


@admin.register(Referential)
class ReferentialAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "source_ref", "organisation", "created_at")
    list_filter = ("organisation",)
    search_fields = ("name", "source_ref")


@admin.register(ReferentialItem)
class ReferentialItemAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "title", "referential", "organisation", "created_at")
    list_filter = ("organisation", "referential")
    search_fields = ("code", "title")


@admin.register(ReferentialConfig)
class ReferentialConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "referential", "scale", "organisation", "created_at")
    list_filter = ("organisation", "group")


@admin.register(ReferentialItemOverlay)
class ReferentialItemOverlayAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "referential_item", "enabled", "organisation", "updated_at")
    list_filter = ("organisation", "group", "enabled")

