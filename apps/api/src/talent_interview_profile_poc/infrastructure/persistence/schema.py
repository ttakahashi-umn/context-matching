"""DB スキーマ初期化（PoC は create_all）。"""

from pathlib import Path

from sqlalchemy.engine.url import make_url

from talent_interview_profile_poc.infrastructure.persistence.database import get_engine
from talent_interview_profile_poc.infrastructure.persistence.orm_models import Base
from talent_interview_profile_poc.settings import database_url


def init_db() -> None:
    url = make_url(database_url())
    if url.drivername.startswith("sqlite") and url.database and url.database != ":memory:":
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=get_engine())
