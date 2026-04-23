"""Generate sample_data/sample_jira_export.xlsx.

Run once to create the bundled sample file. Re-run to regenerate.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

ASSIGNEES = [
    "Ava Thompson",
    "Ben Carter",
    "Chloe Nguyen",
    "Diego Martinez",
    "Elena Rossi",
    "Farah Ahmed",
]
ISSUE_TYPES = ["Story", "Task", "Bug", "Sub-task"]
STATUSES_DONE = ["Done", "Closed", "Resolved"]
STATUSES_OPEN = ["To Do", "In Progress", "In Review", "Blocked"]
POINT_CHOICES = [1, 2, 3, 5, 8, 13]


def generate(num_rows: int = 60, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(1, num_rows + 1):
        issue_type = rng.choices(ISSUE_TYPES, weights=[4, 4, 3, 1])[0]
        # Defects are likelier to still be open
        if issue_type == "Bug":
            status = rng.choices(STATUSES_DONE + STATUSES_OPEN, weights=[3, 1, 1, 3, 3, 2, 2])[0]
        else:
            status = rng.choices(STATUSES_DONE + STATUSES_OPEN, weights=[4, 2, 2, 2, 2, 1, 1])[0]
        assignee = rng.choice(ASSIGNEES)
        # ~8 % unassigned
        if rng.random() < 0.08:
            assignee = ""
        # ~10 % missing story points (sub-tasks, defects)
        sp: float | str = rng.choice(POINT_CHOICES)
        if issue_type == "Sub-task" or rng.random() < 0.1:
            sp = ""
        rows.append(
            {
                "Issue key": f"SAMPLE-{100 + i}",
                "Summary": f"Example {issue_type.lower()} #{i}",
                "Issue Type": issue_type,
                "Status": status,
                "Assignee": assignee,
                "Reporter": rng.choice(ASSIGNEES),
                "Priority": rng.choice(["Low", "Medium", "High", "Highest"]),
                "Story Points": sp,
                "Sprint": rng.choice(["Sprint 42", "Sprint 43", "Sprint 44"]),
                "Created": "2026-03-01",
                "Updated": "2026-04-15",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "sample_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sample_jira_export.xlsx"
    df = generate()
    df.to_excel(out_path, index=False, sheet_name="Issues")
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
