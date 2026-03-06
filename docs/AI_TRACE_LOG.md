# EqualTales — AI Trace Log

**Project:** EqualTales
**Team:** Solo Builder
**Principle:** Augment, Not Abdicate — Every AI output reviewed and verified by a human before use.

---

## AI Usage Traces

### Trace 1: Story Generation (Core Product)

| Field | Content |
|-------|---------|
| **Category** | Content Generation |
| **Tool** | Claude Opus 4.6 via OpenRouter |
| **MCP Tool** | `generate_story` in `mcp_server/server.py` |
| **Input** | Stereotype text, child name/age, matched woman's profile (name, achievement, fairy_tale_moment, age_adaptation), counter_message |
| **Prompt Design** | Structured 5-page narrative arc (Belief → Question → Discovery → Inspiration → New Belief) with age-specific writing rules (young: 5-10 word sentences, middle: vivid descriptions, older: rich vocabulary). Explicit instruction: "Show, don't tell. Never say 'stereotypes are bad.'" |
| **AI Output** | Complete 5-page story in JSON: title, page texts, illustration descriptions, discussion prompts, activity suggestion |
| **What I Kept** | Narrative structure, age-appropriate vocabulary, emotional arc |
| **What I Changed** | Added "Do NOT describe the child's race, skin color, hair type, or ethnicity" in illustration descriptions (handled by separate character diversity system); enforced strict JSON output; "Discovery, Not Biography" design principle |
| **Verification** | Manual reading of 10+ generated stories; automated QA verification loop (Tool 4); checked discussion prompts are open-ended; verified age-appropriate vocabulary per tier |

---

### Trace 2: Stereotype Classification

| Field | Content |
|-------|---------|
| **Category** | Analysis / Classification |
| **Tool** | Claude Sonnet 4.5 via OpenRouter |
| **MCP Tool** | `classify_stereotype` in `mcp_server/server.py` |
| **Input** | Free-text stereotype (e.g., "My daughter thinks only boys can be scientists") + list of 14 valid categories |
| **Prompt Design** | Simplified to return only `primary_category` + `secondary_categories` (0-2). Max tokens reduced to 256. Removed unused fields (stereotype_essence, age_strategy, emotional_tone) to cut latency and cost. |
| **AI Output** | JSON with category mapping |
| **What I Kept** | Category detection logic |
| **What I Changed** | Precomputed classifications for all 10 example buttons (skip API call entirely for most common demo path); fallback to `girls_cant_do_math` if primary_category missing; fixed 6 precomputed category keys that didn't match KB |
| **Verification** | Tested with all 14 categories; verified correct matching to KB women; tested edge cases (misspellings, unusual phrasings); confirmed all precomputed keys exist in KB |

---

### Trace 3: QA Verification

| Field | Content |
|-------|---------|
| **Category** | Quality Assurance / Ethical AI |
| **Tool** | Claude Sonnet 4.5 via OpenRouter |
| **MCP Tool** | `verify_story` in `mcp_server/server.py` |
| **Why This Exists** | EMNLP 2025 research showed AI-generated stories amplify stereotypes 55% more than human-written ones. This tool catches that. |
| **Input** | Full story text (all 5 pages) + original stereotype |
| **Prompt Design** | 6-point checklist: (1) inadvertent reinforcement, (2) new stereotypes introduced, (3) age-appropriate non-preachy language, (4) natural woman integration, (5) empowering ending, (6) character agency |
| **AI Output** | JSON: passed (bool), score (1-10), issues list, strengths list, suggestion |
| **What I Kept** | 6-point verification checklist, scoring rubric, issue categorization |
| **What I Changed** | Safe default (passed=true, score=7) on API failure to prevent blocking UX; max tokens reduced to 512; QA runs after "complete" event so users see story immediately |
| **Verification** | Compared QA scores with manual story review; tested with intentionally problematic stories; verified issues are actionable; confirmed score=9 on well-written test stories |

---

### Trace 4: Illustration Generation

| Field | Content |
|-------|---------|
| **Category** | Visual Content |
| **Tool** | DALL-E 3 via OpenAI API |
| **MCP Tool** | `generate_illustration` in `mcp_server/server.py` |
| **Input** | Scene description (from story's `illustration_description`) + character description (from Flask's `_generate_character_appearance()`) + page number |
| **Prompt Design** | "Warm, whimsical watercolor style with soft colors and gentle brushstrokes. Inclusive and diverse characters. Suitable for ages 3-10." Character description injected as "MAIN CHARACTER (must appear exactly like this):" to maintain consistency across 5 pages. Color palette: coral, gold, sage green, soft purple. |
| **AI Output** | 1024×1024 PNG image URL (standard quality) |
| **What I Kept** | Watercolor aesthetic, warm color palette, children's book style |
| **What I Changed** | Decoupled character appearance from story text — Claude writes scene descriptions without race/ethnicity, Flask generates diverse appearance separately and injects into DALL-E prompt; 10 appearance templates ensure representation |
| **Verification** | Visual inspection of 50+ illustrations; checked character consistency across pages; verified warm color palette; confirmed age-appropriateness |

