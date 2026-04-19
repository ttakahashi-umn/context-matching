from __future__ import annotations

import os
import tempfile


def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
    """パッケージ import より前にテスト用 SQLite URL を固定する（未指定時のみ）。"""
    _ = config
    if os.environ.get("TIP_DATABASE_URL"):
        return
    d = tempfile.mkdtemp(prefix="tip-poc-test-")
    os.environ["TIP_DATABASE_URL"] = f"sqlite+pysqlite:///{os.path.join(d, 'test.db')}"
