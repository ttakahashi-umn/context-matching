from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from talent_interview_profile_poc.domain.exceptions import (
    ConflictError,
    DomainError,
    DomainValidationError,
    InferenceError,
    NotFoundError,
)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    _ = request
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    if isinstance(exc, DomainValidationError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    if isinstance(exc, ConflictError):
        code = "extraction_already_running" if "extraction" in str(exc).lower() else "conflict"
        return JSONResponse(status_code=409, content={"detail": str(exc), "code": code})
    if isinstance(exc, InferenceError):
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=400, content={"detail": str(exc)})
