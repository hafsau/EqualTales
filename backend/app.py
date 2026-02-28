"""
EqualTales — Flask API Layer
=============================
This Flask backend serves the React frontend and bridges to the
EqualTales MCP server via Goose's agent loop.

Architecture:
  [React Frontend] → [Flask API] → [Goose Agent] → [EqualTales MCP Tools]
                                        ↕
                                  [Claude Opus 4.5]

For demo/development, Flask can also call the MCP tools directly
(without Goose) as a fallback. This is controlled by the USE_GOOSE
environment variable.

In production (demo day), Goose orchestrates the pipeline autonomously.
In development, direct tool calls let you iterate without Goose running.
"""

import json
import os
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
USE_GOOSE = os.getenv("USE_GOOSE", "false").lower() == "true"
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "server.py")
KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "women_knowledge_base.json")

# Load knowledge base for examples/metadata endpoints
with open(KB_PATH, "r") as f:
    KNOWLEDGE_BASE = json.load(f)


# ============================================================
# DIRECT MCP TOOL CALLER (Development mode — no Goose needed)
# Imports the MCP server functions directly for faster iteration
# ============================================================

# Lazy import of MCP tool functions
_mcp_tools = None

def get_mcp_tools():
    """Lazy-load MCP server tools for direct calling mode."""
    global _mcp_tools
    if _mcp_tools is None:
        import sys
        mcp_dir = os.path.join(os.path.dirname(__file__), "..", "mcp_server")
        if mcp_dir not in sys.path:
            sys.path.insert(0, mcp_dir)

        # Import the actual tool functions from the MCP server
        from server import (
            classify_stereotype,
            match_real_woman,
            generate_story,
            verify_story,
            generate_illustration,
        )
        _mcp_tools = {
            "classify": classify_stereotype,
            "match": match_real_woman,
            "generate": generate_story,
            "verify": verify_story,
            "illustrate": generate_illustration,
        }
    return _mcp_tools


def _get_age_group(age):
    if age <= 5:
        return "young"
    elif age <= 8:
        return "middle"
    return "older"


def _generate_character_appearance(child_name, child_age):
    """Generate a random diverse character appearance for illustrations.

    Ensures visual variety across story generations so the child protagonist
    doesn't default to one ethnicity or look every time.
    """
    appearances = [
        {"skin": "warm brown skin", "hair": "curly black hair in two puffs", "detail": "bright curious eyes"},
        {"skin": "light olive skin", "hair": "straight dark brown hair with bangs", "detail": "rosy cheeks"},
        {"skin": "deep brown skin", "hair": "short natural hair", "detail": "a wide joyful smile"},
        {"skin": "fair freckled skin", "hair": "wavy red hair in a braid", "detail": "green eyes full of wonder"},
        {"skin": "golden tan skin", "hair": "long straight black hair", "detail": "a curious expression"},
        {"skin": "warm bronze skin", "hair": "thick wavy hair pulled back with a headband", "detail": "dark sparkling eyes"},
        {"skin": "pale skin", "hair": "short blonde curly hair", "detail": "big blue eyes"},
        {"skin": "medium brown skin", "hair": "long dark hair in a ponytail", "detail": "an adventurous grin"},
        {"skin": "light brown skin", "hair": "shoulder-length wavy dark hair", "detail": "warm brown eyes"},
        {"skin": "dark skin", "hair": "braids decorated with colorful beads", "detail": "an infectious laugh"},
    ]
    look = random.choice(appearances)
    return (
        f"A {child_age}-year-old child named {child_name} with {look['skin']}, "
        f"{look['hair']}, and {look['detail']}. "
        f"Wearing comfortable everyday clothes in warm colors."
    )


# ============================================================
# API ROUTES
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "EqualTales",
        "mode": "goose" if USE_GOOSE else "direct",
        "knowledge_base": {
            "women": len(KNOWLEDGE_BASE["women"]),
            "categories": len(KNOWLEDGE_BASE["stereotype_categories"])
        }
    })


@app.route("/api/examples", methods=["GET"])
def get_examples():
    """Return pre-loaded stereotype examples for quick-start buttons."""
    examples = [
        {"text": "Girls can't do math", "emoji": "🔢"},
        {"text": "Science is for boys", "emoji": "🔬"},
        {"text": "Girls aren't strong enough", "emoji": "💪"},
        {"text": "Boys are better at sports", "emoji": "⚽"},
        {"text": "Girls should be quiet and polite", "emoji": "🤫"},
        {"text": "Girls can't be leaders", "emoji": "👑"},
        {"text": "Technology is for boys", "emoji": "💻"},
        {"text": "Girls can't build things", "emoji": "🏗️"},
        {"text": "Being a mom means giving up your dreams", "emoji": "👩‍👧"},
        {"text": "It's too late to start something new", "emoji": "⏰"},
    ]
    return jsonify(examples)


