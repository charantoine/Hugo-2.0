#!/usr/bin/env python3
"""Oracle Encoors — cluster 8/10/11 runtime parity (EVAL1, O1, M1 memory, observability).

Usage (credentials via env, never commit secrets):
  export ENCOORS_BASE_URL=https://hugoback.encoors.com
  export ENCOORS_USERNAME=...
  export ENCOORS_PASSWORD=...
  export ENCOORS_ORACLE_OUT=docs-workspace/encoors_oracle_cluster11.generated.json
  python scripts/encoors_oracle.py

Optional:
  export ENCOORS_SESSION_ID=uuid  # skip session discovery
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


def _request(
    base: str,
    path: str,
    *,
    method: str = "GET",
    token: str | None = None,
    body: dict | None = None,
) -> tuple[int, Any]:
    url = base.rstrip("/") + path
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, raw[:500]
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = raw[:500]
        return exc.code, payload


def login(base: str, username: str, password: str) -> str | None:
    status, data = _request(base, "/auth/login/", method="POST", body={"username": username, "password": password})
    if status != 200 or not isinstance(data, dict):
        return None
    return data.get("access")


def main() -> int:
    base = os.environ.get("ENCOORS_BASE_URL", "https://hugoback.encoors.com")
    username = os.environ.get("ENCOORS_USERNAME", "")
    password = os.environ.get("ENCOORS_PASSWORD", "")
    session_id = os.environ.get("ENCOORS_SESSION_ID", "")

    results: list[dict[str, Any]] = []

    def record(name: str, path: str, status: int, note: str, detail: Any = None):
        results.append({"scenario": name, "path": path, "status": status, "note": note, "detail": detail})

    # Unauthenticated probes
    for path in (
        "/internal/hugo/analytics/conversation-summary/",
        f"/internal/hugo/sessions/00000000-0000-0000-0000-000000000001/observability/",
        f"/internal/hugo/sessions/00000000-0000-0000-0000-000000000001/d9bis/export/",
    ):
        status, _ = _request(base, path)
        record("probe", path, status, "unauthenticated")

    if not username or not password:
        out = {"base": base, "authenticated": False, "results": results, "message": "Set ENCOORS_USERNAME/PASSWORD for EVAL1/O1/M1"}
        serialized = json.dumps(out, indent=2, ensure_ascii=False)
        print(serialized)
        out_path = os.environ.get("ENCOORS_ORACLE_OUT", "")
        if out_path:
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(serialized)
        return 0

    token = login(base, username, password)
    if not token:
        record("auth", "/auth/login/", 401, "login failed")
        print(json.dumps({"base": base, "authenticated": False, "results": results}, indent=2))
        return 1

    record("auth", "/auth/login/", 200, "ok")

    # M1 — memory-summary (domain 20)
    if not session_id:
        status, sessions = _request(base, "/hugo/sessions/", token=token)
        if status == 200 and isinstance(sessions, list) and sessions:
            session_id = str(sessions[0].get("id", ""))
        elif status == 200 and isinstance(sessions, dict):
            rows = sessions.get("results") or []
            if rows:
                session_id = str(rows[0].get("id", ""))

    if session_id:
        mem_path = f"/hugo/sessions/{session_id}/memory-summary/"
        status, mem_data = _request(base, mem_path, token=token)
        detail: dict[str, Any] = {}
        if isinstance(mem_data, dict):
            sm = mem_data.get("session_memory") or {}
            detail = {
                "has_session_memory": bool(sm),
                "memory_scope": sm.get("memory_scope"),
                "has_theme_memories": "theme_memories" in mem_data,
                "theme_count": len(mem_data.get("theme_memories") or []),
            }
        record("M1", mem_path, status, "memory-summary", detail)

        obs_path = f"/internal/hugo/sessions/{session_id}/observability/"
        status, obs_data = _request(base, obs_path, token=token)
        record(
            "OBS_BASE",
            obs_path,
            status,
            "observability base",
            {"schema": obs_data.get("schema") if isinstance(obs_data, dict) else None},
        )

        d9_path = f"/internal/hugo/sessions/{session_id}/d9bis/export/"
        status, _ = _request(base, d9_path, token=token)
        record("D9BIS", d9_path, status, "d9bis export")

    # O1 — exports
    status, export_data = _request(
        base,
        "/exports/run/?metadata_only=true",
        method="POST",
        token=token,
        body={"format": "json"},
    )
    has_pivot = "evaluation_trace_pivot_v1" in json.dumps(export_data)
    record("O1", "/exports/run/", status, "export json metadata", {"has_pivot": has_pivot})

    status, _ = _request(base, "/quality/qualiopi/evidence-bundle/", method="POST", token=token, body={})
    record("O1", "/quality/qualiopi/evidence-bundle/", status, "bundle")

    # EVAL1 — session endpoints (reuse session_id)
    if session_id:
        for suffix, method in (
            ("evaluation-readiness/", "GET"),
            ("request-evaluation/", "POST"),
            ("generate-trace/", "POST"),
        ):
            path = f"/hugo/sessions/{session_id}/{suffix}"
            status, data = _request(base, path, method=method, token=token, body={} if method == "POST" else None)
            detail: dict[str, Any] = {"has_pivot": "evaluation_trace_pivot_v1" in json.dumps(data)}
            if isinstance(data, dict) and path.endswith("generate-trace/"):
                detail["keys"] = sorted(data.keys())[:12]
            record("EVAL1", path, status, method, detail)
    else:
        record("EVAL1", "/hugo/sessions/", 0, "no session_id available")

    out_path = os.environ.get("ENCOORS_ORACLE_OUT", "")
    ok_count = sum(1 for r in results if 200 <= int(r.get("status") or 0) < 300)
    fail_count = len(results) - ok_count
    payload = {
        "base": base,
        "authenticated": True,
        "session_id": session_id or None,
        "summary": {"total": len(results), "ok_2xx": ok_count, "non_2xx": fail_count},
        "results": results,
    }
    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    print(serialized)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(serialized)
    return 0


if __name__ == "__main__":
    sys.exit(main())
