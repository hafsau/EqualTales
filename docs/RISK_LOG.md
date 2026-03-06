# EqualTales — Risk Log

**Project:** EqualTales
**Team:** Solo Builder
**Timeline:** Feb 27 – Mar 7, 2026

---

## Identified Risks & Mitigations

| # | Area | Risk | Severity | Mitigation | Status |
|---|------|------|----------|------------|--------|
| 1 | **Security** | API keys (OPENROUTER_API_KEY, OPENAI_API_KEY) could be exposed in source code | 🔴 Critical | Moved to `.env` file; added `.env` to `.gitignore`; created `.env.example` with placeholders; Render/Vercel env vars set via dashboard | ✅ Fixed |
| 2 | **Ethics** | AI-generated stories amplify stereotypes 55% more than human-written ones (EMNLP 2025) | 🟠 Major | Built `verify_story` MCP tool using Claude Sonnet 4.5; stories must score 7+/10; 6-point checklist for stereotype reinforcement, new stereotypes, preachy language, forced biography, unrealistic endings, gendered descriptions | ✅ Fixed |
| 3 | **Performance** | Sequential pipeline took ~150s (classify → match → generate → verify → 5× illustrate) | 🟠 Major | Parallelized: QA + 5 illustrations run concurrently via `ThreadPoolExecutor(max_workers=6)`; precomputed classifications for 10 example buttons (saves ~5-8s); reduced to ~60-90s total | ✅ Fixed |
| 4 | **Accuracy** | AI could hallucinate facts about real historical women | 🟠 Major | All 50 women in knowledge base manually verified against Wikipedia/Britannica; AI uses only KB-provided data (achievement, fairy_tale_moment, age_adaptations), not general knowledge | ✅ Fixed |
| 5 | **Visual** | DALL-E 3 generates different-looking children across 5 pages | 🟠 Major | `_generate_character_appearance()` creates detailed description (skin, hair, clothing) injected into every illustration prompt; 10 diverse appearance templates ensure representation | ✅ Fixed |
| 6 | **Input** | API crashes on null/malformed inputs (null stereotype, non-integer age, array body) | 🟠 Major | Comprehensive validation: type checking before `.strip()`, `try/except` for int conversion, dict validation for request body, min length 3, max length 500, name truncated to 30 chars | ✅ Fixed |
| 7 | **Privacy** | Potential for storing/leaking user data (child names, stereotypes) | 🟡 Minor | Privacy by design: no database, no login, no cookies, no analytics; all data exists only in browser session; nothing to breach | ✅ Fixed |
| 8 | **Accessibility** | UI lacked ARIA labels; color contrast below WCAG AA | 🟡 Minor | Added `aria-label` to all buttons/inputs/navigation; keyboard navigation (arrow keys, spacebar); contrast updated to 4.5:1+ for all text; alt text on all images | ✅ Fixed |
| 9 | **Content Safety** | DALL-E could generate inappropriate illustrations | 🟡 Minor | Prompt engineering: explicit "suitable for ages 3-10" and "children's picture book" constraints; DALL-E 3's built-in content filtering; `standard` quality (not `hd`) for faster, safer output | ✅ Fixed |
| 10 | **Injection** | XSS/SQL injection via stereotype or child name fields | 🟡 Minor | No database (no SQL injection possible); React auto-escapes output (XSS protected); input length limits enforced server-side | ✅ Fixed |
| 11 | **Availability** | DALL-E image URLs expire after ~1 hour | 🟡 Minor | Acceptable for demo scope; would need S3/Cloudinary for production; fallback story with local images saved in `data/fallback/` | Documented |
| 12 | **Availability** | Render free tier cold-starts (~30s first request) | 🟡 Minor | Health check endpoint keeps service warm; judges warned to expect initial load time | Documented |
| 13 | **Demo** | APIs fail during live demo | 🟠 Major | Fallback story pre-generated and saved locally (`data/fallback/fallback_story.json` + 5 PNGs); Maya, age 6, "Girls can't do math", Katherine Johnson, QA score 9/10 | ✅ Built |

---

## Risk Categories

### Privacy & Data Protection
- **No user accounts** — Can't leak what we don't store
- **No analytics** — No tracking pixels, no third-party scripts
- **Session-only data** — Stories exist only in browser memory
- **No child data persistence** — Names/ages used only for generation, never saved

### Ethical AI Use
- **QA verification loop** — Every story checked for stereotype reinforcement (6-point checklist)
- **Discovery, Not Biography** — Design principle ensures stories show, don't tell
- **Human-curated KB** — 50 women manually verified; AI doesn't invent historical facts
- **Inclusive representation** — 10 diverse character appearances; 50 women from varied backgrounds, eras, and fields
- **EMNLP 2025 citation** — QA tool grounded in research showing AI amplifies stereotypes

### Legal & IP Compliance
- **All dependencies permissively licensed** — MIT, BSD-3-Clause, Apache 2.0, SIL OFL
- **Historical figures in public domain** — No licensing issues for biographical facts
- **No copyrighted content** — All stories freshly generated per request
- **API terms compliance** — OpenRouter and OpenAI TOS followed

### Accessibility (WCAG AA)
- **Keyboard navigation** — Arrow keys, spacebar, tab for full app navigation
- **Touch/swipe** — Mobile gesture support with visual feedback
- **ARIA labels** — Screen reader support for all interactive elements
- **WCAG AA contrast** — All text meets 4.5:1 ratio minimum
- **Alt text** — All illustrations have descriptive alt attributes from scene descriptions
- **Responsive** — 5 breakpoints: 1024px, 768px, 640px, 480px, 375px
- **Dark mode** — Respects system preference; manual toggle available

---

*Risk Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
