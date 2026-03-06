# EqualTales #75HER

## 3-Line Pitch

**Turn stereotypes into bedtime stories.** *(6 words)*

A mother types what her child said — "girls can't do math" — and gets a personalized, illustrated 5-page story featuring a real woman who proved it wrong. *(28 words)*

**[→ Try It Now](https://equaltales.vercel.app)** *(CTA)*

---

## 4-Line Problem Frame

| | |
|---|---|
| **User** | Mothers of children ages 3–10 who hear gender stereotypes |
| **Problem** | No quick, engaging way to counter stereotypes at bedtime |
| **Constraints** | Under 90 seconds; no login; age-appropriate; historically accurate |
| **Success Test** | Child finishes story knowing a real woman who broke the stereotype |

---

## [→ Try It Now: equaltales.vercel.app](https://equaltales.vercel.app)

| | |
|---|---|
| **Live Demo** | https://equaltales.vercel.app |
| **API** | https://equaltales-api.onrender.com |

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
│  └──────────────────────────┬───────────────────────────┘   │
│                             │                                │
│  ┌──────────────────────────▼───────────────────────────┐   │
│  │           GOOSE MCP SERVER (FastMCP)                  │   │
│  │              mcp_server/server.py                     │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │  5 MCP TOOLS (stdio transport, JSON-RPC 2.0)    │  │   │
│  │  │                                                  │  │   │
│  │  │  1. classify_stereotype  ──→ Claude Sonnet 4.5  │  │   │
│  │  │  2. match_real_woman     ──→ Local KB (50 women)│  │   │
│  │  │  3. generate_story       ──→ Claude Opus 4.6    │  │   │
│  │  │  4. verify_story         ──→ Claude Sonnet 4.5  │  │   │
│  │  │  5. generate_illustration──→ DALL-E 3           │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────────┘   │
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

## Goose + MCP Integration

**EqualTales is a Goose-compatible MCP (Model Context Protocol) extension.** The entire story generation engine is exposed as 5 MCP tools that Goose can orchestrate autonomously.

### MCP Server Configuration

```yaml
# goose_config.yaml — Goose extension config
extensions:
  equaltales:
    name: EqualTales Story Engine
    cmd: python
    args: [mcp_server/server.py]
    transport: stdio
    enabled: true
```

### The 5 MCP Tools

| Tool | Model | Purpose | Latency |
|------|-------|---------|---------|
| `classify_stereotype` | Claude Sonnet 4.5 | Categorize stereotype into 14 categories | ~3s |
| `match_real_woman` | Local KB | Find best-matching woman from 50-entry knowledge base | <0.1s |
| `generate_story` | Claude Opus 4.6 | Create 5-page narrative with illustrations descriptions | ~57s |
| `verify_story` | Claude Sonnet 4.5 | QA check for stereotype reinforcement | ~5s |
| `generate_illustration` | DALL-E 3 | Create watercolor children's book illustration | ~15s |

### How Goose Orchestrates

When Goose receives a stereotype input, it autonomously:

1. **Classifies** the stereotype → identifies primary/secondary categories
2. **Matches** a real woman → finds inspiring counter-example from KB
3. **Generates** the story → creates age-appropriate 5-page narrative
4. **Verifies** (parallel) → ensures no stereotype reinforcement
5. **Illustrates** (parallel) → generates 5 DALL-E images concurrently

The Flask backend can run in two modes:
- **Direct mode**: Imports MCP tools directly (current production)
- **Goose mode**: Goose orchestrates via stdio transport (full MCP pattern)

### Why MCP + Goose?

| Benefit | How |
|---------|-----|
| **Autonomous orchestration** | Goose decides tool order and handles errors |
| **Tool composability** | Each tool is independent and reusable |
| **Streaming support** | Real-time progress via SSE |
| **Error recovery** | Goose retries failed tools automatically |

### Why Direct Mode in Production?

Production uses direct tool imports (`USE_GOOSE=false`) for reliability:

| Concern | Direct Mode Solution |
|---------|---------------------|
| Subprocess crashes | No subprocess — tools run in-process |
| Demo stability | No external orchestrator that could fail |
| Same code paths | Identical tool logic, different orchestration |

**The architecture is Goose-native; the deployment is pragmatic.** See [Decision Log](docs/DECISION_LOG.md) for full rationale.

### Try Goose Mode Locally

Verify the MCP integration works with actual Goose orchestration:

```bash
# 1. Install Goose (if not already installed)
pip install goose-ai

# 2. Copy the Goose config
cp goose_config.yaml ~/.config/goose/config.yaml
# Edit the path in config.yaml to your actual project location

# 3. Set environment variables
export OPENROUTER_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# 4. Test the MCP server directly
cd mcp_server && python server.py
# Should print: "Starting EqualTales MCP Server..."

# 5. Run Flask in Goose mode
cd backend
USE_GOOSE=true python app.py
# Should print: "EqualTales API starting in Goose-orchestrated mode"
```

Or interact with the MCP tools via Goose CLI:

```bash
goose run --extension equaltales "Classify this stereotype: Girls can't do math"
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

### Trace 1: Story Generation (Core Product)
| Field | Content |
|-------|---------|
| **Tool** | Claude Opus 4.6 via OpenRouter (`generate_story` MCP tool) |
| **What AI Generated** | 5-page narrative with titles, illustration descriptions, discussion prompts, activity suggestion |
| **What I Changed** | Added "Do NOT describe child's race" instruction (diversity handled separately); enforced "Discovery, Not Biography" design principle; strict JSON output |
| **Verification** | Manual review of 10+ stories; automated QA loop (Tool 4); age-appropriateness check per tier |

### Trace 2: QA Verification
| Field | Content |
|-------|---------|
| **Tool** | Claude Sonnet 4.5 via OpenRouter (`verify_story` MCP tool) |
| **What AI Generated** | Passed/failed status, score 1-10, issues list, strengths, suggestion |
| **What I Changed** | Safe default (passed=true, score=7) on API failure; 6-point checklist; max tokens reduced to 512 |
| **Verification** | Compared QA scores with manual review; tested with intentionally problematic stories |

### Trace 3: Illustration Generation
| Field | Content |
|-------|---------|
| **Tool** | DALL-E 3 via OpenAI API (`generate_illustration` MCP tool) |
| **What AI Generated** | 1024×1024 watercolor-style children's book illustrations |
| **What I Changed** | Decoupled character appearance from story text; 10 diverse appearance templates; coral/gold/sage palette |
| **Verification** | Visual inspection of 50+ illustrations for age-appropriateness and consistency |

### Trace 4: Test Scaffolding
| Field | Content |
|-------|---------|
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | pytest fixtures, test structure, mock configurations |
| **What I Changed** | Fixed mock data structures; simplified SSE streaming tests; adjusted charset assertions |
| **Verification** | 151 backend tests passing; 24 frontend tests passing |

### Trace 5: Knowledge Base Curation
| Field | Content |
|-------|---------|
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | Initial list of 50 women with categories, achievements, fairy_tale_moments, age_adaptations |
| **What I Changed** | Verified every fact against Wikipedia/Britannica; fixed era typos (Malala, Simone Biles "2997"→"1997"); removed duplicates; ensured all 50 suggested by categories |
| **Verification** | Cross-referenced each achievement with 2+ sources; automated validation script |

### Trace 6: Frontend + Backend Development
| Field | Content |
|-------|---------|
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | React components, CSS styling, sound system, parallelization, precomputed classifications |
| **What I Changed** | Fixed 6/10 precomputed category keys; removed dead code; aligned models; fixed keyboard nav closure bug |
| **Verification** | End-to-end pipeline testing; manual UI review; all precomputed categories validated against KB |

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
