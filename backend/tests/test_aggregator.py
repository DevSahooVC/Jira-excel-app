"""Unit tests for the pure aggregator functions."""
from __future__ import annotations

import pytest

from app.aggregator import (
    defects_by_assignee,
    story_points_by_assignee,
    total_story_points_delivered,
)


def _issue(issue_type="Story", assignee="Ava", status="Done", story_points=3):
    return {
        "issue_type": issue_type,
        "assignee": assignee,
        "status": status,
        "story_points": story_points,
    }


# ---------------------------------------------------------------------------
# total_story_points_delivered
# ---------------------------------------------------------------------------


def test_total_sums_only_delivered_rows():
    issues = [
        _issue(story_points=3, status="Done"),
        _issue(story_points=5, status="In Progress"),
        _issue(story_points=2, status="Closed"),
    ]
    total, count = total_story_points_delivered(issues)
    assert total == 5
    assert count == 2


def test_total_status_match_is_case_insensitive():
    issues = [_issue(status="done", story_points=3), _issue(status="RESOLVED", story_points=2)]
    total, count = total_story_points_delivered(issues)
    assert total == 5
    assert count == 2


def test_total_ignores_rows_without_story_points():
    issues = [_issue(status="Done", story_points=None), _issue(status="Done", story_points=8)]
    total, count = total_story_points_delivered(issues)
    assert total == 8
    assert count == 1


def test_total_on_empty_input():
    total, count = total_story_points_delivered([])
    assert total == 0
    assert count == 0


# ---------------------------------------------------------------------------
# story_points_by_assignee
# ---------------------------------------------------------------------------


def test_sp_by_assignee_groups_and_sorts_desc():
    issues = [
        _issue(assignee="Ava", story_points=3),
        _issue(assignee="Ben", story_points=5),
        _issue(assignee="Ava", story_points=8),
        _issue(assignee="Ben", story_points=1, status="In Progress"),  # not delivered
    ]
    rows = story_points_by_assignee(issues)
    assert rows[0] == {"assignee": "Ava", "story_points": 11, "issue_count": 2}
    assert rows[1] == {"assignee": "Ben", "story_points": 5, "issue_count": 1}


def test_sp_by_assignee_treats_blank_as_unassigned():
    issues = [
        _issue(assignee="", story_points=3),
        _issue(assignee=None, story_points=2),
        _issue(assignee="   ", story_points=1),
    ]
    rows = story_points_by_assignee(issues)
    assert rows == [{"assignee": "Unassigned", "story_points": 6, "issue_count": 3}]


def test_sp_by_assignee_empty_when_no_delivered():
    issues = [_issue(status="In Progress", story_points=5)]
    assert story_points_by_assignee(issues) == []


# ---------------------------------------------------------------------------
# defects_by_assignee
# ---------------------------------------------------------------------------


def test_defects_counts_bug_and_defect_types():
    issues = [
        _issue(issue_type="Bug", assignee="Ava"),
        _issue(issue_type="Defect", assignee="Ava"),
        _issue(issue_type="Story", assignee="Ben"),  # ignored
    ]
    rows = defects_by_assignee(issues)
    assert rows == [{"assignee": "Ava", "defect_count": 2}]


def test_defects_counts_regardless_of_status():
    """Defect report counts all defects, delivered or not."""
    issues = [
        _issue(issue_type="Bug", assignee="Ava", status="Done"),
        _issue(issue_type="Bug", assignee="Ava", status="In Progress"),
        _issue(issue_type="Bug", assignee="Ben", status="To Do"),
    ]
    rows = defects_by_assignee(issues)
    assert {"assignee": "Ava", "defect_count": 2} in rows
    assert {"assignee": "Ben", "defect_count": 1} in rows


def test_defects_empty_when_no_bugs():
    issues = [_issue(issue_type="Story"), _issue(issue_type="Task")]
    assert defects_by_assignee(issues) == []


def test_defects_sorts_desc_by_count():
    issues = [
        _issue(issue_type="Bug", assignee="Solo"),
        _issue(issue_type="Bug", assignee="Busy"),
        _issue(issue_type="Bug", assignee="Busy"),
        _issue(issue_type="Bug", assignee="Busy"),
    ]
    rows = defects_by_assignee(issues)
    assert rows[0]["assignee"] == "Busy"
    assert rows[0]["defect_count"] == 3
    assert rows[1]["assignee"] == "Solo"
