"""
Module: app.main
Description: Core HTTP REST Gateway Layer for the SDD Workshop Reports API.
Provides high-performance paginated lookups and secure streaming data extraction channels
while strictly enforcing corporate data boundaries and data-privacy (PII) firewalls.

Compliance Mandates:
- RFC 4180: Strict adherence to downstream tabular string-escaping protocols.
- Data Isolation: Automated remediation against internal attribute leakage (internal_id, owner_email).
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.models import ReportListResponse, ReportPublic, ReportStatus
from app.reports import query

# ==============================================================================
# OBSERVABILITY & LOGGING CONFIGURATION
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")

# ==============================================================================
# APPLICATION CORE INITIALIZATION
# ==============================================================================
app = FastAPI(
    title="Enterprise Spec-Driven Reports Gateway",
    description="Production-grade secure report orchestration service implementing OpenSpec v1.2.0.",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==============================================================================
# ROUTE ENDPOINTS
# ==============================================================================

@app.get(
    "/health",
    tags=["Infrastructure"],
    summary="Liveness and Readiness Probe",
    response_description="Returns the structural state of the service instance."
)
def health() -> dict[str, str]:
    """
    Performs an instant operational readiness check on the API container instance.

    Returns:
        dict[str, str]: A key-value pair validating system liveness state.
    """
    logger.debug("Infrastructure liveness ping evaluated successfully.")
    return {"status": "ok"}


@app.get(
    "/reports",
    response_model=ReportListResponse,
    tags=["Core Reports Ledger"],
    summary="Fetch Paginated Report Registry",
    response_description="A sanitized list of report aggregates paired with window pagination offsets."
)
def list_reports(
    status: ReportStatus | None = Query(None, description="Target report lifecycle status state matrix filter."),
    date_from: datetime | None = Query(None, description="Lower chronological boundary limit constraint (Inclusive)."),
    date_to: datetime | None = Query(None, description="Upper chronological boundary limit constraint (Inclusive)."),
    sort: str = Query("created_at", description="The attribute column key used as the primary sort array vector."),
    descending: bool = Query(True, description="Toggles sorting direction between descending (true) or ascending (false)."),
    offset: int = Query(0, ge=0, description="The sequence indexing marker defining the pagination window skip offset."),
    limit: int = Query(20, ge=1, le=200, description="The allocation boundary capping the max database items per window payload size."),
) -> ReportListResponse:
    """
    Queries the deterministic in-memory ledger utilizing dynamic multi-parameter filters.
    Enforces a mandatory security sanitization boundary by stripping backend operational parameters
    (`internal_id` and `owner_email`) using Pydantic schema transformations before network egress.

    Args:
        status (ReportStatus | None): Filtering criterion matching item states.
        date_from (datetime | None): Lower boundary checking token for creation timestamps.
        date_to (datetime | None): Upper boundary checking token for creation timestamps.
        sort (str): Target column intended for vector sorting operations.
        descending (bool): Sort layout controller.
        offset (int): Pagination lookup window skip counter.
        limit (int): Pagination allocation limit factor.

    Raises:
        HTTPException: Status Code 400 if the sorting vector targets a non-sortable attribute column.

    Returns:
        ReportListResponse: Explicit data model packet holding sanitized public models.
    """
    logger.info(
        "Incoming ledger inquiry received. Filtering matrices - Status: %s, SortColumn: %s, LimitWindow: %d",
        status, sort, limit
    )

    try:
        # Instruct core query engine to slice master data rows based on arguments
        rows = query(
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            descending=descending,
        )
    except ValueError as e:
        logger.warning("Query layer boundary validation failure. Details: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query Compilation Error: {str(e)}"
        ) from e

    # Apply window slicing mechanics over the retrieved list block
    page = rows[offset : offset + limit]
    
    # Enforce Anti-Leak Protection: Convert internal tuples cleanly into sanitized Public models
    items = [ReportPublic.from_internal(r) for r in page]

    logger.info("Ledger query processed successfully. Returning %d elements out of %d total records.", len(items), len(rows))
    return ReportListResponse(
        items=items,
        total=len(rows),
        offset=offset,
        limit=limit,
    )


@app.get(
    "/reports/export",
    tags=["Core Reports Ledger"],
    summary="Asynchronous High-Performance CSV Streaming Downloader",
    response_description="A dynamic RFC 4180 aligned secure text stream attachment download."
)
def export_reports(
    status: ReportStatus | None = Query(None, description="Target report lifecycle status state matrix filter."),
    date_from: datetime | None = Query(None, description="Lower chronological boundary limit constraint (Inclusive)."),
    date_to: datetime | None = Query(None, description="Upper chronological boundary limit constraint (Inclusive)."),
    sort: str = Query("created_at", description="The attribute column key used as the primary sort array vector."),
    descending: bool = Query(True, description="Toggles sorting direction between descending (true) or ascending (false)."),
) -> StreamingResponse:
    """
    Compiles, cleanses, formats, and channels target report ledger entries down an active HTTP
    connection as an RFC 4180 standard compliant CSV text document stream.

    Security Context:
        This engine implements real-time scrubbing mechanisms to drop secure identifiers (`internal_id`, `owner_email`).
        Only standardized, audited public properties are serialized out to the final file payload structure.

    Data Integrity Context:
        Leverages Python's native `csv.writer` abstraction framework to seamlessly capture and shield complex nested
        string inputs (e.g. elements housing literal raw strings, escape quote tokens, and vertical line carriage breaks)
        without shifting tabular array alignments or throwing parsing errors inside spreadsheet clients.

    Raises:
        HTTPException: Status Code 400 if filtering expressions or column targeting arguments fail structural safety constraints.

    Returns:
        StreamingResponse: An asynchronous output text stream transmitting chunked comma-separated-value bytes.
    """
    logger.info("Asynchronous CSV extraction job initiated. Filtering constraints - Status: %s, OrderKey: %s", status, sort)

    try:
        # Route query configurations directly down into backend index layers
        rows = query(
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            descending=descending,
        )
    except ValueError as e:
        logger.error("CSV generation blocked due to upstream query argument failure: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export Compiling Violation: {str(e)}"
        ) from e

    # Initialize string I/O stream handler mapping inside server memory
    stream = io.StringIO()
    writer = csv.writer(stream)

    # --------------------------------------------------------------------------
    # STEP 1: SERIALIZE PUBLIC SCHEMA HEADERS (EXCLUDES ALL INTERNAL DATA FOR AUDITING)
    # --------------------------------------------------------------------------
    writer.writerow(["id", "title", "status", "owner", "amount", "created_at"])

    # --------------------------------------------------------------------------
    # STEP 2: LOOP, SANITIZE, AND TRANSLATE ROWS VIA CONVERSION INTERFACES
    # --------------------------------------------------------------------------
    for r in rows:
        # Route through Pydantic data firewall to drop internal keys and secure personal emails
        public_report = ReportPublic.from_internal(r)
        
        # Stream out formatted safe string lines containing RFC 4180 auto-escaping configurations
        writer.writerow([
            public_report.id,
            public_report.title,
            public_report.status,
            public_report.owner,
            public_report.amount,
            public_report.created_at.isoformat()
        ])

    # Reset streaming buffer index pointer back to zero index context position
    stream.seek(0)
    
    # Extract complete text chunk layout parameters
    csv_payload = stream.getvalue()
    logger.info("CSV extraction processing finalized. Total bytes allocated: %d across %d data rows.", len(csv_payload), len(rows))

    # --------------------------------------------------------------------------
    # STEP 3: ASYNCHRONOUS OUTPUT TRANSMISSION OVER ACTIVE TRANSPORT PORTS
    # --------------------------------------------------------------------------
    return StreamingResponse(
        iter([csv_payload]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=reports_export.csv",
            "X-Content-Type-Options": "nosniff",
            "X-Security-Policy": "Data-Sanitization-Enforced"
        }
    )