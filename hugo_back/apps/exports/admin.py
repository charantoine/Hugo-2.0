from django.contrib import admin

from .models import ExportRun


@admin.register(ExportRun)
class ExportRunAdmin(admin.ModelAdmin):
    list_display = ("id", "organisation", "created_at", "file_path")
    list_filter = ("organisation",)
