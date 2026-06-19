"""
Quality: AuditLog (metadata only, no verbatim). Qualiopi evidence-bundle (POST-POC table names reserved).
"""
import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Critical actions: validation, sharing, exports. No raw content."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=False,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=64)
    resource_type = models.CharField(max_length=64)
    resource_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]
