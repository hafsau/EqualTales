# EqualTales — Decision Log

**Project:** EqualTales
**Team:** Solo Builder
**Timeline:** Feb 27 – Mar 7, 2026 (8 days)

---

## Technical Decisions

| # | Category | Decision → Why | Tradeoff |
|---|----------|----------------|----------|
| 1 | **Frontend** | React 18 with Create React App → Fastest setup for 8-day hackathon; built-in Jest testing | Slower builds than Vite; larger bundle; but setup time saved was critical |
| 2 | **Backend** | Flask over FastAPI → Simpler synchronous code; easier debugging for solo builder | No native async; but SSE works fine with `stream_with_context` |
| 3 | **AI Agent** | Goose + FastMCP → Hackathon requirement; MCP protocol provides clean tool boundaries | Adds architectural complexity; but enables autonomous orchestration |
| 4 | **LLM Routing** | OpenRouter for Claude → Sponsored hackathon credits; unified API for multiple Claude models | ~100ms additional latency; but essential for budget management |
| 5 | **Story Model** | Claude Opus 4.6 for story generation → Highest quality creative writing for children's narratives | ~55-60s generation; expensive ($15/M tokens); but story quality is core differentiator |
| 6 | **Utility Model** | Claude Sonnet 4.5 for classification + QA → Faster and cheaper for analytical tasks | Lower creativity; but classification/QA don't need creative writing ability |
| 7 | **Illustrations** | DALL-E 3 over Midjourney/SD → Best children's book illustration quality; consistent watercolor style | $0.04/image; but illustration quality critical for judges and UX |
| 8 | **Streaming** | SSE over WebSockets → One-way server-to-client; simpler; works through corporate firewalls | More complex than polling; but critical for 90-second generation UX |
| 9 | **Parallelization** | ThreadPoolExecutor for illustrations → 5 DALL-E calls + QA run concurrently | Higher momentary API load; but saves ~60 seconds off total generation |
| 10 | **Precomputed** | Hardcoded classifications for 10 example buttons → Skip classify API call entirely | Two copies to maintain; but saves ~5-8s for the most common demo path |
| 11 | **Story Structure** | 5-page arc (Belief→Question→Discovery→Inspiration→New Belief) → Proven storytelling structure | Less flexibility; but ensures consistent emotional journey |
| 12 | **Knowledge Base** | 50-woman curated JSON → Quality over quantity; manually verified historical accuracy | Limited coverage; but ensures every woman's facts are correct |
| 13 | **Character Diversity** | Backend randomization from 10 appearances → Injected into DALL-E prompts | Less user control; but ensures representation without asking sensitive questions |
| 14 | **Privacy** | No database, no login, no cookies → Privacy by design; can't leak what we don't store | No persistence; but appropriate for demo and eliminates privacy risks |
| 15 | **QA Loop** | AI verification for every story → Catches stereotype reinforcement | Adds ~5s to generation; but essential for ethical credibility (EMNLP 2025) |
| 16 | **Port** | Backend on 5001 → macOS AirPlay Receiver uses 5000 by default | Non-standard; but avoids "address already in use" errors |
| 17 | **Deployment** | Vercel (frontend) + Render (backend) → Free tier; SSE-compatible; auto-deploy from GitHub | Split architecture; but Vercel's serverless times out at 10s (our gen takes 75s) |
| 18 | **Accessibility** | WCAG AA compliance → Color contrast 4.5:1+, ARIA labels, keyboard nav | Slightly darker colors; but ensures usability for all |

---

## Key Architectural Choices Explained

### Why Goose + MCP?

EqualTales exposes **5 MCP tools** via a FastMCP server (`mcp_server/server.py`) that Goose can orchestrate autonomously:

| Tool | Model | Latency |
|------|-------|---------|
| `classify_stereotype` | Claude Sonnet 4.5 | ~3s (or 0s precomputed) |
| `match_real_woman` | Local KB lookup | <0.1s |
| `generate_story` | Claude Opus 4.6 | ~55s |
| `verify_story` | Claude Sonnet 4.5 | ~5s |
| `generate_illustration` | DALL-E 3 | ~15s each |

**Two runtime modes:**

| Mode | How | When |
|------|-----|------|
| **Direct** (`USE_GOOSE=false`) | Flask imports tool functions directly | Production/demo — maximum reliability |
| **Goose** (`USE_GOOSE=true`) | Goose orchestrates via stdio transport | Development — demonstrates full MCP pattern |

Both modes execute identical tool code. The difference is the orchestration layer. This is pragmatic engineering: the architecture proves MCP competence; the deployment choice proves production awareness.

### Why Opus 4.6 for Stories?

| Model Tested | Time | Quality | Verdict |
|-------------|------|---------|---------|
| Claude Sonnet 4 | ~15-20s | Good | "Stories feel generic" |
| Claude Sonnet 4.5 | ~20-25s | Better | "Missing depth" |
| Claude Sonnet 4.6 | ~40-50s | Excellent | "Engaging and meaningful" |
| Claude Opus 4.6 | ~55-60s | Outstanding | Best quality, acceptable wait |

We chose Opus 4.6 because EqualTales aims to reshape how children perceive gender. A mediocre story won't achieve this mission. The extra time is mitigated by progress indicators, wait tips, and parallel illustration generation.

### Why SSE Over WebSockets?

SSE is simpler for one-way server-to-client streaming. We don't need bidirectional communication — the client sends one request and receives a stream of progress events. SSE also works through corporate firewalls that block WebSocket upgrades.

### Why Vercel + Render?

| Requirement | Vercel (Frontend) | Render (Backend) |
|------------|-------------------|------------------|
| React SPA hosting | ✅ Global CDN, instant deploys | — |
| Python runtime | — | ✅ Native support |
| SSE streaming (75s+) | ❌ Serverless times out | ✅ Persistent processes |
| Free tier | ✅ 100GB bandwidth | ✅ 750 hours/month |
| HTTPS | ✅ Automatic | ✅ Automatic |

Split architecture matches our local dev setup and each platform's strengths.

### Why No Database?

Privacy by design. No user accounts, no stored stories, no tracking. Every story is generated fresh and exists only in the browser session. This eliminates privacy risks, simplifies architecture, and means there's nothing to breach.

---

*Decision Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
