# EqualTales — 4-Line Problem Frame

**Project:** EqualTales
**Track:** AI/ML
**Challenge:** CreateHER Fest #75HER Challenge Hackathon 2026

---

## The 4 Lines

### Line 1: User
**Mothers of children ages 3–10** who want to counter gender stereotypes their children are absorbing from peers, media, and society.

### Line 2: Problem
Children internalize gender stereotypes by **age 3**, and by **age 6**, girls start believing boys are inherently "smarter." Existing counter-stereotype content is either:
- **Generic** ("girls can do anything!") — too vague to address specific beliefs
- **Biographical** (stories about famous women) — disconnected from the child's personal experience

Neither approach effectively shifts deeply held beliefs because they don't address the *specific* stereotype the child has expressed.

### Line 3: Constraints
- **Technical:** Must use Goose (Block's open-source AI agent framework) with Claude
- **Timeline:** Solo builder, 8-day build (Feb 27 – Mar 7, 2026)
- **Content:** Stories must be age-appropriate (3-10), engaging, and illustrated
- **Integration:** Real historical women must be woven naturally into narrative (not forced biography)
- **Quality:** Generated content must pass AI-powered stereotype reinforcement detection
- **Budget:** $80 sponsored OpenRouter credits + DALL-E 3 costs (~$0.20-0.40/story)

### Line 4: Success Test
A mother inputs a stereotype her child expressed (e.g., "my daughter thinks math is for boys"), selects child's age and name, and receives a **complete 5-page illustrated story** featuring a fictional child who discovers a real woman who defied that stereotype — **generated in under 90 seconds**, with **verified anti-stereotype content** (QA score 7+/10).

**Observable in 5-minute demo:**
1. Judge clicks "Try It Now" (no login required)
2. Selects example stereotype or types custom input
3. Enters child name and age
4. Watches story generate with progress indicators
5. Reads complete illustrated storybook with page turns
6. Sees QA verification badge confirming story passed stereotype check

---

## AI Pressure-Test

| Field | Content |
|-------|---------|
| **LLM Used** | Claude Sonnet 4.5 (via Claude Code) |
| **Prompt Summary** | "Review this problem frame for clarity, specificity, and completeness" |
| **AI Output** | Suggested adding specific age range, quantifying success metrics, clarifying constraint priorities |
| **What I Kept** | Age range specification (3-10), generation time target (<90 seconds), QA score threshold (7+/10) |
| **What I Changed** | Removed jargon ("counter-stereotypical exposure"), added concrete demo flow steps |

---

*Built for #75HER Challenge | CreateHER Fest 2026*
