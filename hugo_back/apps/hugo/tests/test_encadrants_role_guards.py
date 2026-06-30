"""Role guards on trainer knowledge and org exports (ENC-CODE-02/03)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role


@pytest.fixture
def role_guard_setup(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org Role Guards")
    learner = user_model.objects.create_user(
        username="learner_rg",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    tutor = user_model.objects.create_user(
        username="tutor_rg",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    trainer = user_model.objects.create_user(
        username="trainer_rg",
        password="pass",
        organisation=org,
        role=Role.TRAINER,
    )
    orgadmin = user_model.objects.create_user(
        username="orgadmin_rg",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    return {
        "org": org,
        "learner": learner,
        "tutor": tutor,
        "trainer": trainer,
        "orgadmin": orgadmin,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role_key,expected_status",
    [
        ("learner", 403),
        ("tutor", 403),
        ("trainer", 200),
        ("orgadmin", 200),
    ],
)
def test_trainer_knowledge_list_role_guard(role_guard_setup, role_key, expected_status):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup[role_key])
    response = client.get("/hugo/trainer/knowledge-items/")
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_learner_forbidden_on_trainer_elicitation_answers(role_guard_setup):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup["learner"])
    response = client.post(
        "/hugo/trainer/referential-items/C1/elicitation-answers/",
        {"answers": {"q_mastery": "test"}},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_tutor_forbidden_on_trainer_elicitation_answers(role_guard_setup):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup["tutor"])
    response = client.post(
        "/hugo/trainer/referential-items/C1/elicitation-answers/",
        {"answers": {"q_mastery": "test"}},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_tutor_forbidden_on_export_run(role_guard_setup):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup["tutor"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_trainer_forbidden_on_export_run(role_guard_setup):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup["trainer"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_orgadmin_allowed_on_export_run(role_guard_setup):
    client = APIClient()
    client.force_authenticate(user=role_guard_setup["orgadmin"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 200