---

### Trace 5: Test Generation

| Field | Content |
|-------|---------|
| **Category** | Development Tooling |
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | Complete test suites: conftest.py with fixtures, test_app.py (100+ tests), test_mcp_server.py (40+ tests), App.test.js (50+ tests) |
| **What I Changed** | Fixed mock data to include required `category` field; simplified SSE streaming tests (complex to mock in Jest); adjusted assertions for Flask's charset inclusion; fixed mock data structures |
| **Verification** | 151 backend tests passing; 24 frontend tests passing; all API routes covered; all MCP tools covered |

---

### Trace 6: Knowledge Base Curation

| Field | Content |
|-------|---------|
| **Category** | Research & Content |
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | Initial list of 50 women with categories, achievements, story_hooks, fairy_tale_moments, age_adaptations (young/middle/older), counters_stereotypes arrays |
| **What I Changed** | Verified every fact against Wikipedia/Britannica; rewrote fairy_tale_moment and age_adaptations for accuracy and age-appropriateness; fixed era dates (Malala "2997"→"1997", Simone Biles "2997"→"1997"); removed duplicate entries (Wangari Maathai, Malala Yousafzai); ensured all 50 women suggested by at least one category |
| **Verification** | Cross-referenced each achievement with 2+ historical sources; automated validation script checking all required fields, unique names, valid eras, category mappings |

---

### Trace 7: Frontend Development

| Field | Content |
|-------|---------|
| **Category** | UI/UX Development |
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | React components (4 screens), CSS styling (warm storybook aesthetic), sound system (Web Audio API), theme toggle (light/dark), typewriter text effect, touch/swipe navigation, page-turn animations |
| **What I Changed** | Reviewed all component logic; fixed keyboard navigation stale closure issue; adjusted typewriter speed (variable delay for punctuation); ensured all CSS classes referenced in JS exist in CSS; verified responsive breakpoints at 5 widths |
| **Verification** | Manual testing on desktop and mobile viewports; keyboard-only navigation test; dark mode visual review; SSE event handling verification |

---

### Trace 8: Backend Optimization

| Field | Content |
|-------|---------|
| **Category** | Performance Engineering |
| **Tool** | Goose AI Agent (Block) with Claude |
| **What AI Generated** | ThreadPoolExecutor parallelization for illustrations + QA; precomputed classification cache; input validation; character diversity system; SSE streaming pipeline |
| **What I Changed** | Fixed 6 of 10 precomputed category keys that didn't match KB (e.g., `"boys_are_better_at_sports"` → `"girls_arent_strong"`, `"technology_is_for_boys"` → `"girls_cant_do_tech"`, `"mom_gives_up_dreams"` → `"moms_cant_be_leaders"`); removed dead code (`_extract_completed_pages`); aligned story generation model to Opus 4.6 |
| **Verification** | End-to-end pipeline test; precomputed categories validated against KB; confirmed all 10 example buttons produce targeted (not random) woman matches |

---

## Usage Zones Compliance

### Green Zone (Allowed)
- ✅ Brainstorming story structures and narrative arcs
- ✅ Drafting test scaffolds and fixtures
- ✅ Self-red-teaming (QA verification loop)
- ✅ CSS styling and visual design iteration

### Yellow Zone (Requires Documentation — documented above)
- ⚠️ Story generation → Documented with QA verification (Trace 1)
- ⚠️ Historical facts → Verified against external sources (Trace 6)
- ⚠️ Code generation → Reviewed, tested, and fixed (Traces 5, 7, 8)

### Red Zone (Avoided)
- ❌ Fabricated statistics — All stats cited with academic sources
- ❌ Hidden automation — All AI usage documented in this log
- ❌ Privacy violations — No user data collected or stored
- ❌ Unverified historical claims — Every fact cross-referenced

---

## Augment, Not Abdicate

This project demonstrates responsible AI usage:

1. **Human oversight**: Every AI output reviewed before use
2. **Verification loops**: QA system catches AI mistakes in real-time
3. **Source attribution**: All facts traceable to evidence (see Evidence Log)
4. **Transparent documentation**: Full AI usage logged here — nothing hidden
5. **Human judgment**: All architectural decisions, design principles, and editorial choices made by human
6. **Bug-catching**: Human caught and fixed errors AI introduced (wrong category keys, duplicate KB entries, model mismatches)

---

*AI Trace Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
