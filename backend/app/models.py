"""Pydantic response models for the reporting API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PerAssigneeStoryPoints(BaseModel):
    assignee: str
    story_points: float
    issue_count: int
    bug_count: int = 0
    bug_story_points: float = 0.0
    defect_density: float | None = None


class PerAssigneeDefects(BaseModel):
    assignee: str
    defect_count: int


class SprintReport(BaseModel):
    """Aggregated report for a single sprint (or all sprints combined)."""

    total_story_points_delivered: float
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]
    defects_by_assignee: list[PerAssigneeDefects]


class SprintSPReport(BaseModel):
    """SP-only variant used for the exclude-bugs alternate aggregation."""

    total_story_points_delivered: float
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]


class AnalyzeResponse(BaseModel):
    """Full response for POST /api/analyze."""

    # Including bugs (default behaviour)
    total_story_points_delivered: float = Field(
        description="Sum of story points for issues with status in {Done, Closed, Resolved}."
    )
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]
    defects_by_assignee: list[PerAssigneeDefects]

    # Excluding bugs from SP aggregation
    total_story_points_delivered_ex_bugs: float = Field(
        description="Same as total_story_points_delivered but Bug/Defect issues are excluded."
    )
    total_issues_delivered_ex_bugs: int
    story_points_by_assignee_ex_bugs: list[PerAssigneeStoryPoints]

    # Sprint support
    sprints: list[str] = Field(
        default_factory=list,
        description="Sorted list of unique sprint names found in the file.",
    )
    by_sprint: dict[str, SprintReport] = Field(
        default_factory=dict,
        description="Per-sprint aggregated reports keyed by sprint name (bugs included).",
    )
    by_sprint_ex_bugs: dict[str, SprintSPReport] = Field(
        default_factory=dict,
        description="Per-sprint SP-only reports with Bug/Defect issues excluded.",
    )

    # Handy context for the UI
    filename: str
    total_rows: int
    warnings: list[str] = Field(default_factory=list)
