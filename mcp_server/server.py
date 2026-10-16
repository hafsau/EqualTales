#!/usr/bin/env python3
"""
EqualTales MCP Server
=====================
Custom MCP extension for Goose that provides 5 tools for the
anti-stereotype children's story generation pipeline:

1. classify_stereotype - Categorize a stereotype and select counter-narrative strategy
2. match_real_woman - Find the best real-life woman from the knowledge base
3. generate_story - Write a 5-page illustrated children's story
4. verify_story - QA check for inadvertent stereotype reinforcement
5. generate_illustration - Create a children's book illustration via an OpenAI image model

Goose orchestrates these tools autonomously through its agent loop.
"""

import json
import logging
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

from fastmcp import FastMCP

# ============================================================
# CRITICAL: All logging must go to stderr, never stdout
# stdout is reserved for MCP protocol messages
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("equaltales")

# Load environment variables
load_dotenv()

# ============================================================
# MODEL CONFIGURATION
# Pinned model IDs, overridable in .env without touching code
# ============================================================
STORY_MODEL = os.getenv("CLAUDE_STORY_MODEL", "claude-opus-5-5")   # writes the story
FAST_MODEL = os.getenv("CLAUDE_FAST_MODEL", "claude-haiku-5-5")    # classify + QA
STORY_EFFORT = os.getenv("CLAUDE_STORY_EFFORT", "medium")          # low | medium | high
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1-mini")

# Models that accept server-side refusal fallbacks ("default" routing)
_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"}

# Initialize MCP server
mcp = FastMCP("EqualTales — Anti-Stereotype Story Engine")

# ============================================================
# KNOWLEDGE BASE
# ============================================================
KB_PATH = Path(__file__).parent.parent / "data" / "women_knowledge_base.json"

try:
    with open(KB_PATH, "r") as f:
        KNOWLEDGE_BASE = json.load(f)
    logger.info(f"Loaded knowledge base: {len(KNOWLEDGE_BASE['women'])} women, {len(KNOWLEDGE_BASE['stereotype_categories'])} categories")
except FileNotFoundError:
    logger.error(f"Knowledge base not found at {KB_PATH}")
    KNOWLEDGE_BASE = {"women": [], "stereotype_categories": {}}


# ============================================================
# LAZY API CLIENT INITIALIZATION
# (Only created when a tool that needs them is called)
# ============================================================
_claude_client = None
_openai_client = None


def get_claude_client():
    """Get Anthropic client for the Claude text tools."""
    global _claude_client
    if _claude_client is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to .env (or the Render dashboard).")
        import anthropic
        # Keep the worst case (timeout x attempts) inside gunicorn's request timeout
        _claude_client = anthropic.Anthropic(timeout=120.0, max_retries=1)
        logger.info(f"Initialized Anthropic client (story={STORY_MODEL}, fast={FAST_MODEL})")
    return _claude_client


