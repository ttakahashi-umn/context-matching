from __future__ import annotations

import json
from html import escape
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, Response

from talent_interview_profile_poc.application.services.export_service import ExportService
from talent_interview_profile_poc.presentation.deps import get_export_service

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/talents/{talent_id}.json")
def export_talent_json(
    talent_id: UUID,
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    payload = service.build_talent_export(talent_id)
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return Response(
        content=body,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="talent-{talent_id}.json"'},
    )


@router.get("/talents/{talent_id}.html", response_class=HTMLResponse)
def export_talent_html(
    talent_id: UUID,
    service: Annotated[ExportService, Depends(get_export_service)],
) -> HTMLResponse:
    payload = service.build_talent_export(talent_id)
    title = escape(str(payload["talent"]["display_name"]))
    interviews = payload["interviews"]
    snapshots = payload["profile_snapshots"]
    parts: list[str] = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'/>",
        f"<title>{title}</title></head><body>",
        f"<h1>{title}</h1>",
        "<h2>Interviews &amp; extraction runs</h2><ul>",
    ]
    for inv in interviews:
        iid = escape(str(inv["interview_session_id"]))
        parts.append(f"<li>Interview <code>{iid}</code><ul>")
        for run in inv["extraction_runs"]:
            rid = escape(str(run["extraction_run_id"]))
            tid = escape(str(run["template_version_id"]))
            parts.append(
                "<li>"
                f"Run <code>{rid}</code> template <code>{tid}</code> status "
                f"<strong>{escape(run['status'])}</strong> input_hash "
                f"<code>{escape(run['input_hash'])}</code>"
                "</li>"
            )
        parts.append("</ul></li>")
    parts.append("</ul><h2>Profile snapshots</h2><ul>")
    for s in snapshots:
        sid = escape(str(s["profile_snapshot_id"]))
        src = escape(str(s["source_extraction_run_id"]))
        parts.append(
            f"<li>Snapshot <code>{sid}</code> from extraction <code>{src}</code></li>"
        )
    parts.append("</ul></body></html>")
    return HTMLResponse("".join(parts))
