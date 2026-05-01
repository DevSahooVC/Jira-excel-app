"""Pydantic response models for the reporting API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PerAssigneeStoryPoints(BaseModel):
    assignee: str
    story_points: float
    issue_count: int


class PerAssigneeDefects(BaseModel):
    assignee: str
    defect_count: int


class SprintReport(BaseModel):
    """Aggregated report for a single sprint (or all sprints combined)."""

    total_story_points_delivered: float
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]
    defects_by_assignee: list[PerAssigneeDefects]


class AnalyzeResponse(BaseModel):
    """Full response for POST /api/analyze."""

    total_story_points_delivered: float = Field(
        description="Sum of story points for issues with status in {Done, Closed, Resolved}."
    )
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]
    defects_by_assignee: list[PerAssigneeDefects]

    # Sprint support
    sprints: list[str] = Field(
        default_factory=list,
        description="Sorted list of unique sprint names found in the file.",
    )
    by_sprint: dict[str, SprintReport] = Field(
        default_factory=dict,
        description="Per-sprint aggregated reports keyed by sprint name.",
    )

    # Handy context for the UI
    filename: str
    total_rows: int
    warnings: list[str] = Field(default_factory=list)
