"""Patches schéma SQLite idempotents — baseline B (MIGRATION_MODULES désactivé)."""
from __future__ import annotations

from django.db import connection


def _column_names(cursor, table: str) -> set[str]:
    description = connection.introspection.get_table_description(cursor, table)
    return {col.name for col in description}


def ensure_persona_schema() -> list[str]:
    """
    Applique les changements de la migration 0022 sur une base SQLite existante.

    Nécessaire car config.settings.sqlite_test désactive les migrations Django
    tout en réutilisant test.sqlite3 entre les runs locaux.
    """
    if connection.vendor != "sqlite":
        return []

    from apps.hugo.models import HugoSession, PersonaConversationProfile, TutorPrompt

    changes: list[str] = []
    existing_tables = set(connection.introspection.table_names())

    with connection.cursor() as cursor:
        with connection.schema_editor() as editor:
            if PersonaConversationProfile._meta.db_table not in existing_tables:
                editor.create_model(PersonaConversationProfile)
                changes.append("created persona_conversation_profile")

            tutor_cols = _column_names(cursor, TutorPrompt._meta.db_table)
            if "persona_scope" not in tutor_cols:
                editor.add_field(TutorPrompt, TutorPrompt._meta.get_field("persona_scope"))
                changes.append("added tutor_prompt.persona_scope")

            session_cols = _column_names(cursor, HugoSession._meta.db_table)
            if "persona_conversation_profile_id" not in session_cols:
                editor.add_field(HugoSession, HugoSession._meta.get_field("persona_conversation_profile"))
                changes.append("added hugo_session.persona_conversation_profile_id")

    return changes
