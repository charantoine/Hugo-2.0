import pytest
from django.urls import reverse

from apps.hugo.models import HugoMessage, HugoSession


@pytest.mark.django_db
def test_session_list_filters_by_message_content_and_favorites(
    api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_sess_filters",
        password="pass",
        organisation=organisation,
    )
    fav = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        is_favorite=True,
    )
    other = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        is_favorite=False,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=other,
        role=HugoMessage.Role.LEARNER,
        content="mot unique recherche radiateur xyz",
    )

    api_client.force_authenticate(user=learner)
    base = reverse("session_list_create")

    r_all = api_client.get(base)
    assert r_all.status_code == 200
    data = r_all.data
    rows = data if isinstance(data, list) else data.get("results", [])
    assert len(rows) >= 2

    r_q = api_client.get(base, {"q": "recherche radiateur"})
    assert r_q.status_code == 200
    rows_q = r_q.data if isinstance(r_q.data, list) else r_q.data.get("results", [])
    ids_q = {str(x["id"]) for x in rows_q}
    assert str(other.id) in ids_q
    assert str(fav.id) not in ids_q

    r_fav = api_client.get(base, {"favorites_only": "1"})
    assert r_fav.status_code == 200
    rows_f = r_fav.data if isinstance(r_fav.data, list) else r_fav.data.get("results", [])
    ids_f = {str(x["id"]) for x in rows_f}
    assert str(fav.id) in ids_f
    assert str(other.id) not in ids_f


@pytest.mark.django_db
def test_session_patch_favorite_returns_full_session(
    api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_fav_patch",
        password="pass",
        organisation=organisation,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        is_favorite=False,
    )
    api_client.force_authenticate(user=learner)
    url = reverse("session_detail", kwargs={"session_id": str(session.id)})
    r = api_client.patch(url, {"is_favorite": True}, format="json")
    assert r.status_code == 200
    assert r.data["is_favorite"] is True
    assert r.data["id"] == str(session.id)
    session.refresh_from_db()
    assert session.is_favorite is True
