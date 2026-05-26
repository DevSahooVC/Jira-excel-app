"""Pure aggregation functions.

These work on an already-normalized list of issue dicts with lowercase keys:
    issue_type, assignee, status, story_points, sprint

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


def total_story_points_delivered(
    issues: Iterable[dict], *, exclude_bugs: bool = False
) -> tuple[float, int]:
    """Return (sum_story_points, issue_count) for delivered issues.

    If exclude_bugs is True, issues with issue_type Bug/Defect are skipped.
    """
    total = 0.0
    count = 0
    for it in issues:
        if not _is_delivered(it.get("status")):
            continue
        if exclude_bugs and _is_defect(it.get("issue_type")):
            continue
        sp = it.get("story_points")
        if sp is None:
            continue
        total += float(sp)
        count += 1
    return round(total, 2), count


def story_points_by_assignee(
    issues: Iterable[dict], *, exclude_bugs: bool = False
) -> list[dict]:
    """Story points delivered grouped by assignee, sorted desc by points.

    If exclude_bugs is True, issues with issue_type Bug/Defect are skipped
    from the SP aggregation. The bug_count / bug_story_points columns
    *always* reflect every Bug/Defect issue (any status) assigned to that
    person — they are unaffected by the exclude_bugs flag.
    """
    issues_list = list(issues)

    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    bug_counts: dict[str, int] = defaultdict(int)
    bug_sps: dict[str, float] = defaultdict(float)

    # SP aggregation (respects exclude_bugs / delivered filter)
    for it in issues_list:
        if not _is_delivered(it.get("status")):
            continue
        if exclude_bugs and _is_defect(it.get("issue_type")):
            continue
        sp = it.get("story_points")
        if sp is None:
            continue
        who = _assignee_display(it.get("assignee"))
        sums[who] += float(sp)
        counts[who] += 1

    # Bug aggregation (all statuses, all bugs)
    for it in issues_list:
        if not _is_defect(it.get("issue_type")):
            continue
        who = _assignee_display(it.get("assignee"))
        bug_counts[who] += 1
        sp = it.get("story_points")
        if sp is not None:
            bug_sps[who] += float(sp)

    rows = [
        {
            "assignee": who,
            "story_points": round(sums[who], 2),
            "issue_count": counts[who],
            "bug_count": bug_counts.get(who, 0),
            "bug_story_points": round(bug_sps.get(who, 0.0), 2),
        }
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


def unique_sprints(issues: Iterable[dict]) -> list[str]:
    """Return sorted list of unique, non-null sprint names found in the issues."""
    seen: set[str] = set()
    for it in issues:
        sprint = it.get("sprint")
        if sprint:
            seen.add(str(sprint).strip())
    return sorted(seen)


def aggregate_sprint(
    issues: list[dict], sprint: str | None, *, exclude_bugs: bool = False
) -> dict:
    """Return aggregation dict for a single sprint (or all issues if sprint is None)."""
    subset = issues if sprint is None else [it for it in issues if it.get("sprint") == sprint]
    total_sp, total_delivered = total_story_points_delivered(subset, exclude_bugs=exclude_bugs)
    return {
        "total_story_points_delivered": total_sp,
        "total_issues_delivered": total_delivered,
        "story_points_by_assignee": story_points_by_assignee(subset, exclude_bugs=exclude_bugs),
        "defects_by_assignee": defects_by_assignee(subset),
    }
