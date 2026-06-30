import pytest
from django.urls import reverse

from apps.accounts.models import Organisation, User
from apps.referentials.models import Referential, ReferentialItem, Group, ReferentialConfig


@pytest.mark.django_db
def test_referential_list_returns_org_items(api_client):
    org = Organisation.objects.create(name="Org A")
    other_org = Organisation.objects.create(name="Org B")
    user = User.objects.create_user(username="u1", password="pass", organisation=org)
    r1 = Referential.objects.create(organisation=org, name="R1", source_ref="RNCP1")
    ReferentialItem.objects.create(
        organisation=org,
        referential=r1,
        code="C1",
        title="Comp 1",
    )
    Referential.objects.create(organisation=other_org, name="R2", source_ref="RNCP2")

    api_client.force_authenticate(user=user)
    url = reverse("referential_list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "R1"
    assert data[0]["items_count"] == 1


@pytest.mark.django_db
def test_referential_config_get_and_put(api_client):
    org = Organisation.objects.create(name="Org A")
    user = User.objects.create_user(username="u1", password="pass", organisation=org)
    group = Group.objects.create(organisation=org, name="G1")
    ref = Referential.objects.create(organisation=org, name="R1", source_ref="RNCP1")

    api_client.force_authenticate(user=user)
    url = reverse("referential_config", kwargs={"group_id": group.id})

    # Initially empty
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.json() == {}

    # Set config
    resp = api_client.put(url, {"referential_id": str(ref.id)}, format="json")
    assert resp.status_code == 200
    cfg_id = resp.json()["id"]
    assert ReferentialConfig.objects.filter(id=cfg_id, group=group, referential=ref).exists()

    # Get populated config
    resp = api_client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["referential"]["id"] == str(ref.id)
    assert data["referential"]["name"] == ref.name

