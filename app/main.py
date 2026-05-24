"""FastAPI HTTP layer for the Reports app."""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query

from app.models import ReportListResponse, ReportPublic, ReportStatus
from app.reports import query

app = FastAPI(title="SDD Workshop — Reports API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/reports", response_model=ReportListResponse)
def list_reports(
    status: ReportStatus | None = Query(None, description="Filter by status"),
    date_from: datetime | None = Query(None, description="Lower bound on created_at (inclusive)"),
    date_to: datetime | None = Query(None, description="Upper bound on created_at (inclusive)"),
    sort: str = Query("created_at", description="Sort field"),
    descending: bool = Query(True, description="Sort descending"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
) -> ReportListResponse:
    """Return a paginated list of reports.

    Public fields only — `internal_id` and `owner_email` are stripped via
    `ReportPublic.from_internal`.
    """

    try:
        rows = query(
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            descending=descending,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    page = rows[offset : offset + limit]
    return ReportListResponse(
        items=[ReportPublic.from_internal(r) for r in page],
        total=len(rows),
        offset=offset,
        limit=limit,
    )

    import csv
import io
from fastapi.responses import StreamingResponse

@app.get("/reports/export")
def export_reports(
    status: ReportStatus | None = Query(None, description="Filter by status"),
    date_from: datetime | None = Query(None, description="Lower bound on created_at (inclusive)"),
    date_to: datetime | None = Query(None, description="Upper bound on created_at (inclusive)"),
    sort: str = Query("created_at", description="Sort field"),
    descending: bool = Query(True, description="Sort descending"),
) -> StreamingResponse:
    """Export filtered and sorted reports as a CSV file.
    
    Ensures security compliance by stripping internal_id and owner_email.
    """
    try:
        # Fetch the reports matching filters and sorting rules
        rows = query(
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            descending=descending,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create an in-memory string buffer for the CSV data
    stream = io.StringIO()
    writer = csv.writer(stream)
    
    # Write CSV Header (Public fields only!)
    writer.writerow(["id", "title", "status", "owner", "amount", "created_at"])
    
    # Write rows safely mapping through ReportPublic to strip sensitive data
    for r in rows:
        public_report = ReportPublic.from_internal(r)
        writer.writerow([
            public_report.id,
            public_report.title,
            public_report.status,
            public_report.owner,
            public_report.amount,
            public_report.created_at.isoformat()
        ])
        
    # Rewind buffer pointer to start
    stream.seek(0)
    
    # Return as a downloadable CSV stream attachment
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reports_export.csv"}
    )