def _claude_json(prompt: str, schema: dict, model: str, effort: str, max_tokens: int) -> dict:
    """Call Claude and return the JSON object it produced.

    Structured outputs guarantee schema-valid JSON, so the checks below only
    cover the ways a call can still come back without a usable answer.
    """
    client = get_claude_client()
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    if model in _FALLBACK_MODELS:
        response = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        )
    else:
        response = client.messages.create(**kwargs)

    if response.stop_reason == "refusal":
        raise RuntimeError("The AI declined this request. Please try rephrasing the stereotype.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError(f"The AI response was cut off ({model}, max_tokens={max_tokens}). Please try again.")
    text = "".join(block.text for block in response.content if block.type == "text")
    if not text.strip():
        raise RuntimeError(f"The AI returned an empty response ({model}). Please try again.")
    return json.loads(text)


def get_openai_client():
    """Get OpenAI client for illustration generation."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("Initialized OpenAI client")
    return _openai_client


def _get_age_group(age: int) -> str:
    """Map child age to age group."""
    if age <= 5:
        return "young"
    elif age <= 8:
        return "middle"
    return "older"


def _parse_json_response(text: str) -> dict:
    """Extract JSON from Claude response, handling markdown code blocks."""
    if not text:
        raise ValueError("Empty response from model")
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from code block
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass
    # Try finding JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not parse JSON from response: {text[:200]}...")


# ============================================================
# TOOL 1: CLASSIFY STEREOTYPE
# ============================================================
@mcp.tool()
def classify_stereotype(stereotype_text: str) -> str:
    """Classify a gender stereotype and determine the counter-narrative strategy.

    Takes a stereotype that a child has expressed or that a parent wants to counter
    (e.g., "Girls can't do math" or "My daughter thinks science is only for boys")
    and classifies it into categories with an age-appropriate counter-narrative strategy.

    Args:
        stereotype_text: The stereotype to classify, as expressed by the child or parent

    Returns:
        JSON string with classification results including primary_category,
        secondary_categories, stereotype_essence, age_strategy, and emotional_tone
    """
    logger.info(f"Classifying stereotype: {stereotype_text}")

    categories = list(KNOWLEDGE_BASE["stereotype_categories"].keys())
    # The enum guarantees the model can only answer with a real category
    category_type = {"type": "string", "enum": categories} if categories else {"type": "string"}
    schema = {
        "type": "object",
        "properties": {
            "primary_category": category_type,
            "secondary_categories": {"type": "array", "items": category_type},
        },
        "required": ["primary_category", "secondary_categories"],
        "additionalProperties": False,
    }

    result = _claude_json(
        prompt=f"""Classify this stereotype into one of these categories: {json.dumps(categories)}

Stereotype: "{stereotype_text}"

Return JSON with:
1. "primary_category": best matching category from the list
2. "secondary_categories": array of 0-2 other relevant categories""",
        schema=schema,
        model=FAST_MODEL,
        effort="low",
        max_tokens=2000,
    )
    result["secondary_categories"] = result.get("secondary_categories", [])[:2]
    logger.info(f"Classification result: primary={result.get('primary_category')}")
    return json.dumps(result, indent=2)


# ============================================================
# TOOL 2: MATCH REAL WOMAN
# ============================================================
@mcp.tool()
def match_real_woman(primary_category: str, secondary_categories: str = "[]") -> str:
    """Select the best real-life woman from the knowledge base to feature in the story.

    Matches a classified stereotype to a real historical woman whose achievements
    directly counter the stereotype. Returns her full profile with age-adapted
    descriptions and fairy-tale moments.

    Args:
        primary_category: The primary stereotype category (e.g., "girls_cant_do_math")
        secondary_categories: JSON array string of secondary categories (e.g., '["science_is_for_boys"]')

    Returns:
        JSON string with the selected woman's complete profile including name, era,
        achievement, fairy_tale_moment, age_adaptations, and counters_stereotypes
    """
    logger.info(f"Matching woman for category: {primary_category}")

    try:
        sec_cats = json.loads(secondary_categories) if secondary_categories else []
    except json.JSONDecodeError:
        sec_cats = []

    all_cats = [primary_category] + sec_cats

    # Get suggested women from stereotype categories
    suggested_names = set()
    for cat in all_cats:
        cat_data = KNOWLEDGE_BASE["stereotype_categories"].get(cat, {})
        for name in cat_data.get("suggested_women", []):
            suggested_names.add(name)

    # Find matching women and score them
    candidates = []
    for woman in KNOWLEDGE_BASE["women"]:
        if woman["name"] in suggested_names:
            woman_cats = set(woman.get("counters_stereotypes", []))
            overlap = len(woman_cats.intersection(set(all_cats)))
            candidates.append((woman, overlap))

    candidates.sort(key=lambda x: x[1], reverse=True)

    if candidates:
        # Pick from top 3 for variety
        top = candidates[: min(3, len(candidates))]
        selected = random.choice(top)[0]
    else:
        # Fallback: pick from suggested_women for the primary category
        cat_data = KNOWLEDGE_BASE["stereotype_categories"].get(primary_category, {})
        suggested = cat_data.get("suggested_women", [])
        selected = None
        if suggested:
            # Find the woman object by name from suggested list
            for woman in KNOWLEDGE_BASE["women"]:
                if woman["name"] in suggested:
                    selected = woman
                    break
        # If still no match, pick randomly (last resort)
        if not selected:
            selected = random.choice(KNOWLEDGE_BASE["women"])

    # Also include the counter message from the category
    cat_data = KNOWLEDGE_BASE["stereotype_categories"].get(primary_category, {})

    result = {
        "woman": selected,
        "counter_message": cat_data.get(
            "counter_message",
            "Everyone can achieve great things regardless of gender",
        ),
        "match_quality": "strong" if candidates else "fallback",
    }

    logger.info(f"Selected: {selected['name']} ({result['match_quality']} match)")
    return json.dumps(result, indent=2)


# ============================================================
# TOOL 3: GENERATE STORY
# ============================================================
_STORY_PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "page_number": {"type": "integer"},
        "page_title": {"type": "string"},
        "text": {"type": "string"},
        "illustration_description": {"type": "string"},
    },
    "required": ["page_number", "page_title", "text", "illustration_description"],
    "additionalProperties": False,
}

STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "pages": {"type": "array", "items": _STORY_PAGE_SCHEMA},
        "real_woman_name": {"type": "string"},
        "real_woman_achievement": {"type": "string"},
        "discussion_prompts": {"type": "array", "items": {"type": "string"}},
        "activity_suggestion": {"type": "string"},
    },
    "required": [
        "title", "pages", "real_woman_name", "real_woman_achievement",
        "discussion_prompts", "activity_suggestion",
    ],
    "additionalProperties": False,
}


@mcp.tool()
def generate_story(
    stereotype_text: str,
    child_name: str,
    child_age: int,
    woman_name: str,
    woman_achievement: str,
    woman_fairy_tale_moment: str,
    woman_age_adaptation: str,
    counter_message: str,
) -> str:
    """Generate a personalized 5-page anti-stereotype children's story.

    Creates a complete story following the narrative arc: The Belief → The Question →
    The Discovery → The Inspiration → The New Belief. The fictional protagonist
    shares the child's name and discovers the real woman as proof that the
    stereotype is wrong.

    Args:
        stereotype_text: The stereotype to counter
        child_name: Name of the child (becomes the story protagonist)
        child_age: Age of the child (3-10, determines reading level)
        woman_name: Name of the real woman to feature
        woman_achievement: One-sentence description of her achievement
        woman_fairy_tale_moment: Her key moment told in fairy-tale language
        woman_age_adaptation: Age-appropriate version of her story
        counter_message: The counter-stereotype message to weave in

    Returns:
        JSON string with complete 5-page story including title, page texts,
        illustration descriptions, discussion prompts, and activity suggestion
    """
    logger.info(f"Generating story: {child_name} (age {child_age}) + {woman_name}")

    age_group = _get_age_group(child_age)

    prompt = f"""You are a children's story writer creating an anti-stereotype story. Write a 5-page illustrated children's story.

INPUTS:
- Stereotype to counter: "{stereotype_text}"
- Child's name: {child_name}
- Child's age: {child_age} ({age_group} reading level)
- Real woman to feature: {woman_name}
- Her achievement: {woman_achievement}
- Her fairy-tale moment: {woman_fairy_tale_moment}
- Age-appropriate version: {woman_age_adaptation}
- Counter-message: {counter_message}

STORY STRUCTURE (exactly 5 pages):

Page 1 — "The Belief": {child_name} encounters or expresses the stereotype in a relatable, everyday situation. Show the belief naturally — through a classmate's comment, a TV show, or an overheard conversation. Don't make {child_name} the villain; they're absorbing what the world tells them.

Page 2 — "The Question": Something happens that cracks the stereotype. {child_name} sees, hears, or experiences something that doesn't fit the belief. Curiosity emerges. This should feel surprising and magical.

Page 3 — "The Discovery": {child_name} discovers {woman_name}. This isn't a biography dump — it's a magical discovery. Maybe they find an old book, a portrait comes alive, or a wise character tells them about this remarkable person. Use: {woman_fairy_tale_moment}

Page 4 — "The Inspiration": Tell {woman_name}'s specific story in fairy-tale language appropriate for age {child_age}. Use: {woman_age_adaptation}. Make it vivid and awe-inspiring. Show the obstacles she faced and how she overcame them.

Page 5 — "The New Belief": {child_name} returns to their world changed. They take a specific action inspired by what they learned. The old belief is replaced by a new understanding. End with hope and empowerment — not a lecture.

WRITING RULES:
- {"Use short sentences (5-10 words). Simple vocabulary. Lots of sensory details. Repetition for emphasis." if age_group == "young" else "Use medium-length sentences. Vivid descriptions. Some challenging vocabulary with context clues." if age_group == "middle" else "Use varied sentence structures. Rich vocabulary. Nuance and complexity. Emotional depth."}
- Each page should be {"3-5 sentences" if age_group == "young" else "5-8 sentences" if age_group == "middle" else "6-10 sentences"}
- Show, don't tell. Never say "stereotypes are bad." Let the story do the work.
- The story should feel warm, magical, and empowering — never preachy or guilt-inducing.
- {child_name} should feel like a real kid the reader can identify with.

OUTPUT FORMAT:
Return ONLY a JSON object with this structure:
{{
  "title": "story title",
  "pages": [
    {{
      "page_number": 1,
      "page_title": "The Belief",
      "text": "the story text for this page",
      "illustration_description": "A detailed description for an illustrator: scene, action, colors, mood, specific visual elements. Do NOT describe the child's race, skin color, hair type, or ethnicity — the character appearance will be provided separately for consistency."
    }},
    ... (5 pages total)
  ],
  "real_woman_name": "{woman_name}",
  "real_woman_achievement": "one sentence about her achievement for the companion section",
  "discussion_prompts": ["3 questions a parent can ask their child after reading"],
  "activity_suggestion": "one hands-on activity related to the story theme"
}}

Return ONLY valid JSON."""

    result = _claude_json(
        prompt=prompt,
        schema=STORY_SCHEMA,
        model=STORY_MODEL,
        effort=STORY_EFFORT,
        max_tokens=16000,
    )
    logger.info(f"Story generated: '{result.get('title')}' with {len(result.get('pages', []))} pages")
    return json.dumps(result, indent=2)


# ============================================================
# TOOL 4: VERIFY STORY (QA)
# ============================================================
@mcp.tool()
def verify_story(story_pages_json: str, stereotype_text: str) -> str:
    """Run QA verification on a generated story to check for stereotype reinforcement.

    Analyzes the story text to ensure it doesn't inadvertently reinforce the stereotype
    it's trying to counter, introduce new stereotypes, or use preachy/inappropriate language.
    Based on EMNLP 2025 research showing AI-generated stories amplify stereotypes 55% more
    than human-written ones.

    Args:
        story_pages_json: JSON string of the story pages array, each with "text" field
        stereotype_text: The original stereotype the story was meant to counter

    Returns:
        JSON string with QA results including passed (bool), score (1-10),
        issues found, strengths, and improvement suggestions
    """
    logger.info(f"Running QA verification for stereotype: {stereotype_text}")

    try:
        pages = json.loads(story_pages_json)
    except json.JSONDecodeError:
        pages = []

    if isinstance(pages, dict) and "pages" in pages:
        pages = pages["pages"]

    story_text = "\n\n".join(
        [f"Page {p.get('page_number', i+1)} — {p.get('page_title', '')}: {p.get('text', '')}" for i, p in enumerate(pages)]
    )

    schema = {
        "type": "object",
        "properties": {
            "passed": {"type": "boolean"},
            "score": {"type": "integer"},
            "issues": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "suggestion": {"type": "string"},
        },
        "required": ["passed", "score", "issues", "strengths", "suggestion"],
        "additionalProperties": False,
    }

    result = _claude_json(
        prompt=f"""You are a stereotype detection system for children's content. Analyze this story that was generated to counter the stereotype: "{stereotype_text}"

STORY TEXT:
{story_text}

Check for:
1. Does the story inadvertently REINFORCE the stereotype it's trying to counter?
2. Does it introduce NEW stereotypes (e.g., describing girls primarily by appearance)?
3. Is the language age-appropriate and non-preachy?
4. Does the real woman's story feel natural, not forced?
5. Is the ending empowering without being unrealistic?
6. Are characters described with agency and dimension, not just by gender or appearance?

Return a JSON object:
{{
  "passed": true/false,
  "score": 1-10 (10 = perfect),
  "issues": ["list of any issues found"],
  "strengths": ["list of things done well"],
  "suggestion": "one brief improvement suggestion if score < 8, otherwise an empty string"
}}""",
        schema=schema,
        model=FAST_MODEL,
        effort="low",
        max_tokens=4000,
    )
    # The frontend expects null when there is no suggestion
    result["suggestion"] = result.get("suggestion") or None
    logger.info(f"QA result: passed={result.get('passed')}, score={result.get('score')}")
    return json.dumps(result, indent=2)


# ============================================================
# TOOL 5: GENERATE ILLUSTRATION
# ============================================================
@mcp.tool()
def generate_illustration(
    scene_description: str,
    character_description: str = "",
    page_number: int = 1,
) -> str:
    """Generate a children's book illustration using an OpenAI image model.

    Creates a warm, whimsical watercolor-style illustration suitable for a
    children's picture book. Uses consistent character descriptions across
    pages to maintain visual continuity.

    Args:
        scene_description: Detailed description of the scene to illustrate
        character_description: Consistent description of the main character's appearance (hair, skin, clothing) to maintain continuity across pages
        page_number: Which page this illustration is for (1-5)

    Returns:
        JSON string with the image URL and generation metadata
    """
    logger.info(f"Generating illustration for page {page_number}")

    client = get_openai_client()

    character_note = ""
    if character_description:
        character_note = f"\nMAIN CHARACTER (must appear exactly like this): {character_description}"

    prompt = f"""Create a children's book illustration in a warm, whimsical watercolor style with soft colors and gentle brushstrokes.

Style: Warm watercolor, soft pastels with pops of vibrant color, hand-drawn feel, inclusive and diverse characters, gentle and magical atmosphere. Suitable for ages 3-10.{character_note}

Scene (Page {page_number} of 5): {scene_description}

Important: This is for a children's picture book about breaking gender stereotypes. Keep it warm, inviting, age-appropriate, and beautiful. Characters should be expressive and full of wonder. Use a consistent warm color palette with coral, gold, sage green, and soft purple accents."""

    try:
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="medium",      # ~12s per image vs ~30s at the default quality
            output_format="jpeg",  # smaller payload than PNG over SSE
            n=1,
        )

        # gpt-image models return base64, convert to data URL
        image_data = response.data[0]
        if hasattr(image_data, 'b64_json') and image_data.b64_json:
            url = f"data:image/jpeg;base64,{image_data.b64_json}"
        elif hasattr(image_data, 'url') and image_data.url:
            url = image_data.url
        else:
            raise ValueError("No image data in response")

        result = {
            "url": url,
            "page_number": page_number,
            "revised_prompt": getattr(image_data, 'revised_prompt', None),
            "status": "success",
        }
        logger.info(f"Illustration generated for page {page_number}")
    except Exception as e:
        logger.error(f"Image generation error for page {page_number}: {e}")
        result = {
            "url": None,
            "page_number": page_number,
            "error": str(e),
            "status": "failed",
        }

    return json.dumps(result, indent=2)


# ============================================================
# SERVER STARTUP
# ============================================================
if __name__ == "__main__":
    logger.info("Starting EqualTales MCP Server...")
    logger.info(f"Knowledge base: {len(KNOWLEDGE_BASE['women'])} women, {len(KNOWLEDGE_BASE['stereotype_categories'])} categories")
    mcp.run()
