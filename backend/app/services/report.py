"""Report generation."""

import os
import json
from datetime import datetime
from ..models import AnalyzeResponse


def generate_markdown(analyze_response_dict: dict) -> tuple[str, str]:
    """
    Generate a markdown report from analysis response.

    Args:
        analyze_response_dict: Analysis response dictionary

    Returns:
        Tuple of (markdown_content, file_path)
    """
    # Extract data from response
    evidence_list = analyze_response_dict.get("evidence", [])
    timeline = analyze_response_dict.get("timeline", [])
    metrics = analyze_response_dict.get("metrics", {})
    intent = analyze_response_dict.get("intent", {})
    answer = analyze_response_dict.get("answer", {})

    # Build markdown
    md = "# RepoLens Report\n\n"

    md += "## Inputs\n"
    md += f"- File: {analyze_response_dict.get('file_path', 'unknown')}\n"
    md += f"- Line range: {analyze_response_dict.get('line_start', 'all')}-{analyze_response_dict.get('line_end', 'all')}\n"
    md += f"- Question: {analyze_response_dict.get('question', 'N/A')}\n"
    md += f"- Generated: {datetime.now().isoformat()}\n\n"

    md += "## Answer\n"
    if isinstance(answer, dict):
        md += f"{answer.get('answer', 'No answer')}\n\n"
    else:
        md += f"{answer.answer if hasattr(answer, 'answer') else 'No answer'}\n\n"

    md += "## Risk Assessment\n"
    if isinstance(answer, dict):
        ra = answer.get("risk_assessment", {})
        md += f"- **Risk Level**: {ra.get('risk_level', 'Unknown')}\n"
        md += f"- **Why**: {ra.get('why', 'Unknown')}\n"
        md += f"- **Next Steps**: {ra.get('suggested_next_step', 'Unknown')}\n"
    else:
        if hasattr(answer, "risk_assessment"):
            ra = answer.risk_assessment
            md += f"- **Risk Level**: {ra.risk_level}\n"
            md += f"- **Why**: {ra.why}\n"
            md += f"- **Next Steps**: {ra.suggested_next_step}\n"
    md += "\n"

    md += "## Metrics\n"
    md += f"- **Churn Count**: {metrics.get('churn_count', 'Unknown')}\n"
    md += f"- **Last Touch**: {metrics.get('last_touch', 'Unknown')}\n"
    md += f"- **Stability**: {metrics.get('stability', 'Unknown')}\n\n"

    md += "## Intent\n"
    md += f"- **Label**: {intent.get('label', 'Unknown')}\n"
    md += f"- **Reason**: {intent.get('reason', 'Unknown')}\n"
    if intent.get("supporting_commits"):
        md += f"- **Supporting Commits**: {', '.join(intent['supporting_commits'])}\n"
    md += "\n"

    md += "## Timeline\n"
    if timeline:
        for item in timeline:
            if isinstance(item, dict):
                md += f"- **{item.get('date', 'Unknown')}** ({item.get('label', 'unknown')}): "
                md += f"{item.get('commit', 'unknown')} - {item.get('subject', 'unknown')}\n"
            else:
                md += f"- **{item.date}** ({item.label}): {item.commit} - {item.subject}\n"
    else:
        md += "No timeline data.\n"
    md += "\n"

    md += "## Evidence Appendix\n"
    if evidence_list:
        for evidence in evidence_list:
            if isinstance(evidence, dict):
                md += f"### Commit {evidence.get('hash', 'unknown')[:8]}\n"
                md += f"- **Author**: {evidence.get('author', 'Unknown')}\n"
                md += f"- **Date**: {evidence.get('date', 'Unknown')}\n"
                md += f"- **Subject**: {evidence.get('subject', 'Unknown')}\n"
            else:
                md += f"### Commit {evidence.hash[:8]}\n"
                md += f"- **Author**: {evidence.author}\n"
                md += f"- **Date**: {evidence.date}\n"
                md += f"- **Subject**: {evidence.subject}\n"
    else:
        md += "No evidence data.\n"

    return md


def generate_markdown_and_save(
    repo_path: str, analyze_response_dict: dict
) -> tuple[str, str]:
    """
    Generate markdown and save to cache directory.

    Args:
        repo_path: Repository root path
        analyze_response_dict: Analysis response

    Returns:
        Tuple of (markdown_content, saved_file_path)
    """
    md_content = generate_markdown(analyze_response_dict)

    # Determine cache directory
    cache_dir = os.path.join(repo_path, ".repolens_cache")
    os.makedirs(cache_dir, exist_ok=True)

    report_path = os.path.join(cache_dir, "report.md")

    try:
        with open(report_path, "w") as f:
            f.write(md_content)
    except Exception as e:
        raise ValueError(f"Could not write report: {e}")

    return md_content, report_path
