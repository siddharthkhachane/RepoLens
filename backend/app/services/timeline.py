"""Timeline building."""

from datetime import datetime
from ..models import CommitEvidence, TimelineItem


def build_timeline(evidence_list: list[CommitEvidence]) -> list[TimelineItem]:
    """
    Build a timeline from evidence.

    Args:
        evidence_list: List of CommitEvidence objects

    Returns:
        List of TimelineItem objects ordered by date ascending
    """
    timeline = []

    for evidence in evidence_list:
        # Infer label from subject
        subject_lower = evidence.subject.lower()

        if "revert" in subject_lower:
            label = "revert"
        elif any(word in subject_lower for word in ["fix", "bug", "hotfix"]):
            label = "fix"
        elif any(word in subject_lower for word in ["refactor", "cleanup", "rename"]):
            label = "refactor"
        else:
            label = "change"

        timeline.append(
            TimelineItem(
                date=evidence.date,
                commit=evidence.hash[:8],  # Short hash
                label=label,
                subject=evidence.subject,
            )
        )

    # Sort by date ascending (oldest first)
    # Try to parse dates, fall back to original order if parsing fails
    try:
        timeline.sort(key=lambda x: datetime.fromisoformat(x.date.replace("Z", "+00:00")))
    except Exception:
        # If parsing fails, keep original order
        pass

    return timeline
