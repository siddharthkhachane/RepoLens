# RepoLens Backend

A fast, offline-first backend for analyzing local git repositories to understand file history, code intent, and change metrics.

## Features

- **Git Blame Analysis**: Trace commit history for any file or line range
- **Metrics**: Calculate churn, stability, and last touch date
- **Intent Inference**: Detect workarounds, design changes, and unclear code
- **Caching**: Fast repeated queries with git-aware caching
- **Optional LLM**: Integrate with OpenAI for deeper analysis (offline-first by default)
- **Report Generation**: Export findings as markdown
- **Web UI**: Simple HTML interface for quick manual testing

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Testing**: Pytest
- **Python**: 3.11+

## Setup

### Prerequisites

- Python 3.11 or higher
- Git installed and in PATH
- A local git repository to analyze

### Installation

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

## Running the Server

```bash
# From backend/ directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to access the web UI.

## Running Tests

```bash
# From backend/ directory with venv activated
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest app/tests/test_e2e.py

# Run specific test
pytest app/tests/test_e2e.py::test_analyze_file
```

## API Endpoints

### POST `/repo/validate`

Validate a repository and get HEAD commit hash.

**Request:**
```json
{
  "repo_path": "/path/to/repo"
}
```

**Response:**
```json
{
  "is_valid": true,
  "head": "abc123def456..."
}
```

### POST `/analyze`

Analyze a file and get evidence, metrics, intent, and answer.

**Request:**
```json
{
  "repo_path": "/path/to/repo",
  "file_path": "src/main.py",
  "line_start": 1,
  "line_end": 50,
  "question": "Is it safe to refactor?",
  "max_commits": 10,
  "use_llm": false
}
```

**Response:**
```json
{
  "evidence": [
    {
      "hash": "abc123...",
      "author": "John Doe",
      "date": "2024-01-15T10:30:00Z",
      "subject": "fix: resolve issue",
      "diff_snippet": "..."
    }
  ],
  "timeline": [
    {
      "date": "2024-01-15T10:30:00Z",
      "commit": "abc123",
      "label": "fix",
      "subject": "fix: resolve issue"
    }
  ],
  "metrics": {
    "churn_count": 5,
    "last_touch": "2024-01-15T10:30:00Z",
    "stability": "active"
  },
  "intent": {
    "label": "workaround",
    "reason": "Commits mention workaround...",
    "supporting_commits": ["abc123"]
  },
  "answer": {
    "answer": "This file...",
    "risk_assessment": {
      "risk_level": "medium",
      "why": "File is actively being developed",
      "suggested_next_step": "Review recent commits..."
    },
    "evidence": [
      {
        "type": "commit",
        "ref": "abc123",
        "quote": "fix: resolve issue"
      }
    ],
    "confidence": "high",
    "missing_info": []
  },
  "cache": {
    "hit": false,
    "key": "sha256hash"
  }
}
```

### POST `/report`

Generate a markdown report for a file analysis.

**Request:** Same as `/analyze`

**Response:**
```json
{
  "markdown": "# RepoLens Report\n...",
  "saved_to": "/path/to/repo/.repolens_cache/report.md"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "ok": true
}
```

## Example Curl Commands

### Validate a repository

```bash
curl -X POST http://localhost:8000/repo/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo"}'
```

### Analyze a file

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "file_path": "src/main.py",
    "line_start": 1,
    "line_end": 50,
    "max_commits": 10
  }'
```

### Generate a report

```bash
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "file_path": "src/main.py"
  }' > report.json
```

## Configuration

Configuration is managed through environment variables:

- `OPENAI_API_KEY` (optional): Enable LLM features
- `REPOLENS_CACHE_DIR` (optional, default: `.repolens_cache`): Cache directory name

Example:

```bash
export OPENAI_API_KEY="sk-..."
export REPOLENS_CACHE_DIR=".cache"
uvicorn app.main:app
```

## Caching

Results are cached in `<repo_path>/.repolens_cache/` as JSON files. Cache key is based on:
- Repository HEAD commit hash
- File path
- Line range
- Question (if provided)
- Max commits
- LLM usage flag

Cache is automatically used for subsequent identical queries unless `use_llm` is true.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app setup
│   ├── api.py               # API routes
│   ├── models.py            # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── git_runner.py    # Git subprocess wrapper
│   │   ├── repo_validate.py # Repository validation
│   │   ├── evidence_collector.py  # Git blame and commit info
│   │   ├── metrics.py       # File metrics calculation
│   │   ├── timeline.py      # Timeline building
│   │   ├── intent.py        # Intent inference
│   │   ├── cache.py         # Caching logic
│   │   ├── llm.py           # LLM integration
│   │   └── report.py        # Report generation
│   ├── static/
│   │   └── index.html       # Web UI
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py      # Test fixtures
│       ├── test_repo_validate.py
│       ├── test_git_runner.py
│       └── test_e2e.py      # End-to-end tests
├── pyproject.toml
└── README.md
```

## Testing

All tests are unit and integration tests that work offline without external dependencies.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test module
pytest app/tests/test_e2e.py -v
```

Tests use a temporary git repository fixture that is created and destroyed for each test.

## Development

### Adding New Features

1. Implement in appropriate service module
2. Add tests in `app/tests/`
3. Update models if needed in `app/models.py`
4. Add routes in `app/api.py` if it's a new endpoint

### Code Style

- Follow PEP 8
- Use type hints where practical
- Keep functions small and focused
- Document public APIs with docstrings

## Future Enhancements

- [ ] Full OpenAI integration with streaming
- [ ] Support for GitHub API integration
- [ ] Advanced intent patterns (bugfix, feature, deprecation, etc.)
- [ ] Performance metrics dashboard
- [ ] Multi-file analysis
- [ ] Author/contributor insights

## License

MIT

## Support

For issues or questions, open an issue in the repository.
