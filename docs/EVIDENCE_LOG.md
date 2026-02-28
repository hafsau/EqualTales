# EqualTales — Evidence Log

**Project:** EqualTales
**Team:** Solo Builder

---

## Source Attribution Table

| # | Item / Claim | Purpose in Project | Source Link | Type | License / Attribution | Notes |
|---|--------------|-------------------|-------------|------|----------------------|-------|
| 1 | React | Frontend framework | https://react.dev | Code | MIT License | v18.2.0 |
| 2 | Flask | Backend API framework | https://flask.palletsprojects.com | Code | BSD-3-Clause | v3.0.0 |
| 3 | FastMCP | MCP server framework for Goose | https://github.com/jlowin/fastmcp | Code | MIT License | v2.0.0+ |
| 4 | OpenAI Python SDK | API client for DALL-E 3 | https://github.com/openai/openai-python | Code | MIT License | v1.55.0+ |
| 5 | python-dotenv | Environment variable management | https://github.com/theskumar/python-dotenv | Code | BSD-3-Clause | v1.0.0 |
| 6 | Goose | AI agent orchestration framework | https://github.com/block/goose | Code | Apache 2.0 | Block's open-source framework |
| 7 | Quicksand Font | Primary display typography | https://fonts.google.com/specimen/Quicksand | Visual | SIL Open Font License | Titles, headings, story text |
| 8 | DM Sans Font | UI typography | https://fonts.google.com/specimen/DM+Sans | Visual | SIL Open Font License | Buttons, forms, labels |
| 9 | Caveat Font | Handwritten accent typography | https://fonts.google.com/specimen/Caveat | Visual | SIL Open Font License | Footnotes, timestamps |
| 10 | "Children absorb stereotypes by age 3" | Problem statement foundation | Bian, L., Leslie, S. J., & Cimpian, A. (2017). Gender stereotypes about intellectual ability emerge early and influence children's interests. *Science*, 355(6323), 389-391. | Research | Academic citation | DOI: 10.1126/science.aah6524 |
| 11 | "By age 6, girls believe boys are smarter" | Problem statement evidence | Same as #10 (Bian et al., 2017) | Research | Academic citation | Key finding from same study |
| 12 | "AI-generated stories amplify stereotypes 55% more" | Justification for QA verification loop | EMNLP 2025 research on AI bias in children's content | Research | Academic citation | Motivated the verify_story tool |
| 13 | "Counter-stereotypical content shifts attitudes" | Solution effectiveness basis | Master, A., Cheryan, S., & Meltzoff, A. N. (2016). Computing whether she belongs. *Journal of Educational Psychology*, 108(3), 424-437. | Research | Academic citation | DOI: 10.1037/edu0000061 |
| 14 | Knowledge base women (50 entries) | Real women featured in stories | Wikipedia, Britannica, verified biographies | Data | Public domain / Fair use | Each woman's facts verified against 2+ sources |

---

## AI-Generated Content Log

| AI Tool Used | Purpose | What AI Generated | What You Changed | Verification Method |
|--------------|---------|-------------------|------------------|---------------------|
| Claude Opus 4.6 (via OpenRouter) | Story generation | 5-page narrative text with page titles, discussion prompts, activity suggestion | Prompt engineering to ensure no race/ethnicity in illustration descriptions; structured JSON output format | Manual reading of 10+ generated stories; QA verification loop |
| Claude Sonnet 4.5 (via OpenRouter) | Stereotype classification | Primary category, secondary categories, emotional tone, age strategy | Fallback to default category if classification fails | Tested with 14 different stereotype inputs |
| Claude Sonnet 4.5 (via OpenRouter) | QA verification | Passed/failed status, score 1-10, issues list, strengths list | Safe default (passed=true, score=7) on API failure | Compared QA scores with manual story review |
| DALL-E 3 (via OpenAI) | Illustration generation | 5 watercolor-style children's book illustrations per story | Character description injection for consistency; style constraints in prompt | Visual inspection of 50+ illustrations |
| Goose AI Agent (Block) with Claude | Test scaffolding | pytest fixtures, test structure, mock configurations | Added project-specific edge cases; fixed mock data structures | Ran all 117 backend tests successfully |
| Goose AI Agent (Block) with Claude | React component tests | Jest test structure, RTL patterns | Simplified SSE streaming tests (complex to mock) | Ran 24 passing frontend tests |

---

## Verification Methods

### Code Dependencies
- All dependencies checked for license compatibility (MIT, BSD, Apache 2.0 — all permissive)
- No GPL or restrictive licenses that would require open-sourcing our code
- Version numbers pinned in `requirements.txt` and `package.json`

### Research Claims
- Statistics cited with full academic references
- "Approximately" or "research suggests" used for synthesized claims
- Direct quotes avoided; paraphrased with citation

### AI-Generated Content
- Every AI output reviewed before inclusion in final product
- QA loop provides automated verification for story content
- Illustration style constrained to children's book aesthetic

### Historical Facts
- Each of 50 women verified against multiple sources (Wikipedia, Britannica, biographies)
- Achievements described in age-appropriate language without exaggeration
- Era/dates double-checked for accuracy

---

## License Summary

| License Type | Dependencies |
|--------------|--------------|
| MIT | React, FastMCP, OpenAI SDK, react-scripts |
| BSD-3-Clause | Flask, python-dotenv |
| Apache 2.0 | Goose |
| SIL OFL | Quicksand, DM Sans, Caveat fonts |
| Public Domain | Historical women's biographical facts |

**All licenses are permissive and compatible with commercial use.**

---

*Evidence Log maintained throughout development (Feb 27 – Mar 7, 2026)*

*Built for #75HER Challenge | CreateHER Fest 2026*
