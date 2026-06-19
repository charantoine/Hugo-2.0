import pytest
from apps.accounts.models import Organisation, User, Role


@pytest.fixture
def org_a(db):
    return Organisation.objects.create(name="Org A")


@pytest.fixture
def org_b(db):
    return Organisation.objects.create(name="Org B")


@pytest.fixture
def user_org_a(org_a):
    u = User.objects.create_user(username="user_a", password="testpass", organisation=org_a, role=Role.LEARNER)
    u.set_password("testpass")
    u.save()
    return u


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()
