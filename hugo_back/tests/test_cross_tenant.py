import pytest
from django.db import connection
from apps.accounts.models import Organisation
from apps.referentials.models import Group


@pytest.mark.django_db
def test_rls_org_a_cannot_see_org_b_groups(org_a, org_b):
    Group.objects.create(organisation=org_a, name="Group A")
    Group.objects.create(organisation=org_b, name="Group B")
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.organisation_id = %s", [str(org_a.id)])
    visible = list(Group.objects.filter(organisation_id=org_a.id).values_list("name", flat=True))
    assert "Group A" in visible
    all_groups = list(Group.objects.values_list("name", flat=True))
    assert "Group B" not in all_groups


@pytest.mark.django_db
def test_api_org_a_cannot_access_org_b_group(org_a, org_b, user_org_a, api_client):
    Group.objects.create(organisation=org_a, name="Group A")
    g_b = Group.objects.create(organisation=org_b, name="Group B")
    api_client.force_authenticate(user=user_org_a)
    r = api_client.get("/groups/")
    assert r.status_code == 200
    names = [x["name"] for x in r.json()]
    assert "Group B" not in names
    r2 = api_client.get("/groups/%s/" % g_b.id)
    assert r2.status_code == 404
