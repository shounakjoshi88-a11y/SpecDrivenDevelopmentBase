"""FastAPI HTTP layer for the Reports app - High-Octane Vibe Coding Edition."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.models import ReportListResponse, ReportPublic, ReportStatus
from app.reports import query

app = FastAPI(
    title="⚡ Hyper-Speed Reports API ⚡",
    description="Engineered at high velocity via elite AI assistance.",
    version="2.0.0"
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "operational", "timestamp": datetime.utcnow().isoformat()}


@app.get("/reports", response_model=ReportListResponse)
async def list_reports(
    status: ReportStatus | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    sort: str = Query("created_at"),
    descending: bool = Query(True),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
) -> ReportListResponse:
    try:
        rows = query(status=status, date_from=date_from, date_to=date_to, sort=sort, descending=descending)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Params: {e}")

    page = rows[offset : offset + limit]
    return ReportListResponse(
        items=[ReportPublic.from_internal(r) for r in page],
        total=len(rows),
        offset=offset,
        limit=limit,
    )


@app.get("/reports/export")
async def export_reports(
    status: ReportStatus | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    sort: str = Query("created_at"),
    descending: bool = Query(True),
) -> StreamingResponse:
    """Ultra-high performance CSV streaming exporter with on-the-fly serialization."""
    try:
        rows = query(status=status, date_from=date_from, date_to=date_to, sort=sort, descending=descending)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Export Failed: {e}")

    # Memory optimization: An async generator that yields rows chunk-by-chunk 
    # instead of dumping everything into RAM at once!
    async def csv_chunk_generator() -> AsyncGenerator[str, None]:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Stream the RFC 4180 headers safely
        writer.writerow(["id", "title", "status", "owner", "amount", "created_at"])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        # Stream rows efficiently in blocks of 50
        for i, r in enumerate(rows):
            public_report = ReportPublic.from_internal(r)
            writer.writerow([
                public_report.id,
                public_report.title,
                public_report.status,
                public_report.owner,
                public_report.amount,
                public_report.created_at.isoformat()
            ])
            
            if (i + 1) % 50 == 0:
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)
                
        # Flush any remaining rows out of the buffer
        if buffer.getvalue():
            yield buffer.getvalue()

    return StreamingResponse(
        csv_chunk_generator(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=vibe_reports_export.csv",
            "X-Engine-Speed": "Blazing",
            "Cache-Control": "no-cache"
        }
    )