"""
Logging helpers — metadata only, no verbatim content.
SPEC: Never log raw chat verbatim (learner or tutor messages).
"""
import logging

logger = logging.getLogger(__name__)


def log_action(action, resource_type, resource_id, status="ok", error=None, **extra):
    """Log an action with metadata only (ids, timestamps, status, no content)."""
    payload = {
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id),
        "status": status,
        **extra,
    }
    if error:
        payload["error"] = error
    logger.info("action", extra=payload)
