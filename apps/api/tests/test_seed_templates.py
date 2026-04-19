from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from talent_interview_profile_poc.infrastructure.persistence.database import dispose_engine, get_engine
from talent_interview_profile_poc.infrastructure.persistence.orm_models import Base
from talent_interview_profile_poc.main import app
from talent_interview_profile_poc.seed import SEED_IT_ENGINEER_VERSION


@pytest.fixture
def client() -> TestClient:
    dispose_engine()
    Base.metadata.drop_all(bind=get_engine())
    Base.metadata.create_all(bind=get_engine())
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    dispose_engine()


def test_seed_it_engineer_template_registered(client: TestClient) -> None:
    r = client.get("/templates")
    assert r.status_code == 200
    rows = r.json()
    labels = {row["version_label"] for row in rows}
    assert SEED_IT_ENGINEER_VERSION in labels
    seed_row = next(row for row in rows if row["version_label"] == SEED_IT_ENGINEER_VERSION)
    assert seed_row["purpose"]
    assert "IT エンジニア" in seed_row["purpose"]
