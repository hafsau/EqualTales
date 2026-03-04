# EqualTales — Decision Log

**Project:** EqualTales
**Team:** Solo Builder

---

## Technical Decisions

| Category | Decision → Why | Tradeoff |
|----------|----------------|----------|
| **Tech Stack** | React 18 with Create React App → Fastest setup for hackathon, familiar tooling, built-in Jest testing | Slower builds than Vite; larger bundle size; but setup time saved was critical for 8-day timeline |
| **Tech Stack** | Flask over FastAPI → Simpler synchronous code for rapid prototyping; easier debugging | No native async; but SSE works fine with Flask's `stream_with_context` |
| **Tech Stack** | Python 3.10+ → Required for FastMCP library compatibility | Limits deployment options slightly; but FastMCP is essential for Goose integration |
| **Architecture** | Server-Sent Events (SSE) for streaming → Real-time progress updates; progressive text display | More complex than polling; but critical for 90-second generation UX |
| **Architecture** | Port 5001 instead of 5000 → macOS AirPlay Receiver uses port 5000 by default | Non-standard port; but avoids "address already in use" errors for Mac developers |
| **Architecture** | Parallel illustration generation with ThreadPoolExecutor → 5 DALL-E calls run simultaneously | Higher momentary API load; but reduces total generation time by ~60 seconds |
| **AI Integration** | OpenRouter for Claude API → $80 sponsored hackathon credits; unified API for multiple models | Additional latency (~100ms); but essential for budget management |
| **AI Integration** | Claude Sonnet 4.6 for story generation → Best balance of quality and speed (see detailed analysis below) | ~40-50s generation time; but story quality justifies the wait |
| **AI Integration** | Claude Sonnet 4.5 for classification + QA → Faster and cheaper for analytical tasks | Lower creativity; but classification/QA don't need creative writing ability |
| **AI Integration** | DALL-E 3 over Midjourney/SD → Best children's book illustration quality; consistent style | $0.04-0.08/image (expensive); but illustration quality critical for judges |
| **Feature Scope** | 5-page narrative arc (Belief→Question→Discovery→Inspiration→New Belief) → Proven storytelling structure | Less flexibility for edge cases; but ensures consistent emotional journey |
| **Feature Scope** | 50-woman curated knowledge base → Quality over quantity; verified historical accuracy | Limited coverage; but ensures every woman's story is accurate and age-appropriate |
| **Data** | Character diversity via backend randomization → 10 diverse appearances injected into DALL-E prompts | Less user control; but ensures representation without asking sensitive questions |
| **Testing** | Strict TDD with pytest + Jest → 117 backend tests, 24 frontend tests | Slower initial development; but caught edge cases before demo day |
| **Process** | QA verification loop for every story → Catches stereotype reinforcement AI typically amplifies | Adds ~3 seconds to generation; but essential for ethical credibility |
| **Accessibility** | WCAG AA compliance → Color contrast 4.5:1+ for text, ARIA labels, keyboard navigation | Slightly darker colors than original design; but ensures usability for all users |
| **Accessibility** | Grade-8 reading level for UI text → Mothers with varying literacy can use the app | Simpler vocabulary; but appropriate for target audience |

---

## Key Architectural Choices Explained

### Why SSE Over WebSockets?
SSE is simpler for one-way server-to-client streaming. We don't need bidirectional communication — the client sends one request and receives a stream of events. SSE also works through corporate firewalls that block WebSocket upgrades.

### Why Separate Models for Different Tasks?
- **Sonnet 4.6** for story generation: Best balance of quality and speed for creative writing.
- **Sonnet 4.5** ($3/M tokens): Classification and QA are analytical, not creative. Cheaper and faster.

This hybrid approach keeps costs manageable while maintaining story quality.

### Story Generation Model Deliberation (March 2026)

**The Challenge:** Story generation is the heart of EqualTales. We needed to balance:
1. **Story Quality** — Children's counter-stereotype narratives must be emotionally resonant
2. **Wait Time** — Users shouldn't wait too long; judges have limited demo time

**Models Tested:**

| Model | Generation Time | Story Quality | User Feedback |
|-------|----------------|---------------|---------------|
| `claude-sonnet-4` | ~15-20s | Good | "Stories feel a bit generic" |
| `claude-sonnet-4.5` | ~20-25s | Better | "Improved but still missing depth" |
| `claude-sonnet-4.6` | ~40-50s | Excellent | "Stories are engaging and meaningful" |
| `claude-opus-4.6` | ~60-90s | Outstanding | "Amazing but wait is too long" |

**Total Generation Time Breakdown (with Sonnet 4.6):**
- Classification: ~0s (precomputed for examples) or ~10-15s (custom input)
- Story generation: ~40-50s
- 5 Illustrations (DALL-E 3): ~30-40s (parallel but rate-limited)
- **Total: ~70-90s for examples, ~90-110s for custom text**

**Decision: Claude Sonnet 4.6**

We chose Sonnet 4.6 because:

1. **Quality is non-negotiable**: EqualTales aims to reshape how children perceive gender. A mediocre story won't achieve this mission. The extra 20-30 seconds over Sonnet 4 is worth it.

2. **Acceptable total time**: With precomputed classifications for the 10 example buttons and parallel illustration generation, most demos complete in under 90 seconds.

3. **User testing feedback**: Early testers consistently preferred longer waits with better stories over faster, less engaging narratives.

4. **Hackathon judges evaluate quality**: A compelling 80-second story beats a forgettable 40-second one.

**Mitigations for Wait Time:**
- Progress indicators with 5-step visual feedback
- "Did you know?" educational tips rotating every 8 seconds
- "Featuring [Woman's Name]" reveal card to build anticipation
- Precomputed classifications for example buttons (saves ~25s)
- QA runs in background after "story ready" (saves ~5-10s perceived time)

### Why No Database?
Privacy by design. No user accounts, no stored stories, no tracking. Every story is generated fresh and exists only in the browser session. This eliminates privacy risks and simplifies architecture.

---

*Decision Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
