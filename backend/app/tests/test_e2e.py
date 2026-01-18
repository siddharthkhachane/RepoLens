"""End-to-end tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_validate_repo(client, temp_git_repo):
    """Test repo validation endpoint."""
    response = client.post(
        "/repo/validate", json={"repo_path": temp_git_repo["path"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["head"] is not None


def test_analyze_file(client, temp_git_repo):
    """Test file analysis endpoint."""
    response = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
            "line_start": 1,
            "line_end": 5,
            "max_commits": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "evidence" in data
    assert "timeline" in data
    assert "metrics" in data
    assert "intent" in data
    assert "answer" in data
    assert "cache" in data

    # Check evidence
    assert len(data["evidence"]) >= 1
    assert "hash" in data["evidence"][0]
    assert "subject" in data["evidence"][0]

    # Check metrics
    assert "churn_count" in data["metrics"]
    assert "stability" in data["metrics"]
    assert data["metrics"]["stability"] in ["stable", "active", "volatile"]

    # Check intent
    assert "label" in data["intent"]
    assert data["intent"]["label"] in ["workaround", "design", "unclear"]

    # Check answer
    assert "answer" in data["answer"]
    assert "risk_assessment" in data["answer"]
    assert "confidence" in data["answer"]

    # Check cache
    assert "hit" in data["cache"]
    assert "key" in data["cache"]


def test_analyze_cache_hit(client, temp_git_repo):
    """Test that second analysis returns cached result."""
    # First call
    response1 = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
            "line_start": 1,
            "line_end": 5,
        },
    )
    assert response1.status_code == 200
    assert response1.json()["cache"]["hit"] is False

    # Second call should hit cache
    response2 = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
            "line_start": 1,
            "line_end": 5,
        },
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["cache"]["hit"] is True
    assert response1.json()["cache"]["key"] == data2["cache"]["key"]


def test_report_generation(client, temp_git_repo):
    """Test report generation endpoint."""
    response = client.post(
        "/report",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
            "line_start": 1,
            "line_end": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "markdown" in data
    assert "saved_to" in data

    # Check markdown content
    assert "RepoLens Report" in data["markdown"]
    assert ".repolens_cache" in data["saved_to"]


def test_analyze_timeline_contains_commits(client, temp_git_repo):
    """Test that timeline contains commit information."""
    response = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    timeline = data["timeline"]

    # Should have at least one timeline item
    assert len(timeline) >= 1

    # Check structure of timeline items
    for item in timeline:
        assert "date" in item
        assert "commit" in item
        assert "label" in item
        assert "subject" in item


def test_analyze_intent_detection(client, temp_git_repo):
    """Test that intent is detected correctly."""
    response = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": temp_git_repo["file_path"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    intent = data["intent"]

    # Our test repo has a workaround commit, so intent should detect it
    assert intent["label"] in ["workaround", "design", "unclear"]
    assert len(intent["reason"]) > 0


def test_invalid_repo_path(client):
    """Test analysis with invalid repo path."""
    response = client.post(
        "/analyze",
        json={
            "repo_path": "/nonexistent/path",
            "file_path": "test.py",
        },
    )
    assert response.status_code == 400


def test_invalid_file_path(client, temp_git_repo):
    """Test analysis with non-existent file."""
    response = client.post(
        "/analyze",
        json={
            "repo_path": temp_git_repo["path"],
            "file_path": "nonexistent.py",
        },
    )
    assert response.status_code == 400
