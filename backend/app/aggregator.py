"""Pure aggregation functions.

These work on an already-normalized list of issue dicts with lowercase keys:
    issue_type, assignee, status, story_points

Every report function is side-effect free and deterministic so it can be
unit-tested without the FastAPI layer.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

# Statuses that count as "delivered" per product decision.
DELIVERED_STATUSES = {"done", "closed", "resolved"}

# Issue types we consider defects.
DEFECT_TYPES = {"bug", "defect"}

UNASSIGNED_LABEL = "Unassigned"


def _is_delivered(status: str | None) -> bool:
    if not status:
        return False
    return status.strip().lower() in DELIVERED_STATUSES


def _is_defect(issue_type: str | None) -> bool:
    if not issue_type:
        return False
    return issue_type.strip().lower() in DEFECT_TYPES


def _assignee_display(name: str | None) -> str:
    if not name or not str(name).strip():
        return UNASSIGNED_LABEL
    return str(name).strip()


def total_story_points_delivered(issues: Iterable[dict]) -> tuple[float, int]:
    """Return (sum_story_points, issue_count) for delivered issues."""
    total = 0.0
    count = 0
    for it in issues:
        if not _is_delivered(it.get("status")):
            continue
        sp = it.get("story_points")
        if sp is None:
            continue
        total += float(sp)
        count += 1
    return round(total, 2), count


def story_points_by_assignee(issues: Iterable[dict]) -> list[dict]:
    """Story points delivered grouped by assignee, sorted desc by points."""
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for it in issues:
        if not _is_delivered(it.get("status")):
            continue
        sp = it.get("story_points")
        if sp is None:
            continue
        who = _assignee_display(it.get("assignee"))
        sums[who] += float(sp)
        counts[who] += 1
    rows = [
        {"assignee": who, "story_points": round(sums[who], 2), "issue_count": counts[who]}
        for who in sums
    ]
    rows.sort(key=lambda r: (-r["story_points"], r["assignee"]))
    return rows


def defects_by_assignee(issues: Iterable[dict]) -> list[dict]:
    """Count of defects (Bug/Defect issue type) grouped by assignee.

    Counts *all* defects regardless of status — the product requirement is
    'defects assigned to each team member', not 'defects they resolved'.
    """
    counts: dict[str, int] = defaultdict(int)
    for it in issues:
        if not _is_defect(it.get("issue_type")):
            continue
        who = _assignee_display(it.get("assignee"))
        counts[who] += 1
    rows = [{"assignee": who, "defect_count": n} for who, n in counts.items()]
    rows.sort(key=lambda r: (-r["defect_count"], r["assignee"]))
    return rows
