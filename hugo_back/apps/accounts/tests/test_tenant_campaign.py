"""
Campagne multi-tenant — personas, contournements, exports, sessions.
Complète test_tenant_isolation.py avec scénarios par rôle métier.
"""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.models import HugoSession, TutorPrompt
from apps.referentials.models import Group, GroupMembership, Referential, TutorLearnerLink


@pytest.fixture
def tenant_world(db):
    """Deux organisations avec personas complets dans A et ressources dans B."""
    org_a = Organisation.objects.create(name="Campaign Org A")
    org_b = Organisation.objects.create(name="Campaign Org B")

    def _user(org, username, role):
        return User.objects.create_user(
            username=username,
            password="CampaignPass123!",
            organisation=org,
            role=role,
        )

    personas_a = {
        "superadmin": _user(org_a, "camp_superadmin", Role.SUPERADMIN),
        "orgadmin": _user(org_a, "camp_orgadmin", Role.ORGADMIN),
        "trainer": _user(org_a, "camp_trainer", Role.TRAINER),
        "tutor": _user(org_a, "camp_tutor", Role.TUTOR),
        "learner": _user(org_a, "camp_learner", Role.LEARNER),
    }
    personas_b = {
        "learner": _user(org_b, "camp_learner_b", Role.LEARNER),
        "orgadmin": _user(org_b, "camp_orgadmin_b", Role.ORGADMIN),
    }
    group_a = Group.objects.create(organisation=org_a, name="Campaign Group A")
    group_b = Group.objects.create(organisation=org_b, name="Campaign Group B")
    ref_a = Referential.objects.create(organisation=org_a, name="Ref A")
    ref_b = Referential.objects.create(organisation=org_b, name="Ref B")

    for key in ("tutor", "trainer", "learner"):
        GroupMembership.objects.create(
            organisation=org_a,
            group=group_a,
            user=personas_a[key],
        )
    GroupMembership.objects.create(
        organisation=org_b,
        group=group_b,
        user=personas_b["learner"],
    )
    TutorLearnerLink.objects.create(
        organisation=org_a,
        group=group_a,
        tutor=personas_a["tutor"],
        learner=personas_a["learner"],
    )
    session_a = HugoSession.objects.create(
        organisation=org_a,
        group=group_a,
        learner=personas_a["learner"],
    )
    session_b = HugoSession.objects.create(
        organisation=org_b,
        group=group_b,
        learner=personas_b["learner"],
    )

    return {
        "org_a": org_a,
        "org_b": org_b,
        "group_a": group_a,
        "group_b": group_b,
        "ref_a": ref_a,
        "ref_b": ref_b,
        "session_a": session_a,
        "session_b": session_b,
        "personas_a": personas_a,
        "personas_b": personas_b,
    }


@pytest.fixture
def api_client():
    return APIClient()


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


# --- ORGADMIN A : périmètre strict ---


@pytest.mark.django_db
def test_orgadmin_a_cannot_list_groups_of_org_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.get("/groups/")
    names = {g["name"] for g in response.json()}
    assert "Campaign Group B" not in names
    assert "Campaign Group A" in names


@pytest.mark.django_db
def test_orgadmin_a_cannot_get_group_b_detail(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.get(f"/groups/{tenant_world['group_b'].id}/")
    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_orgadmin_a_cannot_list_referentials_of_org_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.get("/referentials/")
    names = {r["name"] for r in response.json()}
    assert "Ref B" not in names
    assert "Ref A" in names


@pytest.mark.django_db
def test_orgadmin_a_forged_user_create_in_org_b_rejected(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.post(
        "/users/",
        {
            "username": "forged_cross_org",
            "email": "forged@example.com",
            "password": "CampaignPass123!",
            "role": Role.LEARNER,
            "organisation": str(tenant_world["org_b"].id),
        },
        format="json",
    )
    assert response.status_code == 400
    assert not User.objects.filter(username="forged_cross_org").exists()


# --- LEARNER A : sessions et admin interdits ---


@pytest.mark.django_db
def test_learner_a_cannot_access_session_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["learner"])
    response = api_client.get(f"/hugo/sessions/{tenant_world['session_b'].id}/")
    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_learner_a_cannot_list_users(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["learner"])
    response = api_client.get("/users/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_learner_a_cannot_list_all_organisations(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["learner"])
    response = api_client.get("/admin/organisations/")
    assert response.status_code == 403


# --- TUTOR A : visibilité groupes / pas org B ---


@pytest.mark.django_db
def test_tutor_a_does_not_see_group_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["tutor"])
    response = api_client.get("/groups/")
    group_ids = {g["id"] for g in response.json()}
    assert str(tenant_world["group_b"].id) not in group_ids


@pytest.mark.django_db
def test_tutor_a_cannot_access_dashboard_group_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["tutor"])
    gb = tenant_world["group_b"]
    lb = tenant_world["personas_b"]["learner"]
    response = api_client.get(f"/dashboard/groups/{gb.id}/learners/{lb.id}/timeline/")
    assert response.status_code in (403, 404)


# --- TRAINER A : knowledge scoped, pas org B ---


