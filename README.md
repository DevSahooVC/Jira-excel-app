# Jira Excel Reporter

A lightweight reporting app for Jira data that works from an **Excel or CSV extract**
— no Jira API connection required. Built with FastAPI + React.

## What it shows

Upload a Jira extract and the app renders three reports as charts + tables:

1. **Total story points delivered** — sum of Story Points for issues whose
   Status is Done / Closed / Resolved.
2. **Story points delivered by team member** — same sum, grouped by Assignee.
3. **Defects assigned to each team member** — count of Bug/Defect rows grouped
   by Assignee (counts every defect regardless of status).

## Expected columns

Any Jira "Issue Navigator → Export" CSV/XLSX works. We look for:

| Canonical      | Matches (case-insensitive)                                              |
|----------------|-------------------------------------------------------------------------|
| `Issue Type`   | `Issue Type`, `Type`                                                    |
| `Assignee`     | `Assignee`, `Assignee Name`                                             |
| `Status`       | `Status`                                                                |
| `Story Points` | `Story Points`, `Story Point Estimate`, `Custom field (Story Points)`   |

Missing columns are handled gracefully:

- **No Status column** → Story/Task/Bug rows are assumed Done; Epic/Sub-task excluded.
- **No Assignee column or all blank** → per-person sections collapse to "Unassigned".
- A warnings banner in the UI discloses every fallback that was applied.

## Running it

You'll need two terminals: one for the API, one for the UI.

### Backend (FastAPI, port 8000)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
./run.sh                            # or: uvicorn app.main:app --reload
```

Swagger at <http://localhost:8000/docs>.

### Frontend (Vite + React, port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api/*` through to the backend.

## Tests

```bash
cd backend
PYTHONPATH=. pytest
```

11 unit tests cover the aggregator — including case-insensitive status
matching, blank assignees, and the "no Bugs" edge case.

## Project layout

```
jira-excel-app/
├── backend/
│   ├── app/
│   │   ├── main.py         FastAPI app + endpoints
│   │   ├── parser.py       xlsx/csv parsing + tolerant header matching
│   │   ├── aggregator.py   pure aggregation functions (3 reports)
│   │   └── models.py       Pydantic response models
│   ├── tests/
│   │   └── test_aggregator.py
│   ├── sample_data/
│   │   └── sample_jira_export.xlsx   (60 rows, realistic mix)
│   ├── generate_sample.py  regenerate the sample file
│   ├── requirements.txt
│   └── run.sh
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── styles.css
    │   └── components/
    │       ├── UploadForm.jsx
    │       └── ReportChart.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## API

| Method | Path            | Body                  | Purpose                                   |
|--------|-----------------|-----------------------|-------------------------------------------|
| GET    | `/healthz`      | —                     | Liveness                                  |
| GET    | `/api/sample`   | —                     | Download bundled sample_jira_export.xlsx  |
| POST   | `/api/analyze`  | multipart `file=...`  | Returns the 3 reports as JSON             |

`/api/analyze` response shape:

```json
{
  "total_story_points_delivered": 114.0,
  "total_issues_delivered": 25,
  "story_points_by_assignee": [
    {"assignee": "Elena Rossi", "story_points": 29.0, "issue_count": 3}
  ],
  "defects_by_assignee": [
    {"assignee": "Elena Rossi", "defect_count": 4}
  ],
  "filename": "sample_jira_export.xlsx",
  "total_rows": 60,
  "warnings": []
}
```

## Differences from the sister app (JiraQ)

This app reads a **static extract** and does simple aggregation. The JiraQ
backend one level up connects live to Jira Cloud, walks issue changelogs, and
does sprint-scoped attribution. Use JiraQ when you need live or
attribution-accurate numbers; use this one for quick reports off an Excel
export.
