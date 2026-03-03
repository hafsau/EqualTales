# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EqualTales is an AI-powered children's story engine for the **CreateHER Fest #75HER Challenge Hackathon 2026**. A mother types a stereotype her child expressed (e.g., "Girls can't do math"), and EqualTales generates a personalized, illustrated 5-page story featuring a real woman who proved the stereotype wrong.

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | Python/Flask | Port 5001 (NOT 5000 — macOS AirPlay uses 5000) |
| Frontend | React 18 | CRA (react-scripts), port 3000 |
| Story Generation | Claude Opus 4.6 via OpenRouter | Model ID: `anthropic/claude-opus-4.6` |
| Classification/QA | Claude Sonnet 4.5 via OpenRouter | Model ID: `anthropic/claude-sonnet-4.5` |
| Illustrations | DALL-E 3 via OpenAI API | 1024x1024, standard quality |

## Architecture

```
[React Frontend :3000] → [Flask API :5001] → [MCP Tools] → [Claude/DALL-E APIs]
```

### Pipeline Flow (~75-90s)
```
classify (Sonnet, ~3s) → match (local, <0.1s) → generate_story (Opus, ~57s) → [verify + 5 illustrations] IN PARALLEL (~15s)
```

The backend runs QA verification and all 5 DALL-E illustrations concurrently using `ThreadPoolExecutor(max_workers=6)`.

### The 5 MCP Tools (mcp_server/server.py)

1. **classify_stereotype** — Categorizes stereotype text. Uses Sonnet 4.5.
2. **match_real_woman** — Local KB lookup from 50-entry knowledge base. No API call.
3. **generate_story** — Creates 5-page story with narrative arc. Uses Opus 4.6.
4. **verify_story** — QA check for stereotype reinforcement. Uses Sonnet 4.5.
5. **generate_illustration** — DALL-E 3 call. Warm watercolor children's book style.

### Key Backend Behavior

- **Character Diversity**: Backend randomly selects from 10 diverse character appearances. Story prompts tell Claude NOT to specify race — appearance is injected separately to DALL-E.
- **Input Validation**: min 3 chars, max 500 chars, age 3-10, name max 30 chars
- **Fallbacks**: Classification defaults to `girls_cant_do_math`; missing page fields auto-filled; DALL-E failures return null URL; QA failures return safe default (passed=true, score=7)

### SSE Event Types (streaming endpoint)
`status`, `classification`, `real_woman`, `story`, `qa_result`, `illustration`, `complete`, `error`

### Frontend State Flow
`landing` → `input` → `generating` → `storybook`

## Environment Variables

In `.env` at project root:
- `OPENROUTER_API_KEY` — starts with `sk-or-`
- `OPENAI_API_KEY` — starts with `sk-proj-`, for DALL-E 3 only
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
- girls_cant_do_math, science_is_for_boys, girls_arent_strong, boys_are_better_at_sports
- girls_should_be_quiet, girls_cant_be_leaders, technology_is_for_boys, girls_cant_build_things
- mom_gives_up_dreams, too_late_to_start, girls_cant_be_adventurous, girls_are_too_emotional
- pretty_girls_arent_smart, girls_cant_do_dangerous_things

## Important Gotchas

- Port is **5001** not 5000 (macOS AirPlay Receiver uses 5000)
- OpenRouter model IDs use dots not dashes: `anthropic/claude-opus-4.6` not `claude-opus-4-6`
- FastMCP requires Python 3.10+
- DALL-E image URLs expire after ~1 hour
- The `onComplete` callback in TypewriterText uses `useRef` to avoid infinite re-renders
