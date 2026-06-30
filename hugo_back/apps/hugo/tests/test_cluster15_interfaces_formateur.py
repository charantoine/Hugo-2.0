"""Cluster 15 — tests API interfaces formateur (persona C1 — Amélie).

Couvre : workflow TrainerKnowledgeItem (validate, reject, provisional),
création via atelier d'élicitation, usage_stats lecture seule, confidentialité.

Exécution locale :
  cd hugo_back && python -m pytest apps/hugo/tests/test_cluster15_interfaces_formateur.py -v
"""
from __future__ import annotations

import json

import pytest

from apps.accounts.models import Role, User
from apps.hugo.models import HugoMessage, HugoSession, TrainerKnowledgeItem

ENVIRONMENT = "local"
BRANCH = "feature/cluster15-interfaces-apprenant-formateur"

LEARNER_VERBATIM = "CLUSTER15_LEARNER_SECRET_VERBATIM_C1"


def _trainer_client(api_client, organisation):
    trainer = User.objects.create_user(
        username=f"trainer_c1_{organisation.id}",
        password="pass",
        organisation=organisation,
        role=Role.TRAINER,
    )
    api_client.force_authenticate(user=trainer)
    return trainer


def _learner_session_with_verbatim(organisation, learner_user, group) -> HugoSession:
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content=LEARNER_VERBATIM,
    )
    return session


# ---------------------------------------------------------------------------
# PERSONA C1 — Amélie (TRAINER) — workflow validation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_c1_validate_trainer_knowledge_item_persists_validated_status(
    api_client, organisation
):
    """C1 — action validate → statut validated_trainer persisté."""
    _trainer_client(api_client, organisation)
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Critère de maîtrise : sécuriser le poste avant intervention.",
        content_type="mastery_criterion",
        status="declared",
    )
    response = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "validate"},
        format="json",
    )
    item.refresh_from_db()

    assert response.status_code == 200
    assert response.data["status"] == "validated"
    assert item.status == "validated_trainer"
    assert item.validated_at is not None


@pytest.mark.django_db
def test_c1_mark_provisional_then_reject_persists_lifecycle(api_client, organisation):
    """C1 — declared → mark_provisional → reject avec persistance intermédiaire."""
    _trainer_client(api_client, organisation)
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Erreur fréquente : oublier l'EPI.",
        content_type="frequent_error",
        status="declared",
    )

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
        {"action": "reject", "reason": "Doublon avec item existant"},
        format="json",
    )
    assert reject.status_code == 200
    assert TrainerKnowledgeItem.objects.filter(id=item.id).count() == 0


@pytest.mark.django_db
def test_c1_edit_action_validates_with_updated_content(api_client, organisation):
    """C1 — action edit corrige le contenu et valide l'item."""
    trainer = _trainer_client(api_client, organisation)
    item = TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Brouillon incomplet",
        status="derived_provisional",
    )
    response = api_client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "edit", "content": "Règle absolue : couper l'alimentation avant intervention."},
        format="json",
    )
    item.refresh_from_db()

    assert response.status_code == 200
    assert item.status == "validated_trainer"
    assert "couper l'alimentation" in item.content
    assert item.validated_by_id == trainer.id


# ---------------------------------------------------------------------------
# PERSONA C1 — atelier d'élicitation (API existante)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_c1_elicitation_answers_creates_declared_items(api_client, organisation):
    """C1 — POST elicitation-answers crée des TrainerKnowledgeItem declared."""
    _trainer_client(api_client, organisation)
    response = api_client.post(
        "/hugo/trainer/referential-items/REF-COMP-001/elicitation-answers/",
        {
            "answers": {
                "q_mastery": "L'apprenant identifie les risques avant d'agir.",
                "q_errors": "Confondre cause et conséquence.",
            }
        },
        format="json",
    )

    assert response.status_code == 201
    created_ids = response.data["created"]
    assert len(created_ids) == 2
    items = TrainerKnowledgeItem.objects.filter(organisation=organisation)
    assert items.count() == 2
    assert all(item.status == "declared" for item in items)
    assert all(item.source_type == "dialogue_elicited" for item in items)


@pytest.mark.django_db
def test_c1_elicitation_questions_endpoint_returns_structured_workshop(api_client, organisation):
    """C1 — GET elicitation-questions expose le questionnaire atelier V0."""
    _trainer_client(api_client, organisation)
    response = api_client.get(
        "/hugo/trainer/referential-items/REF-COMP-001/elicitation-questions/"
    )

    assert response.status_code == 200
    assert response.data["referential_item_id"] == "REF-COMP-001"
    questions = response.data["questions"]
    assert len(questions) >= 3
    assert all("id" in q and "text" in q for q in questions)


# ---------------------------------------------------------------------------
# PERSONA C1 — usage_stats + confidentialité
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_c1_knowledge_list_exposes_readonly_usage_stats(api_client, organisation):
    """C1 — liste items : usage_stats lecture seule (exploitable / usage_note)."""
    _trainer_client(api_client, organisation)
    TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Savoir validé",
        status="validated_trainer",
    )
    TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Savoir déclaré",
        status="declared",
    )

    response = api_client.get("/hugo/trainer/knowledge-items/")

    assert response.status_code == 200
    items = {row["content"]: row for row in response.data["items"]}
    assert items["Savoir validé"]["usage_stats"]["exploitable"] is True
    assert items["Savoir déclaré"]["usage_stats"]["exploitable"] is False
    assert "usage_note" in items["Savoir validé"]["usage_stats"]
    assert items["Savoir validé"]["usage_stats"]["usage_count"] is None


@pytest.mark.django_db
def test_c1_trainer_knowledge_endpoints_do_not_expose_learner_verbatim(
    api_client, organisation, learner_user, group
):
    """C1 — APIs trainer sans fuite verbatim apprenant (oracle C1-03)."""
    _trainer_client(api_client, organisation)
    _learner_session_with_verbatim(organisation, learner_user, group)
    TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Connaissance métier sans lien verbatim",
        status="declared",
    )

    list_response = api_client.get("/hugo/trainer/knowledge-items/")
    questions_response = api_client.get(
        "/hugo/trainer/referential-items/REF-X/elicitation-questions/"
    )

    assert list_response.status_code == 200
    assert questions_response.status_code == 200
    combined = json.dumps(list_response.data) + json.dumps(questions_response.data)
    assert LEARNER_VERBATIM not in combined


@pytest.mark.django_db
def test_c1_learner_cannot_access_trainer_knowledge_list(api_client, learner_user, organisation):
    """C1 — rôle LEARNER → 403 sur liste knowledge-items."""
    api_client.force_authenticate(user=learner_user)
    response = api_client.get("/hugo/trainer/knowledge-items/")

    assert response.status_code == 403
