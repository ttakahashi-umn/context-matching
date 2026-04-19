# syntax=docker/dockerfile:1
FROM python:3.14-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# コンテナで src を read-only マウントする場合でも動くよう、プロジェクトは非 editable インストール
RUN uv sync --frozen --no-dev --no-editable

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "talent_interview_profile_poc.main:app", "--host", "0.0.0.0", "--port", "8000"]
