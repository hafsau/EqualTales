# EqualTales — AI Trace Log

**Project:** EqualTales
**Team:** Solo Builder
**Principle:** Augment, Not Abdicate

---

## AI Usage Traces

### Trace 1: Story Generation

| Field | Content |
|-------|---------|
| **Category** | Content Generation |
| **Tool** | Claude Opus 4.6 via OpenRouter |
| **Prompt** | "You are a children's story writer creating an anti-stereotype story. Write a 5-page illustrated children's story. [Includes: stereotype to counter, child's name/age, real woman to feature, narrative arc structure, writing rules for age group, JSON output format]" |
| **AI Response** | Complete 5-page story with title, page texts, illustration descriptions, discussion prompts, and activity suggestion in structured JSON |
| **What I Kept** | Narrative structure, age-appropriate vocabulary, emotional arc from belief to new understanding |
| **What I Changed** | Added explicit instruction NOT to describe child's race/ethnicity in illustration descriptions (handled separately by character diversity system); enforced JSON output format for reliable parsing |
| **Verification** | Manual reading of 10+ generated stories for quality; automated QA verification loop for stereotype reinforcement; checked that discussion prompts are open-ended questions |

---

### Trace 2: Stereotype Classification

| Field | Content |
|-------|---------|
| **Category** | Analysis / Classification |
| **Tool** | Claude Sonnet 4.5 via OpenRouter |
| **Prompt** | "Analyze this stereotype that a child has expressed or a parent wants to counter: [stereotype_text]. Available categories: [14 categories]. Return JSON with primary_category, secondary_categories, stereotype_essence, age_strategy, emotional_tone." |
| **AI Response** | JSON classification with category mapping and age-appropriate counter-narrative strategy |
| **What I Kept** | Category detection logic, emotional tone analysis, age-group-specific strategies |
| **What I Changed** | Added fallback to `girls_cant_do_math` if primary_category missing (edge case handling); limited secondary_categories to 1-2 max |
| **Verification** | Tested with all 14 stereotype categories; verified correct matching to knowledge base women; checked edge cases (misspellings, unusual phrasings) |

---

### Trace 3: QA Verification

| Field | Content |
|-------|---------|
| **Category** | Quality Assurance |
| **Tool** | Claude Sonnet 4.5 via OpenRouter |
| **Prompt** | "You are a stereotype detection system for children's content. Analyze this story that was generated to counter the stereotype: [stereotype_text]. Check for: stereotype reinforcement, new stereotypes introduced, age-appropriate language, natural integration of real woman, empowering ending, character agency." |
| **AI Response** | JSON with passed (bool), score (1-10), issues list, strengths list, improvement suggestion |
| **What I Kept** | 6-point verification checklist, scoring rubric, issue categorization |
| **What I Changed** | Added safe default (passed=true, score=7) on API failure to prevent blocking user experience; threshold set at score >= 7 for passing |
| **Verification** | Compared QA scores with manual story review; tested with intentionally problematic stories to confirm detection; verified issue descriptions are actionable |

---

### Trace 4: Illustration Generation

| Field | Content |
|-------|---------|
| **Category** | Visual Content |
| **Tool** | DALL-E 3 via OpenAI API |
| **Prompt** | "Create a children's book illustration in a warm, whimsical watercolor style with soft colors and gentle brushstrokes. Style: Warm watercolor, soft pastels, hand-drawn feel, inclusive and diverse characters. MAIN CHARACTER: [detailed appearance description]. Scene (Page X of 5): [scene_description]" |
| **AI Response** | 1024x1024 PNG image URL with DALL-E's revised prompt |
| **What I Kept** | Watercolor aesthetic, warm color palette, children's book style |
| **What I Changed** | Added explicit character description injection for consistency across 5 pages; specified coral/gold/sage/purple color palette to match UI; added "suitable for ages 3-10" constraint |
| **Verification** | Visual inspection of 50+ illustrations for age-appropriateness; checked character consistency across pages; verified warm color palette adherence |

---

### Trace 5: Test Generation

| Field | Content |
|-------|---------|
| **Category** | Development Tooling |
| **Tool** | Goose AI Agent (Block) with Claude |
| **Prompt** | "Implement strict TDD for this project. Create pytest tests for backend and Jest tests for frontend covering all routes, validation, edge cases." |
| **AI Response** | Complete test suite: conftest.py with fixtures, test_app.py (60+ tests), test_mcp_server.py (40+ tests), App.test.js (50+ tests) |
| **What I Kept** | Test structure, mock patterns, edge case coverage (Unicode, special characters, missing fields) |
| **What I Changed** | Fixed mock data to include required `category` field; simplified SSE streaming tests (complex to mock in Jest); adjusted assertions for Flask's charset inclusion |
| **Verification** | Ran full test suite: 117 backend tests passing, 24 frontend tests passing; verified coverage of all API routes and MCP tools |

---

### Trace 6: QA Agent Script

| Field | Content |
|-------|---------|
| **Category** | Development Tooling |
| **Tool** | Goose AI Agent (Block) with Claude |
| **Prompt** | "Create a QA agent script for continuous monitoring of development processes" |
| **AI Response** | `scripts/qa_agent.py` — comprehensive Python script with checks for file structure, dependencies, knowledge base validation, Python syntax, tests, and API health |
| **What I Kept** | Check categories, severity levels, watch mode functionality, JSON output option |
| **What I Changed** | Added knowledge base structure validation; customized coverage thresholds (70%); added fix mode for dependency installation |
| **Verification** | Ran `python scripts/qa_agent.py --quick` to verify all checks pass; tested watch mode file change detection |

---

### Trace 7: Knowledge Base Curation

| Field | Content |
|-------|---------|
| **Category** | Research & Content |
| **Tool** | Goose AI Agent (Block) with Claude |
| **Prompt** | "Help me create a knowledge base of 50 real women who broke gender stereotypes, organized by category (STEM, sports, leadership, etc.) with age-appropriate story hooks" |
| **AI Response** | Initial list of women with categories, achievements, and story angles |
| **What I Kept** | Category organization, diverse representation across eras/backgrounds |
| **What I Changed** | Verified every fact against Wikipedia/Britannica; rewrote fairy_tale_moment fields for age-appropriateness; added age_adaptations (young/middle/older) for each woman |
| **Verification** | Cross-referenced each woman's achievement with 2+ historical sources; tested that every category has suggested_women; verified 50 unique entries |

---

## Usage Zones Compliance

### Green Zone (Allowed)
- Brainstorming story structures ✓
- Drafting test scaffolds ✓
- Self-red-teaming (QA loop) ✓

### Yellow Zone (Requires Documentation)
- Story generation → Documented with QA verification
- Historical facts → Verified against external sources
- Code suggestions → Reviewed and tested

### Red Zone (Avoided)
- Fabricated statistics ✗ — All stats cited with sources
- Hidden automation ✗ — All AI usage documented here
- Privacy violations ✗ — No user data collected

---

## Augment, Not Abdicate

This project demonstrates responsible AI usage:

1. **Human oversight**: Every AI output reviewed before use
2. **Verification loops**: QA system catches AI mistakes
3. **Source attribution**: All facts traceable to evidence
4. **Transparent documentation**: Full AI usage logged here
5. **Human judgment**: Architectural decisions made by human, not AI

---

*AI Trace Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
