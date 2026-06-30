"""Auth: login, me, admin endpoints."""
import pytest
from django.contrib.auth import get_user_model
from apps.accounts.models import Organisation, Role

User = get_user_model()


@pytest.mark.django_db
def test_login_returns_tokens(org_a, api_client):
    u = User.objects.create_user(username="learner1", password="secret", organisation=org_a, role=Role.LEARNER)
    u.set_password("secret")
    u.save()
    response = api_client.post("/auth/login/", {"username": "learner1", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert data.get("user_id") == str(u.id)
    assert data.get("organisation_id") == str(org_a.id)


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    response = api_client.get("/auth/me/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_profile(org_a, user_org_a, api_client):
    api_client.force_authenticate(user=user_org_a)
    response = api_client.get("/auth/me/")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user_a"
    assert data["organisation_id"] == str(org_a.id)
    assert data["role"] == Role.LEARNER
