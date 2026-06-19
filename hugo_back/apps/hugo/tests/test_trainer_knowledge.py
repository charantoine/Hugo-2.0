import pytest

from apps.accounts.models import Role, User
from apps.hugo.models import TrainerKnowledgeItem


@pytest.mark.django_db
def test_trainer_elicitation_and_validation_flow(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_fixture",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)

    create_response = api_client.post(
        "/hugo/trainer/referential-items/C1/elicitation-answers/",
        {"answers": {"q_mastery": "Il sécurise le chantier avant intervention."}},
        format="json",
    )
    assert create_response.status_code == 201
    item = TrainerKnowledgeItem.objects.get()
    assert item.status == "declared"

    validate_response = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "validate"},
        format="json",
    )
    item.refresh_from_db()

    assert validate_response.status_code == 200
    assert item.status == "validated_trainer"


@pytest.mark.django_db
def test_trainer_knowledge_list_includes_usage_stats(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_list",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Savoir test",
        status="declared",
    )
    api_client.force_authenticate(user=trainer)
    response = api_client.get("/hugo/trainer/knowledge-items/")
    assert response.status_code == 200
    item = response.data["items"][0]
    assert item["usage_stats"]["exploitable"] is False
    assert "usage_note" in item["usage_stats"]


@pytest.mark.django_db
def test_trainer_mark_provisional_and_reject(api_client, organisation):
    trainer = User.objects.create_user(
        username="trainer_actions",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Item à traiter",
        status="declared",
    )
    api_client.force_authenticate(user=trainer)

    provisional = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "mark_provisional"},
        format="json",
    )
    item.refresh_from_db()
    assert provisional.status_code == 200
    assert item.status == "derived_provisional"

    reject = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "reject", "reason": "Hors périmètre"},
        format="json",
    )
    assert reject.status_code == 200
    assert TrainerKnowledgeItem.objects.filter(id=item.id).count() == 0
