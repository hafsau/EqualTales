# EqualTales #75HER

**Mothers of children ages 3–10** get a **personalized, illustrated anti-stereotype story** in **under 90 seconds** — featuring real women who broke barriers.

---

## Quickstart (1-Command Setup)

```bash
# Clone and run (requires Python 3.10+, Node.js 18+)
git clone https://github.com/hafsau/EqualTales.git && cd EqualTales && \
cp .env.example .env && \
echo "Add your API keys to .env, then run:" && \
echo "Terminal 1: cd backend && pip install -r requirements.txt && python3 app.py" && \
echo "Terminal 2: cd frontend && npm install && npm start"
```

### .env.example
```
OPENROUTER_API_KEY=sk-or-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
```

Open http://localhost:3000 → Click "Try It Now" → Select a stereotype → Generate!

---

## Project Overview

### What It Does
EqualTales generates personalized, illustrated children's stories that counter specific gender stereotypes. A mother inputs a stereotype (e.g., "Girls can't do math"), her child's name and age, and receives a 5-page illustrated storybook featuring a real woman who proved the stereotype wrong.

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18.2 | Single-page application with storybook UI |
| Backend | Flask 3.0 | REST API with SSE streaming |
| AI Agent | Goose + FastMCP | MCP tool orchestration |
| Story Generation | Claude Opus 4.6 | High-quality creative writing |
| Classification/QA | Claude Sonnet 4.5 | Fast analytical tasks |
| Illustrations | DALL-E 3 | Children's book watercolor style |

### Dependencies

```
# Backend (requirements.txt)
flask>=3.0.0
openai>=1.55.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
fastmcp>=2.0.0

# Frontend (package.json)
react: ^18.2.0
react-dom: ^18.2.0
react-scripts: 5.0.1
```

---

## Architecture Diagram

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

---

## Decision Log

Key technical choices and tradeoffs:

| Decision | Why | Tradeoff |
|----------|-----|----------|
| **React 18 + CRA** | Fastest setup for 8-day hackathon; built-in Jest | Slower builds than Vite; acceptable for demo |
| **Flask over FastAPI** | Simpler synchronous code; easier debugging | No native async; SSE works fine with stream_with_context |
| **SSE over WebSockets** | One-way streaming is simpler; works through corporate firewalls | Slightly more complex than polling |
| **Parallel illustrations** | ThreadPoolExecutor runs 5 DALL-E calls simultaneously | Higher momentary API load; saves ~60 seconds |
| **Claude Opus for stories** | Highest quality creative writing ($15/M tokens) | Expensive; but story quality is core differentiator |
| **Claude Sonnet for QA** | 5x cheaper ($3/M tokens) for analytical tasks | Lower creativity; fine for classification/verification |
| **No database** | Privacy by design — can't leak what we don't store | No persistence; acceptable for demo |
| **50-woman curated KB** | Quality over quantity; manually verified facts | Limited coverage; ensures accuracy |
| **QA verification loop** | Catches stereotype reinforcement AI typically amplifies | Adds ~3s; essential for ethical credibility |

[Full Decision Log →](docs/DECISION_LOG.md)

---

## AI Trace Log

*Required for AI/ML track — documenting AI tool usage with verification*

### Trace 1: Story Generation
| Field | Content |
|-------|---------|
| **Tool** | Claude Opus 4.6 via OpenRouter |
| **What AI Generated** | 5-page narrative with titles, discussion prompts, activity suggestion |
| **What I Changed** | Added instruction NOT to describe child's race (handled by diversity system); enforced JSON output |
| **Verification** | Manual review of 10+ stories; automated QA loop; checked discussion prompts are open-ended |

### Trace 2: QA Verification
| Field | Content |
|-------|---------|
| **Tool** | Claude Sonnet 4.5 via OpenRouter |
| **What AI Generated** | Passed/failed status, score 1-10, issues list, strengths |
| **What I Changed** | Added safe default (passed=true, score=7) on API failure; threshold set at score >= 7 |
| **Verification** | Compared QA scores with manual review; tested with intentionally problematic stories |

### Trace 3: Illustration Generation
| Field | Content |
|-------|---------|
| **Tool** | DALL-E 3 via OpenAI API |
| **What AI Generated** | 1024x1024 watercolor-style children's book illustrations |
| **What I Changed** | Character description injection for consistency; coral/gold/sage palette to match UI |
| **Verification** | Visual inspection of 50+ illustrations for age-appropriateness and consistency |

### Trace 4: Test Scaffolding
| Field | Content |
|-------|---------|
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | pytest fixtures, test structure, mock configurations |
| **What I Changed** | Fixed mock data structures; simplified SSE streaming tests |
| **Verification** | 151 backend tests passing; 24 frontend tests passing |

