"""アプリケーション設定（環境変数で上書き可能）。"""

import os
from pathlib import Path

# 面談テキスト最大サイズ（バイト）
MAX_TRANSCRIPT_BYTES: int = int(os.environ.get("TIP_MAX_TRANSCRIPT_BYTES", "524288"))


def default_sqlite_url() -> str:
    _default_db = Path(os.environ.get("TIP_DATABASE_PATH", "data/poc.db")).resolve()
    return f"sqlite+pysqlite:///{_default_db}"


def database_url() -> str:
    """テストでは `TIP_DATABASE_URL` を先に設定してからパッケージを import する。"""
    return os.environ.get("TIP_DATABASE_URL") or default_sqlite_url()
