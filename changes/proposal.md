# Proposal: Secure CSV Export Endpoint

## Problem Statement
Users need a way to export the filtered and sorted reports as a downloadable CSV file. However, according to system rules (`app/models.py`), internal-only data fields (`internal_id` and `owner_email`) must never be leaked to public endpoints.

## Proposed Solution
Expose a new `GET /reports/export` endpoint in `app/main.py`. This endpoint will accept the standard filtering and sorting parameters, fetch the database rows using `app.reports.query`, map the records cleanly through `ReportPublic.from_internal` to securely strip sensitive properties, and stream a compliant RFC 4180 CSV file attachment.