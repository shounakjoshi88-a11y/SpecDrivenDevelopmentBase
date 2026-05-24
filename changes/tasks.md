# Implementation Tasks

- [x] Create specification and feature proposal under `changes/`
- [x] Implement `GET /reports/export` endpoint in `app/main.py`
- [x] Filter and sort using existing core query utilities
- [x] Sanitize datasets using `ReportPublic` mapping to eliminate internal field leaks
- [x] Stream valid CSV headers and rows using FastAPI StreamingResponse