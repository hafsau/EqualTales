# EqualTales — CreateHER Fest #75HER Challenge Hackathon 2026

## One-Liner
An AI-powered children's story engine that generates personalized, illustrated anti-stereotype stories for mothers — featuring real-life women who broke barriers.

**Track:** AI/ML | **Builder:** Solo | **Demo Day:** March 8, 2026

---

## The Core Insight

Children absorb gender stereotypes by age 3. By age 6, girls start believing boys are "smarter." Research shows that exposure to counter-stereotypical content — stories where girls build rockets, lead expeditions, solve equations — measurably shifts these attitudes. But parents who want to counter stereotypes face a problem: the content that exists is either generic ("girls can do anything!") or biographical (great women's stories that kids can't personally connect to).

EqualTales bridges this gap. A mother types the specific stereotype she wants to counter — "my daughter thinks math is for boys" — and the AI generates a personalized 5-page illustrated story where a fictional child *like her daughter* discovers a real woman who proves the stereotype wrong. The story doesn't lecture. It shows.

---

## Ideathon Submission

### 1. Project Title + Track
**EqualTales** — AI/ML Track

### 2. 4-Line Problem Frame

> **User:** Mothers of children ages 3–10 who want to counter gender stereotypes their children are absorbing.
>
> **Problem:** Children internalize gender stereotypes by age 3, and by age 6, girls believe boys are inherently smarter. Existing counter-stereotype content is either generic ("girls can do anything") or biographical (disconnected from the child's personal experience) — neither effectively shifts deeply held beliefs.
>
> **Constraints:**
> - Must use Goose (Block's open-source AI agent framework) with Claude Opus 4.5
> - Stories must be age-appropriate, engaging, and illustrated
> - Must integrate real historical women naturally (not as forced biography)
> - Solo builder, 8-day build timeline
> - Generated content must pass anti-stereotype QA verification
>
> **Success Test:** A mother inputs a stereotype her child expressed, selects child's age and name, and receives a complete 5-page illustrated story featuring a fictional child who discovers a real woman who defied that stereotype — generated in under 2 minutes, with verified anti-stereotype content.

### 3. Solution Summary

**EqualTales** is an AI-powered web application that generates personalized, illustrated children's stories designed to counter specific gender stereotypes. Unlike existing products like Rebel Girls (pre-written biographies) or generic affirmation books ("you can be anything!"), EqualTales creates *targeted* stories that address the exact stereotype a child has expressed.

**How it works:**

A mother provides three inputs: (1) the stereotype to counter (e.g., "my daughter thinks only boys can be scientists"), (2) the child's age, and (3) the child's name. EqualTales' AI engine — powered by Goose with Claude Opus 4.5 — then executes a multi-step pipeline:

First, it classifies the stereotype by category and selects an age-appropriate counter-narrative strategy. Then it generates a 5-page story following a proven narrative arc: The Belief → The Question → The Discovery → The Inspiration → The New Belief. The fictional protagonist shares the child's name and encounters a real historical woman (drawn from a curated knowledge base of 50+ barrier-breaking women) who provides living proof that the stereotype is false. Each page gets a custom illustration generated via DALL-E 3 with consistent character design. Finally, the complete story passes through a stereotype detection QA loop to verify it doesn't inadvertently reinforce the very biases it aims to counter.

The result is a personalized, illustrated storybook experience that a mother can read with her child — addressing the specific belief that prompted the story, grounded in real history, and verified by AI quality assurance.

EqualTales advances **SDG 4** (quality education through evidence-based content), **SDG 5** (gender equality by countering stereotypes at their root — childhood), **SDG 9** (AI innovation for social impact), and **SDG 10** (reducing inequality by making counter-stereotype content accessible and personalized).

### 4. Technical Blueprint

| Component | Technology |
|-----------|-----------|
| AI Agent | Goose + Claude Opus 4.5 ($80 sponsored credits) |
| Backend | Python / Flask |
| Frontend | React |
| Illustrations | DALL-E 3 API |
| Stereotype Classification | Claude-based classifier |
| QA Verification | Claude-based stereotype detection loop |
| Hosting | Vercel (frontend) + Render (backend) |
| Version Control | GitHub (public repository) |

**Key Technical Differentiators:**
- **Goose as orchestration agent**: Manages the multi-step story generation pipeline autonomously
- **Stereotype classification engine**: Categorizes input stereotypes and selects counter-narrative strategies based on developmental psychology research
- **Character consistency system**: Hyper-detailed character descriptions maintained across all 5 DALL-E 3 illustration prompts
- **Real-life woman matching**: Knowledge base of 50+ women mapped to stereotype categories for contextual story integration
- **QA verification loop**: Generated stories are re-analyzed by Claude to detect any inadvertent stereotype reinforcement (research shows AI-generated stories amplify stereotypes 55% more than human-written ones)

**Technical Risks:**
- **Character inconsistency across illustrations**: Mitigated by detailed character description templates included in every DALL-E prompt
- **Story quality variance**: Mitigated by structured narrative arc template and QA verification loop
- **Generation time (~90 seconds)**: Mitigated by SSE streaming (text appears progressively) and parallel illustration generation
- **DALL-E 3 cost**: ~$0.04-0.08/image × 5 = $0.20-0.40/story, well within budget

### 5. Team Roles (Solo Builder)

| Role | Responsibility |
|------|---------------|
| Full-Stack Developer | Flask backend, React frontend, API integration, deployment |
| AI/ML Engineer | Goose pipeline, prompt engineering, stereotype classification, QA loop |
| Content Designer | Women knowledge base curation, narrative arc design, age-appropriate language |
| UX Designer | Storybook UI, page-turn experience, demo flow |

---

## Build Plan (Feb 27 – Mar 7, 2026)

### Day 1-2 (Feb 27-28): Foundation
- Set up Goose + Claude Opus 4.5 with sponsored credits
- Scaffold Flask backend + React frontend
- Build core story generation endpoint (stereotype input → 5-page story text)
- Build the women knowledge base (50 entries with structured data)
- Test end-to-end text generation pipeline

### Day 3-4 (Mar 1-2): Illustrations + Frontend
- Integrate DALL-E 3 API for illustration generation
- Build character consistency prompt system
- Build React storybook UI (5-page layout with page turns)
- Implement SSE streaming for progressive text display
- Implement parallel image generation + progressive image loading

### Day 5-6 (Mar 3-4): QA + Intelligence
- Build stereotype classification engine
- Build QA verification loop (detect stereotype reinforcement in generated content)
- Build real-life woman matching system
- Build companion materials (discussion prompts, activities)
- Polish UI and demo flow

### Day 7 (Mar 5): Integration + Testing
- End-to-end testing with diverse stereotype inputs
- Performance optimization (generation time, image loading)
- Bug fixes and edge case handling
- Deploy to hosting

### Day 8 (Mar 6-7): Documentation + Submission
- Record demo video
- Write README and documentation
- Complete Devpost submission
- Final testing and backup preparation

---

## 5-Page Story Structure

| Page | Title | Purpose |
|------|-------|---------|
| 1 | **The Belief** | Fictional child (named after user's child) encounters or expresses the stereotype |
| 2 | **The Question** | Something cracks the stereotype — curiosity emerges |
| 3 | **The Discovery** | Child discovers a REAL woman who defied the stereotype |
| 4 | **The Inspiration** | Real woman's specific achievement told in fairy-tale language |
| 5 | **The New Belief** | Child takes action, stereotype replaced by new understanding |

**Design Principle — "Discovery, Not Biography":**
The fictional child is the protagonist who carries the emotional journey. The real woman appears as a discovery — proof that breaks the stereotype. This means the child reader identifies with the protagonist (who shares their name) and encounters the real woman as someone inspiring, not as the subject of a history lesson.

---

## Real-Life Women Knowledge Base (Categories)

| Category | Women |
|----------|-------|
| STEM/Engineering | Emily Warren Roebling, Mae Jemison, Hedy Lamarr, Katherine Johnson, Ada Lovelace |
| Physical Strength/Sports | Serena Williams, Junko Tabei, Nadia Comăneci, Wilma Rudolph |
| Leadership/Activism | Malala Yousafzai, Wangari Maathai, Jacinda Ardern, Rosa Parks |
| Creativity/Art | Frida Kahlo, Maya Angelou, Zaha Hadid, Augusta Savage |
| Adventure/Exploration | Amelia Earhart, Valentina Tereshkova, Sylvia Earle, Bessie Coleman |
| Emotions/Mental Toughness | Simone Biles, Temple Grandin, Helen Keller |
| Business/Finance | Madam C.J. Walker, Oprah Winfrey, Sara Blakely |

Each entry includes: name, era, one-sentence achievement, age-appropriate story hook, stereotype categories she counters, and a fairy-tale-friendly description of her key moment.

---

## Judging Criteria Alignment

| Criterion (Weight) | How EqualTales Scores |
|--------------------|-----------------------|
| **Clarity (25%)** | One-sentence pitch. Clear problem frame (stereotypes by age 3). Observable success test (input stereotype → get illustrated story). |
| **Proof (25%)** | Live demo from clean start. No login. Judge types a stereotype, gets a complete illustrated story in ~90 seconds. Evidence grounded in developmental psychology research. |
| **Usability (20%)** | Three inputs only (stereotype, age, name). Storybook UI is intuitive. Mobile-friendly. Inclusive — any mother can use it. |
| **Rigor (20%)** | QA verification loop catches stereotype reinforcement. Age-appropriate language. Ethical considerations documented. Real research citations. |
| **Polish (10%)** | Illustrated storybook experience. Clean UI. Tidy repo. Complete documentation. |

---

## SDG Alignment

| UN SDG | How EqualTales Advances It |
|--------|---------------------------|
| **SDG 4: Quality Education** | Creates evidence-based educational content using developmental psychology research; makes counter-stereotype education accessible and personalized |
| **SDG 5: Gender Equality** | Addresses gender inequality at its root — childhood belief formation; empowers mothers with tools to counter stereotypes their children absorb |
| **SDG 9: Industry Innovation** | Uses AI (Goose + Claude + DALL-E 3) as a force for social good; demonstrates that AI can create content that counters bias rather than amplifying it |
| **SDG 10: Reduced Inequalities** | Makes counter-stereotype content available to any mother regardless of income, education, or access to diverse books; personalized to specific stereotypes |

---

## Ethical Considerations

| Consideration | Approach |
|--------------|----------|
| **Content Safety** | All generated stories pass through QA verification; age-appropriate language enforced by prompt design |
| **Historical Accuracy** | Real women's achievements verified against established historical record; stories clearly distinguish fiction from fact |
| **Cultural Sensitivity** | Knowledge base includes women from diverse backgrounds, cultures, and eras; stories avoid cultural appropriation |
| **AI Transparency** | Clear messaging that stories are AI-generated; illustration style clearly not photographs |
| **Stereotype Amplification** | QA loop specifically checks for inadvertent stereotype reinforcement (EMNLP 2025 research showed AI stories amplify stereotypes 55% more) |
| **Privacy** | No login, no data storage, no tracking; stories generated on-demand and not persisted |

---

## Differentiation from Existing Products

| Product | What It Does | EqualTales Difference |
|---------|-------------|----------------------|
| **Rebel Girls** | Pre-written biographical fairy tales of 100+ real women | EqualTales is AI-generated, personalized to the child's name, targeted to specific stereotypes, includes QA verification |
| **Intersectional Storyteller (UW)** | AI-generated diverse children's stories | EqualTales specifically targets stereotypes, integrates real women, has QA loop |
| **StoryBee** | AI story generator for kids | Not focused on stereotypes; no real-life women integration; no QA verification |
| **Generic AI chatbots** | Can generate stories on request | No structured narrative arc; no illustration pipeline; no stereotype verification; no knowledge base |

---

## Demo Flow (for Judges)

1. **Landing page** — One-sentence pitch, "Try It Now" button
2. **Input screen** — Three fields: stereotype text, child's age (slider), child's name
3. **Pre-loaded examples** — Quick-start buttons like "Girls can't do math" or "Boys are stronger than girls"
4. **Generation screen** — Story text streams in with typewriter effect; illustrations appear progressively as they generate
5. **Storybook view** — Beautiful 5-page layout with page turns, illustrations, and text
6. **Companion section** — Discussion prompts, related activities, more about the featured real woman
7. **QA badge** — Shows that the story passed stereotype verification

**Estimated judge experience:** ~90 seconds generation, 3-4 minutes reading = under 5 minutes total.
