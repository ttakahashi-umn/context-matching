from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talent_interview_profile_poc.infrastructure.persistence.database import dispose_engine, get_engine
from talent_interview_profile_poc.infrastructure.persistence.orm_models import Base
from talent_interview_profile_poc.main import app


@pytest.fixture
def client() -> TestClient:
    dispose_engine()
    Base.metadata.drop_all(bind=get_engine())
    Base.metadata.create_all(bind=get_engine())
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    dispose_engine()


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_talent_interview_template_extract_merge_chain(client: TestClient) -> None:
    r = client.post("/talents", json={"display_name": "Alice"})
    assert r.status_code == 201
    talent_id = r.json()["id"]

    r = client.post(f"/talents/{talent_id}/interviews", json={"transcript_text": "面談: Python とチームワークについて話した。"})
    assert r.status_code == 201
    interview_id = r.json()["interview_session_id"]

    yaml_text = """
version: "1.0.0-poc"
fields:
  summary: string
"""
    r = client.post("/templates", json={"yaml_text": yaml_text})
    assert r.status_code == 201
    template_id = r.json()["template_version_id"]

    r = client.post(
        "/extractions",
        json={"interview_session_id": interview_id, "template_version_id": template_id},
    )
    assert r.status_code == 201
    run_id = r.json()["extraction_run_id"]

    r = client.get(f"/extractions/{run_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    assert r.json()["result_json"] is not None

    r = client.post(
        "/profiles/merge",
        json={"talent_id": talent_id, "extraction_run_id": run_id},
    )
    assert r.status_code == 201
    assert "skills" in r.json()["merged_profile_json"]

    r = client.get(f"/talents/{talent_id}")
    assert r.status_code == 200
    assert r.json()["latest_profile_json"] is not None

    r = client.get(f"/talents/{talent_id}/profile/history")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get(f"/exports/talents/{talent_id}.json")
    assert r.status_code == 200
    export = r.json()
    assert export["talent"]["id"] == talent_id
    assert any(er["extraction_runs"] for er in export["interviews"])


def test_invalid_template_yaml(client: TestClient) -> None:
    r = client.post("/templates", json={"yaml_text": "not: yaml: ["})
    assert r.status_code == 422
