"""ドメイン例外（HTTP へのマッピングはプレゼンテーション層）。"""


class DomainError(Exception):
    """ドメイン基底例外。"""


class NotFoundError(DomainError):
    """リソースが存在しない。"""


class DomainValidationError(DomainError):
    """入力や状態がドメイン規則に合わない。"""


class ConflictError(DomainError):
    """競合（例: 同一面談で抽出が実行中）。"""


class InferenceError(DomainError):
    """構造化抽出に失敗した。"""
