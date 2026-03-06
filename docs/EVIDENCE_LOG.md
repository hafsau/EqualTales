# EqualTales — Evidence Log

**Project:** EqualTales
**Team:** Solo Builder
**Timeline:** Feb 27 – Mar 7, 2026

---

## Research Sources

| # | Claim | Source | Type | How Used |
|---|-------|--------|------|----------|
| 1 | "Children absorb stereotypes by age 3" | Bian, L., Leslie, S. J., & Cimpian, A. (2017). Gender stereotypes about intellectual ability emerge early and influence children's interests. *Science*, 355(6323), 389-391. DOI: 10.1126/science.aah6524 | Academic | Landing page stat; problem frame justification |
| 2 | "By age 6, girls believe boys are smarter" | Same study (Bian et al., 2017) | Academic | Landing page stat; urgency framing |
| 3 | "Counter-stereotypical content shifts attitudes" | Master, A., Cheryan, S., & Meltzoff, A. N. (2016). Computing whether she belongs. *Journal of Educational Psychology*, 108(3), 424-437. DOI: 10.1037/edu0000061 | Academic | Solution effectiveness basis; why personalized stories work |
| 4 | "AI-generated stories amplify stereotypes 55% more" | EMNLP 2025 research on AI bias in children's content | Academic | Justification for `verify_story` QA tool; cited in tool docstring |

---

## Code Dependencies

| # | Package | Version | License | Link | Purpose |
|---|---------|---------|---------|------|---------|
| 5 | React | 18.2.0 | MIT | https://react.dev | Frontend UI framework |
| 6 | Flask | 3.0.0 | BSD-3-Clause | https://flask.palletsprojects.com | Backend API server |
| 7 | FastMCP | 2.0.0+ | MIT | https://github.com/jlowin/fastmcp | MCP server framework for Goose integration |
| 8 | OpenAI Python SDK | 1.55.0+ | MIT | https://github.com/openai/openai-python | Client for DALL-E 3 + OpenRouter (Claude) |
| 9 | python-dotenv | 1.0.0 | BSD-3-Clause | https://github.com/theskumar/python-dotenv | Environment variable management |
| 10 | Goose | Latest | Apache 2.0 | https://github.com/block/goose | AI agent orchestration framework (Block) |
| 11 | flask-cors | 4.0.0 | MIT | https://github.com/corydolphin/flask-cors | Cross-origin request handling |
| 12 | gunicorn | 21.2.0 | MIT | https://gunicorn.org | Production WSGI server (Render deployment) |

---

## Visual Assets

| # | Asset | License | Link | Usage |
|---|-------|---------|------|-------|
| 13 | Quicksand Font | SIL Open Font License | https://fonts.google.com/specimen/Quicksand | Titles, headings, story text |
| 14 | DM Sans Font | SIL Open Font License | https://fonts.google.com/specimen/DM+Sans | UI elements: buttons, forms, labels |
| 15 | Caveat Font | SIL Open Font License | https://fonts.google.com/specimen/Caveat | Handwritten accents: footnotes, timestamps, page labels |

---

## Data Sources

| # | Item | Source | License | Verification |
|---|------|--------|---------|-------------|
| 16 | Knowledge base (50 women) | Wikipedia, Britannica, verified biographies | Public domain / Fair use | Each woman's facts verified against 2+ independent sources |
| 17 | Stereotype categories (14) | Academic literature on gender stereotypes + editorial curation | Original taxonomy | Categories mapped to research on common childhood gender beliefs |
| 18 | Age adaptations (3 tiers per woman) | Original writing informed by developmental psychology | Original content | young (3-5), middle (6-8), older (9-10) reading levels |

---

## AI-Generated Content Log

| AI Tool | Purpose | What AI Generated | What I Changed | Verification |
|---------|---------|-------------------|----------------|-------------|
| Claude Opus 4.6 (OpenRouter) | Story generation | 5-page narrative with titles, discussion prompts, activity suggestion | Added instruction NOT to describe child's race (handled by diversity system); enforced JSON output format; "Discovery, Not Biography" design principle in prompt | Manual review of 10+ stories; automated QA loop; age-appropriateness check |
| Claude Sonnet 4.5 (OpenRouter) | Stereotype classification | Primary category + secondary categories from 14-category taxonomy | Simplified prompt from 5 fields to 2 (removed unused fields); precomputed 10 example classifications to skip API entirely | Tested all 14 categories; verified correct KB matching |
| Claude Sonnet 4.5 (OpenRouter) | QA verification | Passed/failed, score 1-10, issues, strengths, suggestion | Added safe default (passed=true, score=7) on API failure; 6-point checklist | Compared QA scores with manual review; tested with intentionally problematic stories |
| DALL-E 3 (OpenAI) | Illustration generation | 1024×1024 watercolor children's book illustrations | Character description injection for consistency; coral/gold/sage palette; "suitable for ages 3-10" constraint | Visual inspection of 50+ illustrations |
| Goose AI Agent (Block) with Claude | Test scaffolding | pytest fixtures, test structure, mock configurations | Fixed mock data structures; simplified SSE streaming tests | 151 backend tests, 24 frontend tests passing |
| Goose AI Agent (Block) with Claude | Knowledge base curation | Initial list of 50 women with categories and story angles | Verified every fact against Wikipedia/Britannica; rewrote age_adaptations; fixed era dates (Malala, Simone Biles had typos) | Cross-referenced each achievement with 2+ sources |
| Goose AI Agent (Block) with Claude | Frontend development | React components, CSS styling, sound system, theme toggle | Reviewed all generated code; fixed keyboard navigation closure bug; adjusted typewriter timing | Manual testing of all 4 screens on multiple viewports |
| Goose AI Agent (Block) with Claude | Backend optimization | Parallel illustration generation, precomputed classifications, input validation | Fixed precomputed category keys (6 of 10 had wrong keys); verified all map to KB | End-to-end pipeline testing |

---

## Verification Methods

### Code Dependencies
- All dependencies checked for license compatibility (MIT, BSD, Apache 2.0 — all permissive)
- No GPL or restrictive licenses
- Version numbers pinned in `requirements.txt` and `package.json`

### Research Claims
- All statistics cited with full academic references and DOIs where available
- Claims paraphrased with citation, not direct quotes
- "Approximately" used for synthesized claims

### AI-Generated Content
- Every AI output reviewed before inclusion
- QA tool provides automated verification for story content
- Illustration style constrained to children's book aesthetic
- Knowledge base facts verified against external sources

### Historical Facts (Knowledge Base)
- Each of 50 women verified against multiple sources (Wikipedia, Britannica, published biographies)
- Achievements described in age-appropriate language without exaggeration
- Era/dates double-checked — caught and fixed typos (Malala "2997" → "1997", Simone Biles "2997" → "1997")
- Duplicate entries detected and removed (Wangari Maathai, Malala Yousafzai were duplicated in initial version)

---

## License Summary

| License Type | Dependencies |
|--------------|--------------|
| MIT | React, FastMCP, OpenAI SDK, flask-cors, gunicorn, react-scripts |
| BSD-3-Clause | Flask, python-dotenv |
| Apache 2.0 | Goose |
| SIL OFL | Quicksand, DM Sans, Caveat fonts |
| Public Domain | Historical women's biographical facts |

**All licenses are permissive and compatible with commercial use.**

---

*Evidence Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
