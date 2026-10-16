# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EqualTales is an AI-powered children's story engine for the **CreateHER Fest #75HER Challenge Hackathon 2026**. A mother types a stereotype her child expressed (e.g., "Girls can't do math"), and EqualTales generates a personalized, illustrated 5-page story featuring a real woman who proved the stereotype wrong.

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | Python/Flask | Port 5001 (NOT 5000 — macOS AirPlay uses 5000) |
| Frontend | React 18 | CRA (react-scripts), port 3000 |
| Story Generation | Claude Opus 5.5 via Anthropic API | `claude-opus-5-5` (env `CLAUDE_STORY_MODEL`), effort `medium` |
| Classification/QA | Claude Haiku 5.5 via Anthropic API | `claude-haiku-5-5` (env `CLAUDE_FAST_MODEL`), effort `low` |
| Illustrations | OpenAI `gpt-image-1-mini` | 1024x1024, medium quality, JPEG data URLs (env `IMAGE_MODEL`) |

## Hosted Backend

**Production URL**: https://equaltales-api.onrender.com

When asked to "run the backend", always use the hosted Render backend, not the local server. To check if it's running:
```bash
curl https://equaltales-api.onrender.com/api/health
```

## Architecture

```
[React Frontend :3000] → [Flask API :5001] → [MCP Tools] → [Anthropic + OpenAI image APIs]
```

### Pipeline Flow
```
classify (Haiku) → match (local, <0.1s) → generate_story (Opus) → 5 illustrations IN PARALLEL (~12s) → verify (Haiku)
```

The backend runs all 5 illustrations concurrently using `ThreadPoolExecutor(max_workers=6)`.

### Model call rules (mcp_server/server.py `_claude_json`)

- All Claude calls go through `_claude_json`: structured outputs (`output_config.format` JSON schema) guarantee valid JSON, and it raises clear errors on refusal, `max_tokens` truncation, or empty text.
- Never hardcode model IDs in call sites — use the `STORY_MODEL` / `FAST_MODEL` / `IMAGE_MODEL` constants.
- Don't route through free/auto model routers: the app previously broke because `openrouter/free` returned empty answers and pinned free models were removed.
- Dependencies are fully pinned in `backend/requirements.txt` (generated from `backend/requirements.in`; instructions in that file).

### The 5 MCP Tools (mcp_server/server.py)

1. **classify_stereotype** — Categorizes stereotype text. Uses `FAST_MODEL`; category enum enforced by schema.
2. **match_real_woman** — Local KB lookup from 50-entry knowledge base. No API call.
3. **generate_story** — Creates 5-page story with narrative arc. Uses `STORY_MODEL` (with server-side refusal fallback).
4. **verify_story** — QA check for stereotype reinforcement. Uses `FAST_MODEL`.
5. **generate_illustration** — `IMAGE_MODEL` call. Warm watercolor children's book style.

### Key Backend Behavior

- **Character Diversity**: Backend randomly selects from 10 diverse character appearances. Story prompts tell Claude NOT to specify race — appearance is injected separately into the image prompt.
- **Input Validation**: min 3 chars, max 500 chars, age 3-10, name max 30 chars
- **Fallbacks**: Classification failures/unknown categories default to `girls_cant_do_math`; missing page fields auto-filled; image failures return null URL; QA failures return safe default (passed=true, score=7)
- **Health**: `/api/health` reports `missing_api_keys` and the configured models — check it first when something breaks

### SSE Event Types (streaming endpoint)
`status`, `classification`, `real_woman`, `story`, `qa_result`, `illustration`, `complete`, `error`

### Frontend State Flow
`landing` → `input` → `generating` → `storybook`

## Environment Variables

In `.env` at project root:
- `ANTHROPIC_API_KEY` — starts with `sk-ant-` (also set in the Render dashboard)
- `OPENAI_API_KEY` — starts with `sk-proj-`, for illustrations only
- Optional: `CLAUDE_STORY_MODEL`, `CLAUDE_FAST_MODEL`, `CLAUDE_STORY_EFFORT`, `IMAGE_MODEL`
- `USE_GOOSE` — `true` for Goose orchestration, `false` (default) for direct MCP tool calls

## Development Commands

```bash
# Backend
cd ~/EqualTales/backend && python3 app.py          # Run Flask server (port 5001)

# Frontend
cd ~/EqualTales/frontend && npm start              # Run React dev server (port 3000)
cd ~/EqualTales/frontend && npm run build          # Production build

# Test the API
curl http://localhost:5001/api/health
curl http://localhost:5001/api/examples
```

## Testing

### Backend (pytest)
```bash
cd ~/EqualTales/backend
pip install -r requirements-dev.txt

pytest tests/ -v                                    # Run all tests
pytest tests/ --cov=. --cov-report=term-missing    # With coverage
pytest tests/test_app.py -v                        # Single file
pytest tests/test_app.py::TestHealthEndpoint -v   # Single class
pytest tests/test_app.py::TestHealthEndpoint::test_returns_200 -v  # Single test
pytest tests/ -m "not slow"                        # Skip slow tests
pytest tests/ -m "integration"                     # Integration tests only
```

### Frontend (Jest)
```bash
cd ~/EqualTales/frontend
npm test                    # Watch mode
npm run test:coverage       # With coverage
npm run test:ci             # CI mode (no watch)
```

### QA Agent
```bash
cd ~/EqualTales
python scripts/qa_agent.py              # Run all QA checks
python scripts/qa_agent.py --quick      # Skip coverage
python scripts/qa_agent.py --watch      # Re-run on file changes
python scripts/qa_agent.py --fix        # Attempt auto-fixes
python scripts/qa_agent.py --json       # JSON output for CI
```

### Coverage Requirements
- Backend: 70% minimum
- Frontend: 70% minimum

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/health` | GET | Status + KB stats |
| `/api/examples` | GET | 10 stereotype examples for quick-start buttons |
| `/api/generate/stream` | POST | **Main endpoint.** SSE streaming |
| `/api/generate` | POST | Non-streaming version |
| `/api/women` | GET | List all 50 women |
| `/api/categories` | GET | List all 14 categories |

## Knowledge Base

50 women across 14 stereotype categories in `data/women_knowledge_base.json`:
- girls_cant_do_math, science_is_for_boys, girls_arent_strong, girls_cant_be_adventurous
- girls_should_be_quiet, girls_cant_be_leaders, girls_cant_do_tech, girls_cant_build_things
- moms_cant_be_leaders, its_too_late_to_start, girls_cant_run_businesses, emotions_are_weakness
- pretty_girls_arent_smart, disability_means_you_cant

## Important Gotchas

- Port is **5001** not 5000 (macOS AirPlay Receiver uses 5000)
- Anthropic model IDs use dashes and no date suffix: `claude-opus-5-5`, `claude-haiku-5-5`
- FastMCP requires Python 3.10+
- Images are returned as base64 data URLs (gpt-image models don't return hosted URLs)
- The `onComplete` callback in TypewriterText uses `useRef` to avoid infinite re-renders
