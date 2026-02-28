# EqualTales — Risk Log

**Project:** EqualTales
**Team:** Solo Builder

---

## Identified Risks & Mitigations

| Area | Issue Description | Severity | Fix Applied | Evidence/Link | Status |
|------|-------------------|----------|-------------|---------------|--------|
| **Security** | API keys (OPENROUTER_API_KEY, OPENAI_API_KEY) initially hardcoded in development | 🔴 Critical | Moved to `.env` file; added `.env` to `.gitignore`; created `.env.example` with placeholder values | `.gitignore:1`, `.env.example` | ✅ Fixed |
| **Ethics** | AI-generated stories amplify stereotypes 55% more than human-written ones (EMNLP 2025 research) | 🟠 Major | Built QA verification loop using Claude Sonnet 4.5 to detect stereotype reinforcement before displaying story; stories must score 7+/10 | `mcp_server/server.py:352-420` (verify_story tool) | ✅ Fixed |
| **Performance** | Initial sequential generation took ~150 seconds (classify → match → generate → verify → 5 illustrations) | 🟠 Major | Implemented parallel execution: QA + 5 illustrations run concurrently using ThreadPoolExecutor(max_workers=6); reduced to ~75-90 seconds | `backend/app.py:180-220` | ✅ Fixed |
| **Privacy** | Potential for storing user data (child names, stereotypes entered) | 🟡 Minor | Privacy by design: no database, no login, no cookies, no analytics; all data exists only in browser session | Architecture decision (no persistence layer) | ✅ Fixed |
| **Accessibility** | Initial UI lacked ARIA labels on interactive elements | 🟡 Minor | Added `aria-label` to all buttons, inputs, and navigation elements; tested with screen reader | `frontend/src/App.js:393-400` (page dots with aria-label) | ✅ Fixed |
| **Content Safety** | DALL-E could generate inappropriate illustrations for children's book | 🟡 Minor | Prompt engineering: explicit "suitable for ages 3-10" and "children's picture book" in every illustration prompt; DALL-E 3's built-in content filtering | `mcp_server/server.py:454-460` | ✅ Fixed |
| **Historical Accuracy** | Risk of AI hallucinating facts about real women | 🟠 Major | All 50 women in knowledge base manually verified against established historical record; AI uses only KB data, not general knowledge | `data/women_knowledge_base.json` (curated, verified) | ✅ Fixed |
| **Character Consistency** | DALL-E generates different-looking children across 5 pages | 🟠 Major | Created detailed character description template injected into every illustration prompt; description includes specific hair, skin, clothing details | `backend/app.py:50-80` (_generate_character_appearance) | ✅ Fixed |
| **Input Validation** | API crashes on null/malformed inputs (null stereotype, non-integer age, array body) | 🟠 Major | Added comprehensive input validation: type checking before .strip(), try/except for int conversion, dict validation for request body | `backend/app.py:158-175` | ✅ Fixed |
| **Injection Attacks** | Potential XSS/SQL injection via stereotype or child name fields | 🟡 Minor | No database (no SQL injection possible); React escapes output (XSS protected); added validation tests confirming safe handling | `backend/tests/test_app.py:598-605` | ✅ Fixed |

---

## Risk Categories Addressed

### Privacy & Data Protection
- **No user accounts** — Can't leak what we don't store
- **No analytics** — No tracking pixels, no third-party scripts
- **Session-only data** — Stories exist only in browser memory
- **No child data persistence** — Names/ages used only for generation

### Ethical AI Use
- **QA verification loop** — Every story checked for stereotype reinforcement
- **Transparency** — Clear messaging that stories are AI-generated
- **Human oversight** — Knowledge base manually curated and verified
- **Inclusive representation** — 10 diverse character appearances, 50 women from varied backgrounds

### Legal & IP Compliance
- **All dependencies MIT/BSD/Apache licensed** — See Evidence Log
- **Historical figures in public domain** — No licensing issues
- **No copyrighted content** — All stories freshly generated
- **API usage within terms** — OpenRouter, OpenAI TOS compliance

### Accessibility
- **Keyboard navigation** — Arrow keys and spacebar for story navigation
- **ARIA labels** — Screen reader support for all interactive elements
- **High contrast** — Warm colors with sufficient contrast ratios
- **Responsive design** — Works on mobile devices

---

## Monitoring & Ongoing Risks

| Risk | Mitigation | Monitoring |
|------|------------|------------|
| DALL-E image URL expiration (1 hour) | Acceptable for demo; would need image storage for production | Manual testing before demo |
| OpenRouter rate limits | $80 budget with usage monitoring | OpenRouter dashboard |
| Story quality variance | QA loop catches worst cases; manual spot-checking | QA scores in companion section |

---

*Risk Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
