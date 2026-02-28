# EqualTales #75HER

**Mothers of children ages 3–10** get a **personalized, illustrated anti-stereotype story** in **under 90 seconds** — featuring real women who broke barriers.

---

## Problem Statement

### Who
Mothers of children ages 3–10 who want to counter gender stereotypes their children are absorbing.

### Problem
Children internalize gender stereotypes by **age 3**. By **age 6**, girls start believing boys are inherently "smarter." Existing counter-stereotype content is either:
- **Generic** ("girls can do anything!") — too vague to address specific beliefs
- **Biographical** — disconnected from the child's personal experience

### Impact
Early stereotypes shape career aspirations, self-confidence, and life choices. Without targeted intervention, these beliefs become deeply ingrained.

---

## Solution Overview

EqualTales is an **AI-powered web application** that generates personalized, illustrated children's stories designed to counter specific gender stereotypes.

A mother types the stereotype her child expressed (e.g., "my daughter thinks math is for boys"), enters the child's name and age, and receives a complete **5-page illustrated storybook** where a fictional child discovers a real woman who proved the stereotype wrong.

### Key Features

| Feature | Description | Why It Matters |
|---------|-------------|----------------|
| **Personalized Stories** | Child's name becomes the protagonist | Creates personal connection and identification |
| **Real Women Integration** | 50 historical women matched to stereotypes | Provides concrete proof, not abstract affirmation |
| **Age-Adaptive Content** | Stories adjust for ages 3-5, 6-8, 9-10 | Appropriate vocabulary and complexity |
| **QA Verification** | AI checks for stereotype reinforcement | Ensures stories don't amplify the bias they counter |
| **Illustrated Pages** | 5 DALL-E 3 watercolor illustrations | Engaging visual storytelling experience |

---

## Quick Start & Demo Path

### Requirements
- Python 3.10+
- Node.js 18+
- OpenRouter API key ($80 sponsored credits)
- OpenAI API key (for DALL-E 3)

### Installation

```bash
# Clone repository
git clone https://github.com/[your-username]/EqualTales.git
cd EqualTales

# Backend setup
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # Add your API keys

# Frontend setup
cd ../frontend
npm install

# Run both (in separate terminals)
cd backend && python3 app.py      # http://localhost:5001
cd frontend && npm start          # http://localhost:3000
```

### 60-Second Demo Path

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open http://localhost:3000 | Landing page with "Try It Now" button |
| 2 | Click "Try It Now" | Input form appears |
| 3 | Click "Girls can't do math" example | Stereotype text fills in |
| 4 | Enter child's name: "Lily" | Name field populated |
| 5 | Set age slider to 6 | Age selected |
| 6 | Click "Create My Story" | Progress screen with steps |
| 7 | Watch generation (~75 seconds) | See "Featuring Katherine Johnson" reveal |
| 8 | View storybook | 5 illustrated pages with navigation |
| 9 | Click through to "Discussion & Activities" | See discussion prompts + QA badge |

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     React 18 (Port 3000)                     │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Landing │→ │  Input   │→ │  Progress  │→ │ Storybook  │  │
│  │  Page   │  │   Form   │  │   Screen   │  │   Viewer   │  │
│  └─────────┘  └──────────┘  └────────────┘  └────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ SSE Stream
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                   Flask API (Port 5001)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  /api/generate/stream                 │   │
│  │  classify → match → generate → [verify + illustrate] │   │
│  │                                    (parallel)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Claude     │  │   Claude     │  │   DALL-E 3   │
│  Opus 4.6    │  │  Sonnet 4.5  │  │   (OpenAI)   │
│  (Stories)   │  │  (QA/Class)  │  │ (Illustrations)│
│  OpenRouter  │  │  OpenRouter  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18.2 | Single-page application with storybook UI |
| Backend | Flask 3.0 | REST API with SSE streaming |
| AI Agent | Goose + FastMCP | MCP tool orchestration |
| Story Generation | Claude Opus 4.6 | High-quality creative writing |
| Classification/QA | Claude Sonnet 4.5 | Fast analytical tasks |
| Illustrations | DALL-E 3 | Children's book watercolor style |
| Hosting | Vercel + Render | Frontend + backend deployment |

### Goose Integration

