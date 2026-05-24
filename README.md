# ⚡ Hyper-Speed Reports API 

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Track](https://img.shields.io/badge/Track-Vibe_Coding-8A2BE2)

> **Submission Context:** This branch represents the **Vibe Coding** track. It was engineered at terminal velocity utilizing AI assistance to prioritize raw execution speed, modern asynchronous memory optimization, and rapid feature delivery without the overhead of upfront enterprise documentation.

A blazing-fast FastAPI service that exposes a paginated `/reports` endpoint and an ultra-fast asynchronous streaming `/reports/export` endpoint backed by a deterministic in-memory dataset.

## ✨ Core Features & Optimizations

- **High-Velocity Export:** Implements a custom `AsyncGenerator` to yield CSV chunks on-the-fly, preventing memory bottlenecks on massive datasets.
- **Zero-Friction Execution:** Stripped of heavy bureaucratic middleware for pure, unadulterated performance.
- **Dynamic Formatting:** Leverages Python's native CSV serializers to handle complex string schemas effortlessly.

## 📂 Project Layout

```text
app/
├── __init__.py
├── data.py        # Seed dataset (120 rows, deterministic)
├── models.py      # Pydantic models — internal vs public
├── reports.py     # Filter / sort / pagination query layer
└── main.py        # ⚡ FastAPI HTTP layer (Optimized with Async Generators)
```

## 🚀 Quick Start

```bash
# 1. Setup the virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Launch the API
uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Liveness probe — returns `{"status": "operational"}`. |
| `GET` | `/reports` | Paginated list of reports with filtering and sorting. |
| `GET` | `/reports/export` | **[NEW]** High-performance Async CSV streaming export. |

### 🔍 Query Parameters (`/reports` & `/reports/export`)

| Parameter | Type | Default | Behavior |
| :--- | :--- | :--- | :--- |
| `status` | `enum` | `None` | Match exactly: `pending`, `approved`, `rejected`, `archived`. |
| `date_from` | `datetime (ISO)` | `None` | Lower bound on `created_at` (inclusive). |
| `date_to` | `datetime (ISO)` | `None` | Upper bound on `created_at` (inclusive). |
| `sort` | `string` | `"created_at"` | Target column for vector sorting. |
| `descending` | `bool` | `true` | Toggles sort direction. |
| `offset` | `int (>=0)` | `0` | Pagination index skip. *(Not applicable for export)* |
| `limit` | `int (1..200)`| `20` | Payload window size limit. *(Not applicable for export)* |