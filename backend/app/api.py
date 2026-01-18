"""API routes for RepoLens."""

import os
from fastapi import APIRouter, HTTPException
from .models import (
    RepoValidateRequest,
    RepoValidateResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ReportRequest,
    ReportResponse,
    CacheInfo,
)
from .core.config import get_settings
from .services.repo_validate import validate_repo
from .services.evidence_collector import resolve_file_path, collect_evidence
from .services.metrics import file_metrics
from .services.timeline import build_timeline
from .services.intent import infer_intent
from .services.llm import generate_answer
from .services.cache import cache_key, cache_get, cache_set
from .services.report import generate_markdown_and_save

router = APIRouter()


@router.post("/repo/validate", response_model=RepoValidateResponse)
async def validate_endpoint(request: RepoValidateRequest):
    """
    Validate a repository.

    Args:
        request: RepoValidateRequest with repo_path

    Returns:
        RepoValidateResponse with is_valid and head hash
    """
    is_valid, head = validate_repo(request.repo_path)
    return RepoValidateResponse(is_valid=is_valid, head=head)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    """
    Analyze a file in a repository.

    Args:
        request: AnalyzeRequest

    Returns:
        AnalyzeResponse with evidence, timeline, metrics, intent, answer
    """
    # Validate repo
    is_valid, repo_head = validate_repo(request.repo_path)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid repository")

    # Resolve file path
    try:
        abs_path, rel_path = resolve_file_path(request.repo_path, request.file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Default line range
    line_start = request.line_start
    line_end = request.line_end
    if line_start is None or line_end is None:
        line_start = 1
        line_end = 200

    # Compute cache key
    settings = get_settings()
    cache_dir = os.path.join(request.repo_path, settings.repolens_cache_dir)
    key = cache_key(
        repo_head,
        rel_path,
        line_start,
        line_end,
        request.question,
        request.max_commits,
        request.use_llm,
    )

    # Check cache
    cached = cache_get(cache_dir, key)
    if cached:
        return AnalyzeResponse(
            evidence=[evidence for evidence in cached.get("evidence", [])],
            timeline=[item for item in cached.get("timeline", [])],
            metrics=cached.get("metrics", {}),
            intent=cached.get("intent", {}),
            answer=cached.get("answer", {}),
            cache=CacheInfo(hit=True, key=key),
        )

    # Collect evidence
    evidence_list = collect_evidence(
        request.repo_path, rel_path, line_start, line_end, request.max_commits
    )

    # Get metrics
    metrics_dict = file_metrics(request.repo_path, rel_path)

    # Build timeline
    timeline_list = build_timeline(evidence_list)

    # Infer intent
    intent_dict = infer_intent(evidence_list, timeline_list, metrics_dict)

    # Generate answer
    answer_obj = generate_answer(
        request.question,
        evidence_list,
        timeline_list,
        metrics_dict,
        intent_dict.__dict__,
        request.use_llm,
    )

    # Build response
    response_dict = {
        "evidence": [e.model_dump() for e in evidence_list],
        "timeline": [t.model_dump() for t in timeline_list],
        "metrics": metrics_dict,
        "intent": intent_dict.model_dump(),
        "answer": answer_obj.model_dump(),
        "cache": {"hit": False, "key": key},
    }

    # Cache it
    cache_set(cache_dir, key, response_dict)

    response = AnalyzeResponse(
        evidence=evidence_list,
        timeline=timeline_list,
        metrics=metrics_dict,  # type: ignore
        intent=intent_dict,
        answer=answer_obj,
        cache=CacheInfo(hit=False, key=key),
    )
    return response


@router.post("/report", response_model=ReportResponse)
async def report_endpoint(request: ReportRequest):
    """
    Generate a report for a file.

    Args:
        request: ReportRequest

    Returns:
        ReportResponse with markdown and file path
    """
    # Use analyze logic to get all the data
    is_valid, repo_head = validate_repo(request.repo_path)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid repository")

    # Resolve file path
    try:
        abs_path, rel_path = resolve_file_path(request.repo_path, request.file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Default line range
    line_start = request.line_start
    line_end = request.line_end
    if line_start is None or line_end is None:
        line_start = 1
        line_end = 200

    # Collect evidence
    evidence_list = collect_evidence(
        request.repo_path, rel_path, line_start, line_end, request.max_commits
    )

    # Get metrics
    metrics_dict = file_metrics(request.repo_path, rel_path)

    # Build timeline
    timeline_list = build_timeline(evidence_list)

    # Infer intent
    intent_dict = infer_intent(evidence_list, timeline_list, metrics_dict)

    # Generate answer
    answer_obj = generate_answer(
        request.question,
        evidence_list,
        timeline_list,
        metrics_dict,
        intent_dict.__dict__,
        request.use_llm,
    )

    # Build response dict for markdown generation
    response_dict = {
        "file_path": rel_path,
        "line_start": line_start,
        "line_end": line_end,
        "question": request.question,
        "evidence": [e.model_dump() for e in evidence_list],
        "timeline": [t.model_dump() for t in timeline_list],
        "metrics": metrics_dict,
        "intent": intent_dict.model_dump(),
        "answer": answer_obj.model_dump(),
    }

    # Generate markdown and save
    markdown, file_path = generate_markdown_and_save(request.repo_path, response_dict)

    return ReportResponse(markdown=markdown, saved_to=file_path)