EqualTales uses **Goose** (Block's open-source AI agent framework) with **FastMCP** to expose 5 tools:

1. `classify_stereotype` — Categorizes input and selects counter-narrative strategy
2. `match_real_woman` — Finds best woman from 50-entry knowledge base
3. `generate_story` — Creates 5-page narrative with discussion prompts
4. `verify_story` — QA check for stereotype reinforcement (score 1-10)
5. `generate_illustration` — DALL-E 3 call with character consistency

---

## Story Structure

Each story follows a 5-page narrative arc:

| Page | Title | Purpose |
|------|-------|---------|
| 1 | **The Belief** | Fictional child encounters/expresses the stereotype |
| 2 | **The Question** | Something cracks the stereotype — curiosity emerges |
| 3 | **The Discovery** | Child discovers a real woman who defied it |
| 4 | **The Inspiration** | Real woman's achievement told in fairy-tale language |
| 5 | **The New Belief** | Child takes action, stereotype replaced by understanding |

---

## Project Logs & Documentation

| Document | Description | Location |
|----------|-------------|----------|
| Decision Log | 15 key technical choices with tradeoffs | [docs/DECISION_LOG.md](docs/DECISION_LOG.md) |
| Risk Log | 8 issues identified and fixed | [docs/RISK_LOG.md](docs/RISK_LOG.md) |
| Evidence Log | 14 sources with licenses | [docs/EVIDENCE_LOG.md](docs/EVIDENCE_LOG.md) |
| AI Trace Log | 7 AI usage entries with verification | [docs/AI_TRACE_LOG.md](docs/AI_TRACE_LOG.md) |
| Problem Frame | 4-line problem definition | [docs/PROBLEM_FRAME.md](docs/PROBLEM_FRAME.md) |

---

## Testing & Known Issues

### Test Results

```bash
# Backend (pytest)
cd backend && pytest tests/ -v
# Result: 149 passed, 2 skipped in 0.68s

# Frontend (Jest)
cd frontend && npm test
# Result: 24 passed, 25 skipped (SSE mocking complexity)
```

### Test Coverage

| Area | Tests | Coverage |
|------|-------|----------|
| API Routes | 50+ | All 6 endpoints |
| MCP Tools | 50+ | All 5 tools |
| Input Validation | 20+ | All edge cases including XSS, injection |
| Integration Tests | 14 | E2E pipeline, error recovery, performance |
| React Components | 24 | Landing, Input, Error handling |

### Known Issues

| Issue | Workaround | Status |
|-------|------------|--------|
| DALL-E URLs expire after ~1 hour | Acceptable for demo; would need storage for production | Documented |
| SSE tests skipped in Jest | Integration tests with real backend recommended | By design |
| Generation time ~75-90s | Progress indicators + parallel generation | Optimized |

### Future Improvements

- [ ] Image persistence (S3/Cloudinary)
- [ ] Multi-language support
- [ ] PDF export
- [ ] Parent dashboard

---

## Project Structure

```
EqualTales/
├── backend/
│   ├── app.py              # Flask API (port 5001)
│   ├── requirements.txt    # Production dependencies
│   ├── requirements-dev.txt # Test dependencies
│   ├── conftest.py         # pytest fixtures
│   └── tests/              # 117 pytest tests
├── frontend/
│   ├── src/
│   │   ├── App.js          # React app (5 components)
│   │   ├── App.css         # Warm storybook design
│   │   └── App.test.js     # Jest tests
│   └── package.json
├── mcp_server/
│   └── server.py           # FastMCP (5 tools)
├── scripts/
│   └── qa_agent.py         # QA monitoring agent
├── data/
│   └── women_knowledge_base.json  # 50 women, 14 categories
├── docs/
│   ├── PROBLEM_FRAME.md
│   ├── DECISION_LOG.md
│   ├── RISK_LOG.md
│   ├── EVIDENCE_LOG.md
│   └── AI_TRACE_LOG.md
├── .env                    # API keys (not committed)
├── CLAUDE.md               # Claude Code context
└── README.md               # This file
```

---

## Team & Acknowledgments

### Team: Solo Builder

| Name | Role | GitHub | LinkedIn |
|------|------|--------|----------|
| [Your Name] | Full-Stack + AI/ML | [@username](https://github.com/username) | [Profile](https://linkedin.com/in/username) |

### Special Thanks

- **CreateHER Fest** — For the #75HER Challenge opportunity
- **Block** — For Goose and the $80 OpenRouter credits
- **Anthropic** — For Claude's exceptional creative writing
- **OpenAI** — For DALL-E 3's beautiful illustrations

---

## License & Attributions

### Project License
MIT License

### Dependencies

| Package | License | Link |
|---------|---------|------|
| React | MIT | https://react.dev |
| Flask | BSD-3-Clause | https://flask.palletsprojects.com |
| FastMCP | MIT | https://github.com/jlowin/fastmcp |
| OpenAI SDK | MIT | https://github.com/openai/openai-python |
| Goose | Apache 2.0 | https://github.com/block/goose |
| Quicksand Font | SIL OFL | https://fonts.google.com/specimen/Quicksand |
| DM Sans Font | SIL OFL | https://fonts.google.com/specimen/DM+Sans |
| Caveat Font | SIL OFL | https://fonts.google.com/specimen/Caveat |

---

Built with love for **#75HER Challenge** | **CreateHER Fest 2026**
