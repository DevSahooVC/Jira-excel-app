"""FastAPI application entry point.

Endpoints:
    GET  /healthz         liveness
    GET  /api/sample      download the bundled sample_jira_export.xlsx
    POST /api/analyze     multipart upload of .xlsx -> 3 reports as JSON
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .aggregator import (
    defects_by_assignee,
    story_points_by_assignee,
    total_story_points_delivered,
)
from .models import AnalyzeResponse
from .parser import parse_jira_file

app = FastAPI(
    title="Jira Excel Reporter",
    description="Simple Jira reporting from an Excel extract.",
    version="0.1.0",
)

# Paths that work both in source checkout and in a PyInstaller onefile build.
_ROOT = Path(__file__).resolve().parent.parent
_BUNDLE_ROOT = Path(getattr(__import__("sys"), "_MEIPASS", _ROOT))  # type: ignore[attr-defined]

# Dev-friendly CORS — Vite dev server runs on 5173 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_PATH = _BUNDLE_ROOT / "sample_data" / "sample_jira_export.xlsx"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB hard cap

# If a built frontend exists, serve it (this enables single-exe packaging).
STATIC_DIR = _BUNDLE_ROOT / "app" / "static"
INDEX_HTML = STATIC_DIR / "index.html"

if STATIC_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(STATIC_DIR / "assets")),
        name="assets",
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sample")
def download_sample() -> FileResponse:
    if not SAMPLE_PATH.exists():
        raise HTTPException(status_code=404, detail="Sample file not bundled.")
    return FileResponse(
        SAMPLE_PATH,
        filename="sample_jira_export.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


ALLOWED_EXTENSIONS = (".xlsx", ".xlsm", ".csv", ".tsv")


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)) -> AnalyzeResponse:
    filename = file.filename or "upload.xlsx"
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"File must be one of: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")

    try:
        issues, warnings = parse_jira_file(contents, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    total_sp, total_delivered = total_story_points_delivered(issues)

    return AnalyzeResponse(
        total_story_points_delivered=total_sp,
        total_issues_delivered=total_delivered,
        story_points_by_assignee=story_points_by_assignee(issues),
        defects_by_assignee=defects_by_assignee(issues),
        filename=filename,
        total_rows=len(issues),
        warnings=warnings,
    )


@app.get("/", include_in_schema=False)
def ui_root() -> HTMLResponse:
    if INDEX_HTML.exists():
        return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))
    return HTMLResponse(
        "<h1>Jira Excel Reporter</h1><p>UI not built. Run the frontend dev server.</p>",
        status_code=200,
    )


@app.get("/{path:path}", include_in_schema=False)
def ui_spa_fallback(path: str) -> HTMLResponse:
    # Avoid intercepting API routes.
    if path.startswith("api") or path.startswith("healthz"):
        raise HTTPException(status_code=404, detail="Not found")
    if INDEX_HTML.exists():
        return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="UI not built")
