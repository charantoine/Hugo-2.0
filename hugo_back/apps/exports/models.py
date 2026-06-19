"""
Exports: ExportRun (params, file path). ExportTemplate optional POC.
"""
import uuid
from django.db import models


class ExportRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="export_runs",
        null=False,
    )
    params = models.JSONField(default=dict)
    file_path = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "export_run"
        ordering = ["-created_at"]