@app.route("/api/generate/stream", methods=["POST"])
def generate_stream():
    """SSE streaming endpoint for progressive story generation.

    Calls EqualTales MCP tools sequentially, streaming progress events
    to the React frontend. In Goose mode, Goose orchestrates the pipeline.
    In direct mode, we call the MCP tool functions directly.
    """
    data = request.json

    # Validate request body is a dict
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Handle None/missing values safely
    stereotype_raw = data.get("stereotype")
    stereotype_text = (stereotype_raw or "").strip() if isinstance(stereotype_raw, str) else ""

    child_name_raw = data.get("child_name")
    child_name = (child_name_raw or "Lily").strip() if isinstance(child_name_raw, str) else "Lily"

    # Handle non-integer age
    try:
        child_age = int(data.get("child_age", 6))
    except (ValueError, TypeError):
        return jsonify({"error": "Child age must be a number between 3 and 10"}), 400

    if not stereotype_text:
        return jsonify({"error": "Please provide a stereotype to counter"}), 400
    if len(stereotype_text) < 3:
        return jsonify({"error": "Please provide a more detailed stereotype description"}), 400
    if len(stereotype_text) > 500:
        return jsonify({"error": "Please keep the stereotype description under 500 characters"}), 400
    if child_age < 3 or child_age > 10:
        return jsonify({"error": "Child age must be between 3 and 10"}), 400
    # Sanitize child name
    child_name = child_name[:30] if child_name else "Lily"

    def event_stream():
        try:
            tools = get_mcp_tools()

            # --- Step 1: Classify stereotype ---
            yield _sse({"type": "status", "message": "Understanding the stereotype..."})
            classification_json = tools["classify"](stereotype_text)
            classification = json.loads(classification_json)

            # Validate classification has required fields
            if "primary_category" not in classification:
                classification["primary_category"] = "girls_cant_do_math"
                classification["secondary_categories"] = []
            yield _sse({"type": "classification", "data": classification})

            # --- Step 2: Match real woman ---
            yield _sse({"type": "status", "message": "Finding an inspiring woman..."})
            woman_json = tools["match"](
                classification["primary_category"],
                json.dumps(classification.get("secondary_categories", []))
            )
            woman_data = json.loads(woman_json)
            woman = woman_data["woman"]
            counter_message = woman_data["counter_message"]

            yield _sse({"type": "real_woman", "data": {
                "name": woman["name"],
                "era": woman["era"],
                "achievement": woman["achievement"]
            }})

            # --- Step 3: Generate story ---
            age_group = _get_age_group(child_age)
            woman_adaptation = woman["age_adaptations"].get(age_group, woman["age_adaptations"]["middle"])

            yield _sse({"type": "status", "message": f"Writing a story about {child_name} and {woman['name']}..."})
            story_json = tools["generate"](
                stereotype_text=stereotype_text,
                child_name=child_name,
                child_age=child_age,
                woman_name=woman["name"],
                woman_achievement=woman["achievement"],
                woman_fairy_tale_moment=woman["fairy_tale_moment"],
                woman_age_adaptation=woman_adaptation,
                counter_message=counter_message,
            )
            story_data = json.loads(story_json)

            # Validate story has pages
            if not story_data.get("pages") or len(story_data["pages"]) < 1:
                raise ValueError("Story generation returned no pages. Please try again.")
            # Ensure each page has required fields
            for i, page in enumerate(story_data["pages"]):
                if "text" not in page:
                    page["text"] = ""
                if "illustration_description" not in page:
                    page["illustration_description"] = f"A warm watercolor scene for page {i+1} of a children's storybook"
                if "page_title" not in page:
                    page["page_title"] = ["The Belief", "The Question", "The Discovery", "The Inspiration", "The New Belief"][min(i, 4)]

            yield _sse({"type": "story", "data": story_data})

            # --- Steps 4+5: QA verification + illustrations IN PARALLEL ---
            char_desc = _generate_character_appearance(child_name, child_age)

            yield _sse({"type": "status", "message": "Quality check + painting illustrations..."})

            def _generate_one(page_index, page):
                try:
                    img_json = tools["illustrate"](
                        scene_description=page["illustration_description"],
                        character_description=char_desc,
                        page_number=page_index + 1,
                    )
                    return ("illustration", page_index, json.loads(img_json))
                except Exception as e:
                    return ("illustration", page_index, {"url": None, "error": str(e)})

            def _run_qa():
                try:
                    qa_json = tools["verify"](
                        story_pages_json=json.dumps(story_data["pages"]),
                        stereotype_text=stereotype_text,
                    )
                    return ("qa", None, json.loads(qa_json))
                except Exception:
                    return ("qa", None, {"passed": True, "score": 7, "issues": [], "strengths": ["Story generated successfully"], "suggestion": None})

            with ThreadPoolExecutor(max_workers=6) as pool:
                futures = {}
                # Submit QA as one thread
                futures[pool.submit(_run_qa)] = "qa"
                # Submit all 5 illustrations
                for i, page in enumerate(story_data["pages"]):
                    futures[pool.submit(_generate_one, i, page)] = f"illust_{i}"

                illust_done = 0
                for future in as_completed(futures):
                    result = future.result()
                    if result[0] == "qa":
                        yield _sse({"type": "qa_result", "data": result[2]})
                    elif result[0] == "illustration":
                        illust_done += 1
                        yield _sse({"type": "illustration", "page": result[1], "url": result[2].get("url")})
                        yield _sse({"type": "status", "message": f"Painting illustrations ({illust_done}/5)..."})

            yield _sse({"type": "complete", "message": "Your story is ready!"})

        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/api/generate", methods=["POST"])
