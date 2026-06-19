"""Evidence upload media handling — strip EXIF by default, GPS opt-in in meta only."""
from __future__ import annotations

import io
import os

from PIL import Image


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif"}


def is_image_upload(filename: str) -> bool:
    ext = os.path.splitext(str(filename or ""))[-1].lower()
    return ext in _IMAGE_EXTENSIONS


def strip_image_metadata(file_obj) -> io.BytesIO:
    """
    Return a new in-memory file with pixel data preserved and EXIF/metadata removed.
    Non-image uploads are returned unchanged (rewound).
    """
    name = getattr(file_obj, "name", "") or ""
    if not is_image_upload(name):
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        return file_obj

    img = Image.open(file_obj)
    img.load()
    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.getdata()))

    output = io.BytesIO()
    fmt = (img.format or "JPEG").upper()
    if fmt in {"JPEG", "JPG"}:
        clean.save(output, format="JPEG", quality=92)
    elif fmt == "PNG":
        clean.save(output, format="PNG")
    elif fmt == "WEBP":
        clean.save(output, format="WEBP", quality=92)
    else:
        clean.save(output, format=img.format or "PNG")
    output.seek(0)
    return output


def evidence_meta_from_request(data) -> dict:
    gps_opt_in = str(data.get("gps_opt_in", "")).lower() in {"1", "true", "yes", "on"}
    meta = {"gps_opt_in": gps_opt_in, "exif_stripped": True}
    if gps_opt_in and data.get("gps_lat") is not None and data.get("gps_lon") is not None:
        meta["gps_lat"] = data.get("gps_lat")
        meta["gps_lon"] = data.get("gps_lon")
    return meta
