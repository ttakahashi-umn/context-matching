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
    r = client.post(
        "/talents",
        json={
            "family_name": "山田",
            "given_name": "太郎",
            "family_name_kana": "やまだ",
            "given_name_kana": "たろう",
        },
    )
    assert r.status_code == 201
    talent_id = r.json()["id"]

    r = client.post(f"/talents/{talent_id}/interviews", json={"transcript_text": "面談: Python とチームワークについて話した。"})
    assert r.status_code == 201
    interview_id = r.json()["interview_session_id"]

    yaml_text = """
version: "1.0.0-poc"
purpose: "結合テスト用の最小テンプレ"
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
    assert export["talent"]["family_name"] == "山田"
    assert export["talent"]["display_label"] == "山田 太郎"
    assert any(er["extraction_runs"] for er in export["interviews"])


def test_invalid_template_yaml(client: TestClient) -> None:
    r = client.post("/templates", json={"yaml_text": "not: yaml: ["})
    assert r.status_code == 422


def test_template_requires_purpose_in_yaml(client: TestClient) -> None:
    r = client.post(
        "/templates",
        json={"yaml_text": 'version: "x"\nfields: {a: 1}\n'},
    )
    assert r.status_code == 422


def test_template_patch_updates_yaml(client: TestClient) -> None:
    yaml_a = 'version: "patch-v"\npurpose: "更新前"\nfields:\n  a: 1\n'
    r = client.post("/templates", json={"yaml_text": yaml_a})
    assert r.status_code == 201
    tid = r.json()["template_version_id"]

    yaml_b = 'version: "patch-v"\npurpose: "更新後"\nfields:\n  a: 2\n'
    r2 = client.patch(f"/templates/{tid}", json={"yaml_text": yaml_b})
    assert r2.status_code == 200
    body = r2.json()
    assert body["purpose"] == "更新後"
    assert body["yaml_text"] == yaml_b

    r3 = client.get(f"/templates/{tid}")
    assert r3.status_code == 200
    assert r3.json()["purpose"] == "更新後"


def test_template_patch_version_label_conflict(client: TestClient) -> None:
    r1 = client.post(
        "/templates",
        json={"yaml_text": 'version: "label-one"\npurpose: "p1"\nfields: {x: 1}\n'},
    )
    r2 = client.post(
        "/templates",
        json={"yaml_text": 'version: "label-two"\npurpose: "p2"\nfields: {x: 2}\n'},
    )
    assert r1.status_code == 201 and r2.status_code == 201
    id1 = r1.json()["template_version_id"]

    r = client.patch(
        f"/templates/{id1}",
        json={"yaml_text": 'version: "label-two"\npurpose: "ぶつける"\nfields: {x: 3}\n'},
    )
    assert r.status_code == 409
