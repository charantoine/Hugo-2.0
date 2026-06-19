"""Evidence upload — EXIF stripping (ENC-CODE-04)."""
import io
import json

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoSession
from apps.referentials.models import Group


def _jpeg_with_exif() -> bytes:
    img = Image.new("RGB", (32, 32), color=(120, 40, 200))
    buf = io.BytesIO()
    exif = img.getexif()
    exif[0x010E] = "SECRET_GPS_MARKER_ENC"
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


@pytest.mark.django_db
def test_evidence_upload_strips_exif_from_jpeg(db):
    client = APIClient()
    org = Organisation.objects.create(name="Org EXIF")
    user_model = get_user_model()
    learner = user_model.objects.create_user(
        username="learner_exif",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G EXIF")
    session = HugoSession.objects.create(organisation=org, group=group, learner=learner)

    client.force_authenticate(user=learner)
    payload = _jpeg_with_exif()
    upload = SimpleUploadedFile("proof.jpg", payload, content_type="image/jpeg")
    response = client.post(
        "/evidence/",
        {"session_id": str(session.id), "file": upload},
        format="multipart",
    )
    assert response.status_code == 201
    assert response.data["meta"].get("exif_stripped") is True

    from django.core.files.storage import default_storage

    stored = default_storage.open(response.data["file_path"])
    reread = Image.open(stored)
    exif = reread.getexif()
    assert not exif or 0x010E not in exif
    stored.close()


@pytest.mark.django_db
def test_evidence_gps_only_in_meta_when_opt_in(db):
    client = APIClient()
    org = Organisation.objects.create(name="Org GPS")
    user_model = get_user_model()
    learner = user_model.objects.create_user(
        username="learner_gps",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G GPS")
    session = HugoSession.objects.create(organisation=org, group=group, learner=learner)

    client.force_authenticate(user=learner)
    upload = SimpleUploadedFile(
        "proof.jpg",
        _jpeg_with_exif(),
        content_type="image/jpeg",
    )
    response = client.post(
        "/evidence/",
        {
            "session_id": str(session.id),
            "file": upload,
            "gps_opt_in": "true",
            "gps_lat": "48.8566",
            "gps_lon": "2.3522",
        },
        format="multipart",
    )
    assert response.status_code == 201
    meta = response.data["meta"]
    assert meta.get("gps_opt_in") is True
    assert meta.get("gps_lat") == "48.8566"
    assert meta.get("gps_lon") == "2.3522"

    from django.core.files.storage import default_storage

    stored = default_storage.open(response.data["file_path"])
    reread = Image.open(stored)
    exif = reread.getexif()
    assert not exif or 0x010E not in exif
    stored.close()
