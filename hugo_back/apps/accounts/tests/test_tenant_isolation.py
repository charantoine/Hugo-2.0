"""Multi-tenant isolation — SUPERADMIN context, memberships, org transfer."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.models import TutorPrompt
from apps.referentials.models import Group, GroupMembership


@pytest.fixture
def org_a(db):
    return Organisation.objects.create(name="Org A")


@pytest.fixture
def org_b(db):
    return Organisation.objects.create(name="Org B")


@pytest.fixture
def orgadmin_a(org_a):
    return User.objects.create_user(
        username="orgadmin_a",
        password="testpass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )


@pytest.fixture
def superadmin_a(org_a):
    return User.objects.create_user(
        username="superadmin_a",
        password="testpass",
        organisation=org_a,
        role=Role.SUPERADMIN,
        is_superuser=True,
    )


@pytest.fixture
def learner_a(org_a):
    return User.objects.create_user(
        username="learner_a",
        password="testpass",
        organisation=org_a,
        role=Role.LEARNER,
    )


@pytest.fixture
def learner_b(org_b):
    return User.objects.create_user(
        username="learner_b",
        password="testpass",
        organisation=org_b,
        role=Role.LEARNER,
    )


@pytest.fixture
def group_a(org_a):
    return Group.objects.create(organisation=org_a, name="Group A")


@pytest.fixture
def group_b(org_b):
    return Group.objects.create(organisation=org_b, name="Group B")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_orgadmin_cannot_list_other_org_users(orgadmin_a, org_b, learner_b, api_client):
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.get("/users/")
    assert response.status_code == 200
    usernames = [row["username"] for row in response.json()]
    assert "learner_b" not in usernames


@pytest.mark.django_db
def test_superadmin_lists_users_in_target_org_via_header(
    superadmin_a, org_b, learner_b, api_client
):
    api_client.force_authenticate(user=superadmin_a)
    response = api_client.get("/users/", HTTP_X_ORGANISATION_ID=str(org_b.id))
    assert response.status_code == 200
    usernames = [row["username"] for row in response.json()]
    assert "learner_b" in usernames


@pytest.mark.django_db
def test_orgadmin_cannot_use_tenant_header(orgadmin_a, org_b, learner_b, api_client):
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.get("/users/", HTTP_X_ORGANISATION_ID=str(org_b.id))
    assert response.status_code == 200
    usernames = [row["username"] for row in response.json()]
    assert "learner_b" not in usernames


@pytest.mark.django_db
def test_membership_cross_org_group_rejected(orgadmin_a, org_a, org_b, group_b, learner_a, api_client):
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.post(
        f"/groups/{group_b.id}/members/",
        {"user": str(learner_a.id)},
        format="json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_membership_multi_group_same_org_allowed(orgadmin_a, org_a, learner_a, api_client):
    group_one = Group.objects.create(organisation=org_a, name="G1")
    group_two = Group.objects.create(organisation=org_a, name="G2")
    api_client.force_authenticate(user=orgadmin_a)
    r1 = api_client.post(f"/groups/{group_one.id}/members/", {"user": str(learner_a.id)}, format="json")
    r2 = api_client.post(f"/groups/{group_two.id}/members/", {"user": str(learner_a.id)}, format="json")
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert GroupMembership.objects.filter(user=learner_a, organisation=org_a).count() == 2


@pytest.mark.django_db
def test_user_org_transfer_forbidden(orgadmin_a, org_a, learner_a, api_client):
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.patch(
        f"/users/{learner_a.id}/",
        {"organisation": str(org_a.id)},
        format="json",
    )
    assert response.status_code in (200, 400)
    learner_a.refresh_from_db()
    assert learner_a.organisation_id == org_a.id


@pytest.mark.django_db
def test_default_tutor_prompt_cross_org_rejected(orgadmin_a, org_a, org_b, group_a, api_client):
    prompt_b = TutorPrompt.objects.create(
        organisation=org_b,
        code="prompt-b",
        name="Prompt B",
        prompt_type="AFEST_HUGO",
    )
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.patch(
        f"/groups/{group_a.id}/",
        {"default_tutor_prompt": str(prompt_b.id)},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_superadmin_lists_all_organisations(superadmin_a, org_a, org_b, api_client):
    api_client.force_authenticate(user=superadmin_a)
    response = api_client.get("/admin/organisations/")
    assert response.status_code == 200
    names = {row["name"] for row in response.json()}
    assert {"Org A", "Org B"}.issubset(names)


@pytest.mark.django_db
def test_orgadmin_lists_only_own_organisation(orgadmin_a, org_a, org_b, api_client):
    api_client.force_authenticate(user=orgadmin_a)
    response = api_client.get("/admin/organisations/")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Org A"


@pytest.mark.django_db
def test_superadmin_invalid_tenant_header_returns_400(superadmin_a, api_client):
    api_client.force_authenticate(user=superadmin_a)
    response = api_client.get(
        "/users/",
        HTTP_X_ORGANISATION_ID="00000000-0000-0000-0000-000000000099",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_superadmin_creates_user_in_target_org(superadmin_a, org_b, api_client):
    api_client.force_authenticate(user=superadmin_a)
    response = api_client.post(
        "/users/",
        {
            "username": "new_learner_b",
            "email": "new@example.com",
            "password": "ComplexPass123!",
            "role": Role.LEARNER,
        },
        format="json",
        HTTP_X_ORGANISATION_ID=str(org_b.id),
    )
    assert response.status_code == 201
    created = User.objects.get(username="new_learner_b")
    assert created.organisation_id == org_b.id
