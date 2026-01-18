"""Pydantic models for RepoLens."""

from pydantic import BaseModel, Field
from typing import Optional


class RepoValidateRequest(BaseModel):
    """Request to validate a repository."""

    repo_path: str


class RepoValidateResponse(BaseModel):
    """Response from repository validation."""

    is_valid: bool
    head: str | None = None


class CommitEvidence(BaseModel):
    """Evidence from a single commit."""

    hash: str
    author: str
    date: str
    subject: str
    diff_snippet: str


class TimelineItem(BaseModel):
    """Item in the timeline."""

    date: str
    commit: str
    label: str
    subject: str


class Metrics(BaseModel):
    """Metrics about the file."""

    churn_count: int
    last_touch: str | None = None
    stability: str  # "stable", "active", or "volatile"


class Intent(BaseModel):
    """Inferred intent about the code."""

    label: str  # "workaround", "design", or "unclear"
    reason: str
    supporting_commits: list[str] = []


class EvidenceRef(BaseModel):
    """Reference to evidence."""

    type: str
    ref: str
    quote: str


class RiskAssessment(BaseModel):
    """Risk assessment."""

    risk_level: str  # "low", "medium", or "high"
    why: str
    suggested_next_step: str


class Answer(BaseModel):
    """Answer to the analysis question."""

    answer: str
    risk_assessment: RiskAssessment
    evidence: list[EvidenceRef] = []
    confidence: str  # "low", "medium", or "high"
    missing_info: list[str] = []


class CacheInfo(BaseModel):
    """Cache information."""

    hit: bool
    key: str


class AnalyzeRequest(BaseModel):
    """Request to analyze a file."""

    repo_path: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    question: Optional[str] = None
    max_commits: int = 10
    use_llm: bool = False


class AnalyzeResponse(BaseModel):
    """Response from analysis."""

    evidence: list[CommitEvidence]
    timeline: list[TimelineItem]
    metrics: Metrics
    intent: Intent
    answer: Answer
    cache: CacheInfo


class ReportRequest(BaseModel):
    """Request to generate a report."""

    repo_path: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    question: Optional[str] = None
    max_commits: int = 10
    use_llm: bool = False


class ReportResponse(BaseModel):
    """Response from report generation."""

    markdown: str
    saved_to: str
