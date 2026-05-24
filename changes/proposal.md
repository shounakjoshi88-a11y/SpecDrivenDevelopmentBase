# OpenSpec: Feature Proposal — Secure Asynchronous CSV Report Export Engine

## Document Metadata
- **Specification Version:** 1.2.0-REV2
- **Track:** Spec-Driven Development (SDD Submission)
- **Status:** APPROVED / IMPLEMENTED
- **Target Component:** `app.main` (FastAPI HTTP Layer Integration)
- **Security Classification:** Confidential / Controlled Financial Data Boundary

---

## 1. Executive Summary & Business Context
End-users require the capability to extract compiled data representations out of the `/reports` system for external reporting, downstream auditing, and local analytics inside spreadsheets. 

While the system already exposes a paginated JSON web ledger, pulling full raw datasets iteratively via pagination parameters introduces significant client-side overhead. This feature introduces a high-performance, single-query streaming endpoint (`GET /reports/export`) that matches all filtering and sorting dimensions currently available to the system, formatting the resulting data matrix as a downloadable document complying with standard data interchange formats.

---

## 2. High-Level Architectural Design & Core Pillars
The implementation of the export engine rests upon three non-negotiable architectural mandates:

### A. Strict Data Isolation & Anti-Leak Safeguards
The backing memory storage layer manages full operational internal models (`app.models.Report`) which possess fields labeled as strictly confidential:
1. `internal_id`: Back-office alphanumeric system hash used for database indexing and cross-ledger reconciliation.
2. `owner_email`: Personally Identifiable Information (PII) protected under global privacy compliance rules.

Under no operational context may these parameters cross the HTTP public network perimeter. The export engine must strictly decouple internal models from the transport text serialization layer by dynamically routing every item through the `ReportPublic.from_internal` domain mapper.

### B. High-Fidelity Data Serialization (RFC 4180 Alignment)
The application dataset contains complex character fields designed to pressure-test text escaping matrices. Notably, as documented in the data seed definitions (`app.data`), specific report entries feature titles containing embedded formatting anomalies:
* Example: `CSV with commas, "quotes" and newlines\nin the title`

To prevent field misalignment (where a comma shifts a column or a newline creates an unwanted row break), the endpoint must delegate formatting to Python's native `csv.writer` engine operating over an in-memory character stream (`io.StringIO`), which enforces standardized double-quote wrap encapsulation and escape-masking rules.

### C. Low-Memory Footprint via Dynamic Streaming
Rather than loading, formatting, and accumulating the entire generated string block in full inside server RAM before responding (which breaks scalability under larger row counts), the endpoint must stream chunks dynamically using FastAPI’s `StreamingResponse`. This establishes an iterative consumption flow over an in-memory buffer.

---

## 3. Web API Contract & Endpoint Specification

### HTTP Routing Details
- **Method:** `GET`
- **Path:** `/reports/export`

### Request Query Interceptor Interface
The engine captures and transparently forwards the full suite of downstream querying parameters directly to the standalone filtering module (`app.reports.query`):

| Parameter Name | Target Type | Validation / Defaults | Functional Enforcement |
| :--- | :--- | :--- | :--- |
| `status` | `ReportStatus` | Optional Enum | Filters rows by checking against target states. |
| `date_from` | `datetime` | Optional ISO-8601 | Lower boundary limit checking (Inclusive). |
| `date_to` | `datetime` | Optional ISO-8601 | Upper boundary limit checking (Inclusive). |
| `sort` | `string` | Default: `created_at` | Sorts key vector matching `id`, `title`, `status`, `owner`, `amount`, or `created_at`. |
| `descending` | `boolean` | Default: `true` | Changes ordering flow between ascending/descending sorting logic. |

### Response Transport Protocol
- **Content Type Header:** `text/csv; charset=utf-8`
- **Attachment Directive Header:** `Content-Disposition: attachment; filename=reports_export.csv`
- **Error Behavior:** Any out-of-bounds parameter inputs (e.g., passing an invalid column name to the sorting evaluator) will trigger a `ValueError` inside the core engine. The API layer must catch this error and wrap it cleanly in an explicit `HTTPException(status_code=400)` to notify the calling client of input formatting errors.