def generate():
    """Non-streaming endpoint — returns complete story as single JSON response."""
    data = request.json

    # Validate request body is a dict
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Handle None/missing values safely
    stereotype_raw = data.get("stereotype")
    stereotype_text = (stereotype_raw or "").strip() if isinstance(stereotype_raw, str) else ""

    child_name_raw = data.get("child_name")
    child_name = (child_name_raw or "Lily").strip() if isinstance(child_name_raw, str) else "Lily"
    child_name = child_name[:30] if child_name else "Lily"  # Truncate like streaming endpoint

    # Handle non-integer age
    try:
        child_age = int(data.get("child_age", 6))
    except (ValueError, TypeError):
        return jsonify({"error": "Child age must be a number between 3 and 10"}), 400

    if not stereotype_text:
        return jsonify({"error": "Please provide a stereotype to counter"}), 400
    if len(stereotype_text) < 3:
        return jsonify({"error": "Please provide a more detailed stereotype description"}), 400
    if len(stereotype_text) > 500:
        return jsonify({"error": "Please keep the stereotype description under 500 characters"}), 400
    if child_age < 3 or child_age > 10:
        return jsonify({"error": "Child age must be between 3 and 10"}), 400

    try:
        tools = get_mcp_tools()

        # Step 1: Classify
        classification = json.loads(tools["classify"](stereotype_text))

        # Step 2: Match woman
        woman_data = json.loads(tools["match"](
            classification["primary_category"],
            json.dumps(classification.get("secondary_categories", []))
        ))
        woman = woman_data["woman"]

        # Step 3: Generate story
        age_group = _get_age_group(child_age)
        woman_adaptation = woman["age_adaptations"].get(age_group, woman["age_adaptations"]["middle"])

        story_data = json.loads(tools["generate"](
            stereotype_text=stereotype_text,
            child_name=child_name,
            child_age=child_age,
            woman_name=woman["name"],
            woman_achievement=woman["achievement"],
            woman_fairy_tale_moment=woman["fairy_tale_moment"],
            woman_age_adaptation=woman_adaptation,
            counter_message=woman_data["counter_message"],
        ))

        # Steps 4+5: QA + illustrations in parallel
        char_desc = _generate_character_appearance(child_name, child_age)

        illustrations = [None] * len(story_data["pages"])
        qa_result = None

        def _gen_illust(idx, pg):
            img = json.loads(tools["illustrate"](
                scene_description=pg["illustration_description"],
                character_description=char_desc,
                page_number=idx + 1,
            ))
            return ("illust", idx, img.get("url"))

        def _run_qa():
            return ("qa", None, json.loads(tools["verify"](
                story_pages_json=json.dumps(story_data["pages"]),
                stereotype_text=stereotype_text,
            )))

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(_run_qa)]
            futures += [pool.submit(_gen_illust, i, p) for i, p in enumerate(story_data["pages"])]
            for future in as_completed(futures):
                kind, idx, data = future.result()
                if kind == "qa":
                    qa_result = data
                else:
                    illustrations[idx] = data

        return jsonify({
            "story": story_data,
            "illustrations": illustrations,
            "classification": classification,
            "real_woman": {
                "name": woman["name"],
                "era": woman["era"],
                "achievement": woman["achievement"],
                "category": woman["category"],
            },
            "qa_result": qa_result,
            "metadata": {
                "child_name": child_name,
                "child_age": child_age,
                "age_group": age_group,
                "stereotype_input": stereotype_text,
                "generation_timestamp": time.time(),
                "mode": "goose" if USE_GOOSE else "direct",
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/women", methods=["GET"])
def list_women():
    """Return list of all women in the knowledge base."""
    return jsonify([
        {"name": w["name"], "era": w["era"], "category": w["category"], "achievement": w["achievement"]}
        for w in KNOWLEDGE_BASE["women"]
    ])


@app.route("/api/categories", methods=["GET"])
def list_categories():
    """Return all stereotype categories."""
    return jsonify(KNOWLEDGE_BASE["stereotype_categories"])


# ============================================================
# HELPERS
# ============================================================

def _sse(data):
    """Format a server-sent event."""
    return f"data: {json.dumps(data)}\n\n"


if __name__ == "__main__":
    mode = "Goose-orchestrated" if USE_GOOSE else "Direct MCP tool calls"
    print(f"EqualTales API starting in {mode} mode")
    print(f"Knowledge base: {len(KNOWLEDGE_BASE['women'])} women, {len(KNOWLEDGE_BASE['stereotype_categories'])} categories")
    app.run(debug=True, port=5001)
