"""LLM integration and answer generation."""

from ..models import CommitEvidence, TimelineItem, Answer, RiskAssessment, EvidenceRef
from ..core.config import get_settings


def generate_answer(
    question: str | None,
    evidence_list: list[CommitEvidence],
    timeline: list[TimelineItem],
    metrics: dict,
    intent: dict,
    use_llm: bool = False,
) -> Answer:
    """
    Generate an answer to the question about the code.

    Args:
        question: Optional question from user
        evidence_list: List of CommitEvidence
        timeline: List of TimelineItem
        metrics: Metrics dictionary
        intent: Intent dictionary
        use_llm: Whether to use LLM (if available)

    Returns:
        Answer object
    """
    settings = get_settings()

    # Determine if LLM is available and requested
    use_llm = use_llm and settings.openai_api_key is not None

    if use_llm:
        # TODO: Implement OpenAI API call
        # For now, fall back to local summary
        pass

    # Local deterministic summary
    return _generate_local_answer(question, evidence_list, timeline, metrics, intent)


def _generate_local_answer(
    question: str | None,
    evidence_list: list[CommitEvidence],
    timeline: list[TimelineItem],
    metrics: dict,
    intent: dict,
) -> Answer:
    """
    Generate a local, deterministic answer without LLM.

    Args:
        question: Optional question
        evidence_list: List of CommitEvidence
        timeline: List of TimelineItem
        metrics: Metrics dictionary
        intent: Intent dictionary

    Returns:
        Answer object
    """
    # Risk assessment based on stability
    stability = metrics.get("stability", "unclear")
    if stability == "volatile":
        risk_level = "high"
        why = "File has high churn and is frequently modified."
    elif stability == "active":
        risk_level = "medium"
        why = "File is actively being developed."
    else:
        risk_level = "low"
        why = "File is stable with few recent changes."

    suggested_next_step = "Review recent commits and test changes thoroughly."

    # Build answer text
    churn = metrics.get("churn_count", 0)
    intent_label = intent.get("label", "unclear")

    answer_text = (
        f"This file has been modified {churn} times in the last 50 commits. "
        f"The code appears to be {intent_label} in nature. "
        f"The most recent changes were {', '.join([t.label for t in timeline[-3:]]) if timeline else 'unknown'}. "
        f"Proceed with caution given the {stability} nature of this code."
    )

    # Confidence assessment
    if intent_label != "unclear":
        confidence = "high"
    elif len(evidence_list) >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    # Evidence references from first 2 commits
    evidence_refs = []
    for evidence in evidence_list[:2]:
        evidence_refs.append(
            EvidenceRef(
                type="commit",
                ref=evidence.hash[:8],
                quote=evidence.subject,
            )
        )

    # Missing info
    missing_info = []
    if intent_label == "unclear":
        missing_info.append(
            "No explicit design/issue reference found in commit messages"
        )

    return Answer(
        answer=answer_text,
        risk_assessment=RiskAssessment(
            risk_level=risk_level,
            why=why,
            suggested_next_step=suggested_next_step,
        ),
        evidence=evidence_refs,
        confidence=confidence,
        missing_info=missing_info,
    )
