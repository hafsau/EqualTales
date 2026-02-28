# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EqualTales is an AI-powered children's story engine for the **CreateHER Fest #75HER Challenge Hackathon 2026** (AI/ML Track). A mother types a stereotype her child expressed (e.g., "Girls can't do math"). EqualTales generates a personalized, illustrated 5-page story where a fictional child discovers a real woman who proved the stereotype wrong. No login, no signup — judges click "Try It Now" immediately.

## Project Structure

```
~/EqualTales/
├── backend/
│   ├── app.py              # Flask API (port 5001, NOT 5000 — macOS AirPlay uses 5000)
│   ├── requirements.txt    # Flask, openai, python-dotenv, gunicorn, fastmcp
│   ├── requirements-dev.txt # pytest, pytest-cov, responses (test dependencies)
│   ├── conftest.py         # pytest fixtures and mocks
│   ├── pytest.ini          # pytest configuration
│   └── tests/
│       ├── test_app.py     # Backend API tests
│       └── test_mcp_server.py  # MCP server tool tests
├── frontend/
│   ├── public/index.html   # Google Fonts: Quicksand, DM Sans, Caveat
│   ├── src/
│   │   ├── App.js          # React single-file app (5 components + main App)
│   │   ├── App.css         # Full CSS with warm storybook design
│   │   ├── App.test.js     # React component tests (Jest + RTL)
│   │   └── setupTests.js   # Jest test configuration
│   └── package.json        # React 18.2, react-scripts 5.0.1, test dependencies
├── mcp_server/
│   └── server.py           # FastMCP server with 5 tools (runs via Goose OR direct import)
├── scripts/
│   └── qa_agent.py         # QA agent for continuous monitoring
├── data/
│   └── women_knowledge_base.json  # 50 women, 14 stereotype categories
├── .env                    # OPENROUTER_API_KEY and OPENAI_API_KEY
├── goose_config.yaml       # Goose extension config (points to mcp_server/server.py)
└── CreatorFest_Project_Plan.md
```

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| AI Agent | Goose (Block's open-source framework) + Claude | OpenRouter for Claude API calls, NOT direct Anthropic |
| Story Generation | Claude Opus 4.6 via OpenRouter | Model ID: `anthropic/claude-opus-4.6` |
| Classification | Claude Sonnet 4.5 via OpenRouter | Model ID: `anthropic/claude-sonnet-4.5` |
| QA Verification | Claude Sonnet 4.5 via OpenRouter | Same model, cheaper than Opus |
| Illustrations | DALL-E 3 via OpenAI API | 1024x1024, standard quality |
| Backend | Python/Flask | Port 5001 |
| Frontend | React 18 | CRA (react-scripts), port 3000 |
| Deployment | Vercel (frontend) + Render (backend) | Not yet deployed |

## API Keys

Both live in `~/EqualTales/.env`:
- `OPENROUTER_API_KEY` — starts with `sk-or-`, $80 sponsored hackathon credits
- `OPENAI_API_KEY` — starts with `sk-proj-`, for DALL-E 3 only

## The 5 MCP Tools (mcp_server/server.py)

1. **classify_stereotype** — Takes stereotype text, returns primary_category, secondary_categories, emotional_tone. Uses Sonnet 4.5.
2. **match_real_woman** — Local KB lookup. Finds best woman from 50-entry knowledge base by category overlap. No API call.
3. **generate_story** — Creates 5-page story with narrative arc (Belief → Question → Discovery → Inspiration → New Belief). Uses Opus 4.6. Returns JSON with title, pages (text + illustration_description), discussion_prompts, activity_suggestion.
4. **verify_story** — QA check for inadvertent stereotype reinforcement. Returns passed (bool), score (1-10), issues, strengths. Uses Sonnet 4.5.
5. **generate_illustration** — DALL-E 3 call. Warm watercolor children's book style. Returns image URL.

## Pipeline Flow & Timing (~75-90s)

```
classify (Sonnet, ~3s) → match (local, <0.1s) → generate_story (Opus, ~57s) → [verify + 5 illustrations] IN PARALLEL (~15s)
```

The backend runs QA verification and all 5 DALL-E illustrations concurrently using `ThreadPoolExecutor(max_workers=6)`. This saves ~60s compared to sequential.

## Flask Backend (backend/app.py)

### Key Routes
- `GET /api/health` — Status + KB stats
- `GET /api/examples` — 10 pre-loaded stereotype examples for quick-start buttons
- `POST /api/generate/stream` — **Main endpoint.** SSE streaming. Frontend uses this.
- `POST /api/generate` — Non-streaming version (returns complete JSON)
- `GET /api/women` — List all 50 women
- `GET /api/categories` — List all 14 categories

### SSE Event Types
The streaming endpoint sends these event types (frontend listens for all of them):
- `status` — Progress messages (triggers step highlighting)
- `classification` — Stereotype classification result
- `real_woman` — Selected woman's name, era, achievement
- `story` — Complete 5-page story data
- `qa_result` — QA verification result (passed, score, issues)
- `illustration` — Individual page illustration URL (sent per-page as they complete)
- `complete` — Pipeline finished
- `error` — Error message

### Character Diversity System
The backend randomly selects from 10 diverse character appearances (different skin tones, hair types, features) for each story generation. The story prompt tells Claude NOT to specify race/ethnicity in illustration descriptions — the appearance is injected separately as `character_description` to DALL-E.

### Edge Case Handling
- Input validation: min 3 chars, max 500 chars, age 3-10, name max 30 chars
- Classification fallback: defaults to `girls_cant_do_math` if no `primary_category` returned
- Story validation: fills in missing page fields (text, illustration_description, page_title)
- DALL-E failures: per-image try/catch, returns null URL (frontend shows placeholder)
- QA failures: returns safe default (passed=true, score=7)
- Connection drops: frontend shows storybook if story data exists

## React Frontend (frontend/src/App.js)

### Components
1. **LandingPage** — Hero with "Try It Now" CTA, stats (Age 3/Age 6/5 pages), fade-in animation
2. **InputForm** — Stereotype text/examples grid, child name, age slider (3-10), back button
3. **GenerationProgress** — 5-step progress tracker, progress bar with gradient, elapsed timer, "Featuring [woman]" reveal card
4. **TypewriterText** — Character-by-character text reveal (25ms), blinking cursor, only on first page view
5. **StorybookViewer** — Page-turn animations (translateX + rotateY), keyboard nav (arrows + spacebar), page dots with seen state, companion section (discussion prompts, activity, QA badge)

### State Flow
`landing` → `input` → `generating` → `storybook`

### Error Recovery
Error banner shows three buttons: "Try Again" (retries same inputs), "Change Input" (back to form), "Dismiss".

## Design System (frontend/src/App.css)

### Typography
- **Quicksand** — Rounded friendly sans-serif for titles, headings, story text
- **DM Sans** — Clean geometric for UI elements, buttons, forms
- **Caveat** — Handwritten cursive for labels, footnotes, timestamps

### Color Palette
- Coral `#E07A6A` (primary/CTA), Coral dark `#C4594B`, Coral light `#FDF0EE`
- Purple deep `#6B4D8E` (accent, "Tales" in title, story title)
- Gold `#E8B44C` (highlights, progress bar)
- Sage `#6DAA73` (QA score, success states)
- Parchment `#FEF9F2` (background with SVG noise texture)

### Key Visual Effects
- Floating blurred gradient orbs on landing (drift animation)
- Book spine effect (4px coral-to-gold gradient left border on story pages)
- Page turns: translateX(40px) + rotateY(2deg), 0.45s
- Image reveal: blur(4px) + scale(1.04) → blur(0) + scale(1)
- Warm-toned shadows throughout

## Knowledge Base (data/women_knowledge_base.json)

50 unique women across 14 stereotype categories. Each woman entry has:
- name, era, category, achievement
- fairy_tale_moment (magical retelling of key achievement)
- age_adaptations (young/middle/older versions)
- counters_stereotypes (array of category keys)

All 50 women are discoverable through at least one category's `suggested_women` array.

### The 14 Categories
girls_cant_do_math, science_is_for_boys, girls_arent_strong, boys_are_better_at_sports, girls_should_be_quiet, girls_cant_be_leaders, technology_is_for_boys, girls_cant_build_things, mom_gives_up_dreams, too_late_to_start, girls_cant_be_adventurous, girls_are_too_emotional, pretty_girls_arent_smart, girls_cant_do_dangerous_things

## Running Locally

```bash
# Terminal 1 — Backend
cd ~/EqualTales/backend
python3 -m pip install -r requirements.txt
python3 app.py
# Should print: "Running on http://127.0.0.1:5001"

# Terminal 2 — Frontend
cd ~/EqualTales/frontend
npm install
npm start
# Opens http://localhost:3000
```

Requires Python 3.10+ (for FastMCP) and Node.js.

## Development Commands

```bash
# Backend
cd ~/EqualTales/backend && python3 app.py          # Run Flask server (port 5001)

# Frontend
cd ~/EqualTales/frontend && npm start              # Run React dev server (port 3000)
cd ~/EqualTales/frontend && npm run build          # Production build

# Test the API manually
curl http://localhost:5001/api/health              # Health check
curl http://localhost:5001/api/examples            # Get example stereotypes
```

## Testing (Strict TDD)

### Backend Tests (pytest)
```bash
cd ~/EqualTales/backend

# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py -v

# Run specific test class
pytest tests/test_app.py::TestHealthEndpoint -v

# Run single test
pytest tests/test_app.py::TestHealthEndpoint::test_returns_200 -v
```

### Frontend Tests (Jest + React Testing Library)
```bash
cd ~/EqualTales/frontend

# Install test dependencies
npm install

# Run tests (watch mode)
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode (no watch)
npm run test:ci
```

### QA Agent (Continuous Monitoring)
```bash
cd ~/EqualTales

# Run all QA checks
python scripts/qa_agent.py

# Quick mode (skip coverage)
python scripts/qa_agent.py --quick

# Watch mode (re-run on file changes)
python scripts/qa_agent.py --watch

# Attempt to fix common issues
python scripts/qa_agent.py --fix

# Output as JSON (for CI)
python scripts/qa_agent.py --json
```

### Test Coverage Requirements
- **Backend**: 70% minimum (pytest-cov)
- **Frontend**: 70% minimum (Jest coverage)

### What's Tested

**Backend (test_app.py)**:
- All API routes (health, examples, women, categories, generate, generate/stream)
- Input validation (stereotype length, age bounds, name truncation)
- Edge cases (fallback classification, missing page fields, DALL-E failures, QA failures)
- SSE event streaming format
- Helper functions (_get_age_group, _generate_character_appearance, _sse)

**MCP Server (test_mcp_server.py)**:
- All 5 MCP tools (classify_stereotype, match_real_woman, generate_story, verify_story, generate_illustration)
- JSON parsing helper (_parse_json_response)
- Knowledge base validation
- Error handling (API failures, invalid JSON)

**Frontend (App.test.js)**:
- All 5 components (LandingPage, InputForm, GenerationProgress, TypewriterText, StorybookViewer)
- App state flow (landing → input → generating → storybook)
- User interactions (form submission, navigation, keyboard shortcuts)
- Error handling (connection errors, missing data)
- Edge cases (empty illustrations, missing prompts, QA failures)

## Judging Criteria
- Clarity 25%, Proof 25%, Usability 20%, Rigor 20%, Polish 10%
- No login — judges click "Try It Now" immediately
- Target: under 90 seconds generation, under 5 minutes total judge experience

## Important Gotchas
- Port is **5001** not 5000 (macOS AirPlay Receiver uses 5000)
- OpenRouter model IDs use dots not dashes: `anthropic/claude-opus-4.6` not `claude-opus-4-6`
- FastMCP requires Python 3.10+. If unavailable, server.py has a fallback stub class
- DALL-E image URLs expire after ~1 hour — fine for demo but not for persistence
- The `onComplete` callback in TypewriterText uses `useRef` to avoid infinite re-renders
- Story generation prompt tells Claude NOT to describe child's race in illustration descriptions — diversity is handled by the backend's random appearance system