@pytest.mark.django_db
def test_trainer_a_can_list_knowledge_in_org_a(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["trainer"])
    response = api_client.get("/hugo/trainer/knowledge-items/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_trainer_a_cannot_access_admin_organisations(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["trainer"])
    response = api_client.get("/admin/organisations/")
    assert response.status_code == 403


# --- SUPERADMIN : multi-org via header ---


@pytest.mark.django_db
def test_superadmin_lists_groups_in_org_b_via_header(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    response = api_client.get(
        "/groups/",
        HTTP_X_ORGANISATION_ID=str(tenant_world["org_b"].id),
    )
    assert response.status_code == 200
    names = {g["name"] for g in response.json()}
    assert "Campaign Group B" in names
    assert "Campaign Group A" not in names


@pytest.mark.django_db
def test_superadmin_creates_group_in_org_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    response = api_client.post(
        "/groups/",
        {"name": "Superadmin Created B", "llm_backend": "OLLAMA"},
        format="json",
        HTTP_X_ORGANISATION_ID=str(tenant_world["org_b"].id),
    )
    assert response.status_code == 201
    assert Group.objects.filter(
        name="Superadmin Created B",
        organisation=tenant_world["org_b"],
    ).exists()


@pytest.mark.django_db
def test_superadmin_lists_referentials_in_org_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    response = api_client.get(
        "/referentials/",
        HTTP_X_ORGANISATION_ID=str(tenant_world["org_b"].id),
    )
    assert response.status_code == 200
    names = {r["name"] for r in response.json()}
    assert "Ref B" in names
    assert "Ref A" not in names


# --- Contournements / attaques ---


@pytest.mark.django_db
def test_forged_membership_user_org_a_to_group_b(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.post(
        f"/groups/{tenant_world['group_b'].id}/members/",
        {"user": str(tenant_world["personas_a"]["learner"].id)},
        format="json",
    )
    assert response.status_code == 404
    assert not GroupMembership.objects.filter(
        user=tenant_world["personas_a"]["learner"],
        group=tenant_world["group_b"],
    ).exists()


@pytest.mark.django_db
def test_forged_tutor_link_cross_org_group(tenant_world, api_client):
    """SUPERADMIN scoped to org A cannot attach links on group B (404)."""
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    response = api_client.post(
        f"/groups/{tenant_world['group_b'].id}/tutor-links/",
        {
            "tutor": str(tenant_world["personas_a"]["tutor"].id),
            "learner": str(tenant_world["personas_b"]["learner"].id),
        },
        format="json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_orgadmin_b_cannot_access_group_a(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_b"]["orgadmin"])
    response = api_client.get(f"/groups/{tenant_world['group_a'].id}/")
    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_superadmin_without_header_stays_in_home_org(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    response = api_client.get("/groups/")
    names = {g["name"] for g in response.json()}
    assert "Campaign Group A" in names
    assert "Campaign Group B" not in names


@pytest.mark.django_db
def test_orgadmin_cannot_create_tutor_link(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    tutor = tenant_world["personas_a"]["tutor"]
    learner = tenant_world["personas_a"]["learner"]
    response = api_client.post(
        f"/groups/{tenant_world['group_a'].id}/tutor-links/",
        {"tutor": str(tutor.id), "learner": str(learner.id)},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_superadmin_can_create_tutor_link(tenant_world, api_client):
    _auth(api_client, tenant_world["personas_a"]["superadmin"])
    tutor = tenant_world["personas_a"]["tutor"]
    learner = tenant_world["personas_a"]["learner"]
    TutorLearnerLink.objects.filter(
        group=tenant_world["group_a"], tutor=tutor, learner=learner
    ).delete()
    response = api_client.post(
        f"/groups/{tenant_world['group_a'].id}/tutor-links/",
        {"tutor": str(tutor.id), "learner": str(learner.id)},
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_documents_list_scoped_to_tenant(tenant_world, api_client):
    from apps.library.models import Document

    Document.objects.create(
        organisation=tenant_world["org_a"],
        title="Doc A",
        file_path="a/doc.pdf",
    )
    Document.objects.create(
        organisation=tenant_world["org_b"],
        title="Doc B",
        file_path="b/doc.pdf",
    )
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.get("/documents/")
    titles = {d["title"] for d in response.json()}
    assert "Doc A" in titles
    assert "Doc B" not in titles


@pytest.mark.django_db
def test_conduct_profiles_scoped_to_tenant_org(tenant_world, api_client):
    from apps.hugo.models import TutorConductProfile

    TutorConductProfile.objects.create(
        organisation=tenant_world["org_b"],
        posture="reflective_afest",
        system_template="org b frame",
    )
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.get("/hugo/conduct-profiles/")
    assert response.status_code == 200
    org_ids = {p.get("organisation") for p in response.json() if p.get("organisation")}
    assert str(tenant_world["org_b"].id) not in {str(x) for x in org_ids if x}


@pytest.mark.django_db
def test_evaluation_export_cross_org_group_id_ignored(tenant_world, api_client):
    """Export avec group_id d'une autre org ne doit pas fuiter de traces."""
    from apps.hugo.models import Trace

    Trace.objects.create(
        organisation=tenant_world["org_b"],
        session=tenant_world["session_b"],
        payload_structured={"secret": "org_b_only"},
    )
    _auth(api_client, tenant_world["personas_a"]["orgadmin"])
    response = api_client.post(
        "/exports/run/?metadata_only=true",
        {"format": "json", "group_ids": [str(tenant_world["group_b"].id)]},
        format="json",
    )
    assert response.status_code in (200, 201, 400, 403)
    if response.status_code in (200, 201):
        meta = response.json()
        assert meta.get("traces_count", 0) == 0
