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


class AnalyzeResponse(BaseModel):
    """Full response for POST /api/analyze."""

    total_story_points_delivered: float = Field(
        description="Sum of story points for issues with status in {Done, Closed, Resolved}."
    )
    total_issues_delivered: int
    story_points_by_assignee: list[PerAssigneeStoryPoints]
    defects_by_assignee: list[PerAssigneeDefects]

    # Handy context for the UI
    filename: str
    total_rows: int
    warnings: list[str] = Field(default_factory=list)