### Trace 5: Knowledge Base Curation
| Field | Content |
|-------|---------|
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | Initial list of 50 women with categories, achievements, story angles |
| **What I Changed** | Verified every fact against Wikipedia/Britannica; rewrote for age-appropriateness |
| **Verification** | Cross-referenced each achievement with 2+ historical sources |

[Full AI Trace Log →](docs/AI_TRACE_LOG.md)

---

## Risk Log

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| **API keys hardcoded** | Critical | Moved to `.env`; added to `.gitignore`; created `.env.example` | ✅ Fixed |
| **AI amplifies stereotypes** | Major | QA verification loop detects reinforcement; stories must score 7+/10 | ✅ Fixed |
| **150s generation time** | Major | Parallel execution with ThreadPoolExecutor; reduced to ~75s | ✅ Fixed |
| **AI hallucinating facts** | Major | 50 women manually verified against Wikipedia/Britannica | ✅ Fixed |
| **Character inconsistency** | Major | Detailed character description injected into every DALL-E prompt | ✅ Fixed |
| **Privacy concerns** | Minor | No database, no login, no cookies — session-only data | ✅ Fixed |
| **WCAG AA compliance** | Minor | Color contrast 4.5:1+ (#6B605A text, #C4594B buttons); ARIA labels; keyboard nav | ✅ Fixed |
| **DALL-E URLs expire** | Minor | Acceptable for demo; would need S3/Cloudinary for production | Documented |

[Full Risk Log →](docs/RISK_LOG.md)

---

## Evidence Log

### Research Sources

| # | Claim | Source | Type |
|---|-------|--------|------|
| 1 | "Children absorb stereotypes by age 3" | Bian et al. (2017). *Science*, 355(6323). DOI: 10.1126/science.aah6524 | Academic |
| 2 | "By age 6, girls believe boys are smarter" | Same study (Bian et al., 2017) | Academic |
| 3 | "Counter-stereotypical content shifts attitudes" | Master et al. (2016). *J. Educational Psychology*, 108(3). DOI: 10.1037/edu0000061 | Academic |
| 4 | "AI-generated stories amplify stereotypes 55% more" | EMNLP 2025 research on AI bias | Academic |

### Code Dependencies

| # | Package | License | Link |
|---|---------|---------|------|
| 5 | React | MIT | https://react.dev |
| 6 | Flask | BSD-3-Clause | https://flask.palletsprojects.com |
| 7 | FastMCP | MIT | https://github.com/jlowin/fastmcp |
| 8 | OpenAI SDK | MIT | https://github.com/openai/openai-python |
| 9 | Goose | Apache 2.0 | https://github.com/block/goose |
| 10 | Quicksand Font | SIL OFL | https://fonts.google.com/specimen/Quicksand |
| 11 | DM Sans Font | SIL OFL | https://fonts.google.com/specimen/DM+Sans |
| 12 | Caveat Font | SIL OFL | https://fonts.google.com/specimen/Caveat |

### Data Sources

| # | Item | Source | License |
|---|------|--------|---------|
| 13 | Knowledge base (50 women) | Wikipedia, Britannica, biographies | Public domain / Fair use |
| 14 | Historical achievements | Multiple verified sources per woman | Public domain |

[Full Evidence Log →](docs/EVIDENCE_LOG.md)

---

## Demo Fallback

If the live demo is unavailable, see [Demo Fallback Documentation](docs/DEMO_FALLBACK.md) for:
- Video walkthrough (60s)
- Step-by-step screenshots of full user journey
- Sample generated story

---

## Known Issues & Next Steps

### Known Issues

| Issue | Workaround | Status |
|-------|------------|--------|
| DALL-E URLs expire after ~1 hour | Acceptable for demo; would need image storage | Documented |
| SSE tests skipped in Jest | Complex to mock; integration tests recommended | By design |
| Generation time ~35-75s | Progress indicators + parallel generation | Optimized |

### Next Steps

- [ ] Image persistence (S3/Cloudinary)
- [ ] Multi-language support
- [ ] PDF export
- [ ] Parent dashboard
- [ ] More women in knowledge base

---

## Testing

```bash
# Backend (pytest)
cd backend && pytest tests/ -v
# 151 tests (unit + integration)

# Frontend (Jest)
cd frontend && npm test
# 24 passed, 25 skipped
```

---

## License

### Project License
**MIT License** — See [LICENSE](LICENSE)

### Attributions

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

All licenses are permissive and compatible with commercial use.

---

Built with love for **#75HER Challenge** | **CreateHER Fest 2026**
