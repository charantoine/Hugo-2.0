import pytest

from apps.accounts.models import Role, User
from apps.hugo.models import TrainerKnowledgeItem


@pytest.mark.django_db
def test_trainer_chat_import_creates_provisional_resource(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_chat_import",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)
    session_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"

    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Cas-type : sécuriser le chantier avant intervention.",
            "content_type": "mastery_criterion",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "provenance_note": "Créé depuis chat — à relire",
            "meta": {
                "import_kind": "trainer_resource_provisional",
                "session_id": session_id,
                "source_message_ids": [message_id],
                "draft_title": "Cas-type chantier",
            },
        },
        format="json",
    )
    assert response.status_code == 201
    item = TrainerKnowledgeItem.objects.get()
    assert item.status == "derived_provisional"
    assert item.source_type == "chat_import"
    assert item.meta["import_kind"] == "trainer_resource_provisional"
    assert item.meta["session_id"] == session_id


@pytest.mark.django_db
def test_trainer_chat_import_creates_pedagogical_explication(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_explication",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)

    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Explicitation : objectif et situation de référence.",
            "content_type": "pedagogical_explication",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "meta": {
                "import_kind": "trainer_explication",
                "session_id": "33333333-3333-3333-3333-333333333333",
                "source_message_ids": [],
                "source": "chat",
                "explication": {
                    "learning_objective": "Comprendre le risque électrique",
                    "reference_situation": "Coffret ouvert en intervention",
                },
            },
        },
        format="json",
    )
    assert response.status_code == 201
    item = TrainerKnowledgeItem.objects.get()
    assert item.content_type == "pedagogical_explication"
    assert item.meta["explication"]["learning_objective"] == "Comprendre le risque électrique"
    assert item.meta.get("source") == "chat"


@pytest.mark.django_db
def test_trainer_chat_import_forbidden_for_learner(api_client, organisation):
    learner = User.objects.create_user(
        username="learner_no_trainer",
        password="pass",
        organisation=organisation,
        role=Role.LEARNER,
    )
    api_client.force_authenticate(user=learner)

    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Tentative import",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "meta": {
                "import_kind": "trainer_explication",
                "session_id": "55555555-5555-5555-5555-555555555555",
                "source": "chat",
            },
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_trainer_explication_import_then_validate_non_regression(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_validate_explication",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)

    create_response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Explicitation complète",
            "content_type": "pedagogical_explication",
            "source_type": "chat_import",
            "status": "derived_provisional",
            "meta": {
                "import_kind": "trainer_explication",
                "session_id": "66666666-6666-6666-6666-666666666666",
                "source": "chat",
                "group_id": "grp-smoke",
                "explication": {"learning_objective": "Notion test"},
            },
        },
        format="json",
    )
    assert create_response.status_code == 201
    item = TrainerKnowledgeItem.objects.get()
    assert item.status == "derived_provisional"

    validate_response = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "validate"},
        format="json",
    )
    item.refresh_from_db()
    assert validate_response.status_code == 200
    assert item.status == "validated_trainer"
    assert item.meta["explication"]["learning_objective"] == "Notion test"


@pytest.mark.django_db
def test_trainer_chat_import_requires_meta_for_chat_source(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_chat_guard",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)

    response = api_client.post(
        "/hugo/trainer/knowledge-items/",
        {
            "content": "Sans meta",
            "source_type": "chat_import",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_trainer_patch_merges_decision_rationale(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_rationale",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Ressource existante",
        status="derived_provisional",
        meta={"existing_key": "keep"},
    )
    api_client.force_authenticate(user=trainer)

    response = api_client.patch(
        f"/hugo/trainer/knowledge-items/{item.id}/",
        {
            "meta": {
                "decision_rationale": {
                    "envisioned_decision": "Laisser provisoire",
                    "reasons": "Besoin de relecture collective",
                    "status": "draft",
                    "session_id": "44444444-4444-4444-4444-444444444444",
                },
            },
            "provenance_note": "Justification importée depuis chat",
        },
        format="json",
    )
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.meta["existing_key"] == "keep"
    assert item.meta["decision_rationale"]["envisioned_decision"] == "Laisser provisoire"
    assert item.meta["decision_rationale"]["status"] == "draft"
    assert "Justification importée" in item.provenance_note


@pytest.mark.django_db
def test_trainer_patch_decision_rationale_preserves_status_and_validate_workflow(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_rationale_status",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Item pour justification",
        status="declared",
        meta={"explication": {"learning_objective": "keep-me"}},
    )
    api_client.force_authenticate(user=trainer)

    patch_response = api_client.patch(
        f"/hugo/trainer/knowledge-items/{item.id}/",
        {
            "meta": {
                "decision_rationale": {
                    "envisioned_decision": "Laisser provisoire",
                    "reasons": "Relecture nécessaire",
                    "status": "draft",
                    "source": "chat",
                    "institutional_decision": False,
                    "session_id": "77777777-7777-7777-7777-777777777777",
                },
            },
            "provenance_note": "Justification importée depuis chat — brouillon",
        },
        format="json",
    )
    assert patch_response.status_code == 200
    item.refresh_from_db()
    assert item.status == "declared"
    assert item.meta["explication"]["learning_objective"] == "keep-me"
    assert item.meta["decision_rationale"]["status"] == "draft"
    assert item.meta["decision_rationale"]["institutional_decision"] is False

    validate_response = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "validate"},
        format="json",
    )
    item.refresh_from_db()
    assert validate_response.status_code == 200
    assert item.status == "validated_trainer"
    assert item.meta["decision_rationale"]["envisioned_decision"] == "Laisser provisoire"
