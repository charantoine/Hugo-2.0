"""Tutor-link permissions — transitional SUPERADMIN-only policy."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


@pytest.fixture
def link_world(db):
    org = Organisation.objects.create(name="TutorLink Org")
    superadmin = User.objects.create_user(
        username="tl_superadmin",
        password="pass",
        organisation=org,
        role=Role.SUPERADMIN,
    )
    orgadmin = User.objects.create_user(
        username="tl_orgadmin",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    tutor = User.objects.create_user(
        username="tl_tutor",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    learner = User.objects.create_user(
        username="tl_learner",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="TL Group")
    for user in (tutor, learner):
        GroupMembership.objects.create(organisation=org, group=group, user=user)
    return {
        "org": org,
        "group": group,
        "superadmin": superadmin,
        "orgadmin": orgadmin,
        "tutor": tutor,
        "learner": learner,
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_superadmin_can_create_tutor_link(link_world, api_client):
    api_client.force_authenticate(user=link_world["superadmin"])
    response = api_client.post(
        f"/groups/{link_world['group'].id}/tutor-links/",
        {"tutor": str(link_world["tutor"].id), "learner": str(link_world["learner"].id)},
        format="json",
    )
    assert response.status_code == 201
    assert TutorLearnerLink.objects.filter(
        group=link_world["group"],
        tutor=link_world["tutor"],
        learner=link_world["learner"],
    ).exists()


@pytest.mark.django_db
def test_orgadmin_cannot_create_tutor_link(link_world, api_client):
    api_client.force_authenticate(user=link_world["orgadmin"])
    response = api_client.post(
        f"/groups/{link_world['group'].id}/tutor-links/",
        {"tutor": str(link_world["tutor"].id), "learner": str(link_world["learner"].id)},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_tutor_cannot_create_tutor_link(link_world, api_client):
    api_client.force_authenticate(user=link_world["tutor"])
    response = api_client.post(
        f"/groups/{link_world['group'].id}/tutor-links/",
        {"tutor": str(link_world["tutor"].id), "learner": str(link_world["learner"].id)},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_superadmin_lists_all_tutor_links_in_group(link_world, api_client):
    TutorLearnerLink.objects.create(
        organisation=link_world["org"],
        group=link_world["group"],
        tutor=link_world["tutor"],
        learner=link_world["learner"],
    )
    api_client.force_authenticate(user=link_world["superadmin"])
    response = api_client.get(f"/groups/{link_world['group'].id}/tutor-links/")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_orgadmin_get_tutor_links_scoped_like_encadrant_not_admin(link_world, api_client):
    """ORGADMIN does not receive admin-wide tutor-link listing (transitional)."""
    TutorLearnerLink.objects.create(
        organisation=link_world["org"],
        group=link_world["group"],
        tutor=link_world["tutor"],
        learner=link_world["learner"],
    )
    api_client.force_authenticate(user=link_world["orgadmin"])
    response = api_client.get(f"/groups/{link_world['group'].id}/tutor-links/")
    assert response.status_code == 200
    assert response.json() == []
