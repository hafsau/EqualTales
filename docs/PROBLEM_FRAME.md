# EqualTales — 4-Line Problem Frame

**Project:** EqualTales
**Track:** AI/ML
**Challenge:** CreateHER Fest #75HER Challenge Hackathon 2026
**SDGs:** Gender Equality (5), Quality Education (4), Decent Work (8), Industry Innovation (9), Reduced Inequalities (10)

---

## The 4 Lines

### Line 1: User
**Mothers of children ages 3–10** who want to counter gender stereotypes their children are absorbing from peers, media, and society.

### Line 2: Problem
Children internalize gender stereotypes by **age 3** (Bian et al., 2017, *Science*), and by **age 6**, girls start believing boys are inherently "smarter." Research shows AI-generated children's content amplifies stereotypes **55% more** than human-written content (EMNLP 2025). Existing counter-stereotype content is either:
- **Generic** ("girls can do anything!") — too vague to address specific beliefs
- **Biographical** (stories about famous women) — disconnected from the child's personal experience

Neither approach effectively shifts deeply held beliefs because they don't address the *specific* stereotype the child has expressed.

### Line 3: Constraints
- **Technical:** Must use Goose (Block's open-source AI agent framework) with Claude as AI backbone
- **Timeline:** Solo builder, 8-day build (Feb 27 – Mar 7, 2026)
- **Content:** Stories must be age-appropriate (3-10), engaging, and illustrated
- **Narrative Design:** Real historical women must be woven naturally into narrative — "Discovery, Not Biography" principle
- **Quality:** Generated content must pass AI-powered stereotype reinforcement detection (score 7+/10)
- **Budget:** Sponsored OpenRouter credits for Claude + DALL-E 3 costs (~$0.20-0.40/story)
- **Privacy:** No user accounts, no data persistence, no login required

### Line 4: Success Test
A mother inputs a stereotype her child expressed (e.g., "my daughter thinks math is for boys"), selects child's age and name, and receives a **complete 5-page illustrated story** featuring a fictional child (named after her real child) who discovers a real woman who defied that stereotype — **generated in under 90 seconds**, with **verified anti-stereotype content** (QA score 7+/10).

**Observable in 5-minute demo:**
1. Judge opens https://equaltales.vercel.app (no login required)
2. Clicks "Try It Now"
3. Selects example stereotype or types custom input
4. Enters child name and age (3-10)
5. Watches 5-step progress (classify → match woman → write story → QA → illustrate)
6. Reads complete 5-page illustrated storybook with page-turn navigation
7. Views companion section: real woman bio, discussion prompts, activity suggestion
8. Sees QA verification badge confirming story passed stereotype detection

---

## How It Works (Technical)

```
Mother's Input → Goose MCP Server (5 tools) → Personalized Storybook

Tool 1: classify_stereotype    → Claude Sonnet 4.5  → Category mapping
Tool 2: match_real_woman       → Local KB (50 women) → Best-fit woman
Tool 3: generate_story         → Claude Opus 4.6     → 5-page narrative
Tool 4: verify_story           → Claude Sonnet 4.5   → Stereotype QA
Tool 5: generate_illustration  → DALL-E 3            → 5 watercolor images
```

The entire story engine is a **Goose-compatible MCP extension** — 5 tools exposed via FastMCP with stdio transport and JSON-RPC 2.0 protocol. Flask backend orchestrates the pipeline and streams progress to the React frontend via SSE.

---

## AI Pressure-Test

| Field | Content |
|-------|---------|
| **LLM Used** | Claude (via Goose AI Agent) |
| **Prompt Summary** | "Review this problem frame for clarity, specificity, and completeness" |
| **AI Output** | Suggested adding specific age range, quantifying success metrics, clarifying constraint priorities |
| **What I Kept** | Age range specification (3-10), generation time target (<90 seconds), QA score threshold (7+/10) |
| **What I Changed** | Removed jargon ("counter-stereotypical exposure"), added concrete demo flow steps, added SDG alignment |

---

*Built for #75HER Challenge | CreateHER Fest 2026*
