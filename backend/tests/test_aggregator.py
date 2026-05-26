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
    assert rows[0] == {
        "assignee": "Ava",
        "story_points": 11,
        "issue_count": 2,
        "bug_count": 0,
        "bug_story_points": 0.0,
        "defect_density": 0.0,
    }
    assert rows[1] == {
        "assignee": "Ben",
        "story_points": 5,
        "issue_count": 1,
        "bug_count": 0,
        "bug_story_points": 0.0,
        "defect_density": 0.0,
    }


def test_sp_by_assignee_treats_blank_as_unassigned():
    issues = [
        _issue(assignee="", story_points=3),
        _issue(assignee=None, story_points=2),
        _issue(assignee="   ", story_points=1),
    ]
    rows = story_points_by_assignee(issues)
    assert rows == [
        {
            "assignee": "Unassigned",
            "story_points": 6,
            "issue_count": 3,
            "bug_count": 0,
            "bug_story_points": 0.0,
            "defect_density": 0.0,
        }
    ]


def test_sp_by_assignee_empty_when_no_delivered():
    issues = [_issue(status="In Progress", story_points=5)]
    assert story_points_by_assignee(issues) == []


def test_sp_by_assignee_includes_bug_columns_all_statuses():
    """Bug count/SP always reflect every Bug/Defect assigned (any status),
    independent of the exclude_bugs flag."""
    issues = [
        _issue(assignee="Ava", story_points=5),
        _issue(assignee="Ava", story_points=3, issue_type="Bug"),  # delivered bug
        _issue(
            assignee="Ava",
            story_points=2,
            issue_type="Bug",
            status="In Progress",
        ),  # open bug
        _issue(assignee="Ben", story_points=4),
    ]
    rows = story_points_by_assignee(issues)
    ava = next(r for r in rows if r["assignee"] == "Ava")
    ben = next(r for r in rows if r["assignee"] == "Ben")
    # Ava delivered SP includes the delivered bug (8), bug stats include both bugs (2 / 5 SP)
    assert ava["story_points"] == 8
    assert ava["bug_count"] == 2
    assert ava["bug_story_points"] == 5.0
    assert ben["bug_count"] == 0
    assert ben["bug_story_points"] == 0.0

    # With exclude_bugs, Ava's SP drops to 5 but bug columns still show 2 / 5
    rows_ex = story_points_by_assignee(issues, exclude_bugs=True)
    ava_ex = next(r for r in rows_ex if r["assignee"] == "Ava")
    assert ava_ex["story_points"] == 5
    assert ava_ex["issue_count"] == 1
    assert ava_ex["bug_count"] == 2
    assert ava_ex["bug_story_points"] == 5.0


def test_sp_by_assignee_defect_density():
    """Defect density = delivered bug SP / delivered feature SP, as percent."""
    issues = [
        # Ava: 10 SP feature delivered + 3 SP bug delivered + 5 SP bug open (ignored)
        _issue(assignee="Ava", story_points=10),
        _issue(assignee="Ava", story_points=3, issue_type="Bug"),
        _issue(
            assignee="Ava", story_points=5, issue_type="Bug", status="In Progress"
        ),
        # Ben: 8 SP feature delivered, no bugs
        _issue(assignee="Ben", story_points=8),
    ]
    rows = story_points_by_assignee(issues)
    ava = next(r for r in rows if r["assignee"] == "Ava")
    ben = next(r for r in rows if r["assignee"] == "Ben")
    assert ava["defect_density"] == 30.0  # 3 / 10
    assert ben["defect_density"] == 0.0

    # Density is invariant under exclude_bugs toggle
    rows_ex = story_points_by_assignee(issues, exclude_bugs=True)
    ava_ex = next(r for r in rows_ex if r["assignee"] == "Ava")
    assert ava_ex["defect_density"] == 30.0


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
