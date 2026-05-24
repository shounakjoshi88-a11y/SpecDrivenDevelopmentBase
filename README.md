# 🛡️ Enterprise Reports API 

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Compliance](https://img.shields.io/badge/Compliance-RFC--4180-success)
![Security](https://img.shields.io/badge/Security-Strict-red)
![Track](https://img.shields.io/badge/Track-Spec_Driven-0078D4)

> **Submission Context:** This branch represents the **Spec-Driven Development (SDD)** track. It was engineered following strict, upfront architectural planning. Please refer to the `changes/` directory for the comprehensive `proposal.md` and `tasks.md` engineering logs.

A robust FastAPI service exposing secure paginated lookups and compliant CSV data extraction channels, backed by a deterministic ledger.

## 🔐 Security & Compliance Highlights

- **Data Isolation & PII Firewall:** Enforces strict sanitization via Pydantic model conversions (`ReportPublic.from_internal`) to guarantee `internal_id` and `owner_email` never cross the network perimeter.
- **RFC 4180 Adherence:** Utilizes standard `csv.writer` stream buffers to safely escape complex multi-line strings, embedded commas, and quotes.
- **Enterprise Observability:** Integrates standard execution logging and diagnostic error handling for enterprise auditing and traceability.

## 📂 Project Layout

```text
changes/           # 🛡️ SDD Technical Architecture & Planning
├── proposal.md    # Feature Proposal & OpenSpec Constraints
└── tasks.md       # Implementation Checklists & QA Verification Log

app/               # Application Source
├── __init__.py
├── data.py        # Seed dataset (120 rows, deterministic)
├── models.py      # Pydantic models (Security Boundaries)
├── reports.py     # Filter / sort / pagination query layer
└── main.py        # FastAPI HTTP layer (Enterprise logging & security)
```

## 🚀 Setup & Execution

```bash
# 1. Setup the virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Launch the API
uvicorn app.main:app --reload --port 8000
```

## 📡 API Contract

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe — returns `{"status": "ok"}`. |
| `GET` | `/reports` | Paginated list of reports with filtering and sorting. |
| `GET` | `/reports/export` | **[NEW]** Secure, sanitized CSV streaming export attachment. |

### 🔍 Core Query Parameters

| Parameter | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `status` | `enum` | `None` | Match exactly: `pending`, `approved`, `rejected`, `archived`. |
| `date_from` | `datetime (ISO)` | `None` | Lower bound on `created_at` (inclusive). |
| `date_to` | `datetime (ISO)` | `None` | Upper bound on `created_at` (inclusive). |
| `sort` | `string` | `"created_at"` | Target column for vector sorting. |
| `descending` | `bool` | `true` | Toggles sort direction. |
| `offset` | `int (>=0)` | `0` | Pagination index skip. *(Not applicable for export)* |
| `limit` | `int (1..200)`| `20` | Payload window size limit. *(Not applicable for export)* |