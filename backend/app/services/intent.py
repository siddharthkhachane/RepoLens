"""Intent inference."""

from ..models import CommitEvidence, TimelineItem, Intent


def infer_intent(
    evidence_list: list[CommitEvidence], timeline: list[TimelineItem], metrics: dict
) -> Intent:
    """
    Infer intent from evidence and metrics.

    Args:
        evidence_list: List of CommitEvidence objects
        timeline: List of TimelineItem objects
        metrics: Dictionary of metrics

    Returns:
        Intent object
    """
    all_subjects = " ".join([e.subject.lower() for e in evidence_list])
    all_timeline_labels = " ".join([t.label for t in timeline])

    # Heuristic 1: Check for workaround keywords
    if any(
        word in all_subjects for word in ["workaround", "hack", "temporary", "temp"]
    ):
        supporting = [e.hash[:8] for e in evidence_list if any(
            word in e.subject.lower()
            for word in ["workaround", "hack", "temporary", "temp"]
        )]
        return Intent(
            label="workaround",
            reason="Commits mention workaround, hack, or temporary fixes.",
            supporting_commits=supporting,
        )

    # Heuristic 2: Check for design keywords
    if any(
        word in all_subjects for word in ["design", "architecture", "adr", "rfc"]
    ):
        supporting = [e.hash[:8] for e in evidence_list if any(
            word in e.subject.lower() for word in ["design", "architecture", "adr", "rfc"]
        )]
        return Intent(
            label="design",
            reason="Commits mention design, architecture, or RFC discussions.",
            supporting_commits=supporting,
        )

    # Heuristic 3: Volatile + multiple fixes = likely workaround
    if metrics.get("stability") == "volatile" and all_timeline_labels.count("fix") >= 2:
        fix_commits = [e.hash[:8] for e in evidence_list if "fix" in e.subject.lower()]
        return Intent(
            label="workaround",
            reason="High churn with multiple fixes suggests iterative workarounds.",
            supporting_commits=fix_commits,
        )

    # Default: unclear
    return Intent(
        label="unclear",
        reason="No clear pattern in commit history.",
        supporting_commits=[],
    )
