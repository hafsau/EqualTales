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
| **AI Integration** | Claude Opus 4.6 for story generation → Highest quality creative writing | $15/M tokens (expensive); but story quality is core differentiator |
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
- **Opus 4.6** ($15/M tokens): Creative writing needs the best model. Stories are the core product.
- **Sonnet 4.5** ($3/M tokens): Classification and QA are analytical, not creative. 5x cheaper.

This hybrid approach keeps costs manageable while maintaining story quality.

### Why No Database?
Privacy by design. No user accounts, no stored stories, no tracking. Every story is generated fresh and exists only in the browser session. This eliminates privacy risks and simplifies architecture.

---

*Decision Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
