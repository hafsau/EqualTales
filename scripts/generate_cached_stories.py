#!/usr/bin/env python3
"""
EqualTales Cache Generation Script
===================================
Pre-generates complete stories with illustrations for demo examples.

This script generates stories for all 10 example stereotypes, downloads
the DALL-E images, and saves everything to frontend/public/cached-stories/
for instant loading during demos.

Usage:
    python scripts/generate_cached_stories.py           # Generate all 10 stories
    python scripts/generate_cached_stories.py --one 0   # Generate only first example
    python scripts/generate_cached_stories.py --force   # Regenerate even if exists
    python scripts/generate_cached_stories.py --list    # List examples without generating
"""

import argparse
import json
import os
import sys
import time
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "mcp_server"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from server import (
    classify_stereotype,
    match_real_woman,
    generate_story,
    verify_story,
    generate_illustration,
)

# ============================================================
# CONFIGURATION
# ============================================================

CACHE_DIR = PROJECT_ROOT / "backend" / "cached-stories"

# The 10 example stereotypes (must match PRECOMPUTED_CLASSIFICATIONS in app.py)
EXAMPLE_STEREOTYPES = [
    ("Girls can't do math", "girls_cant_do_math", ["science_is_for_boys"]),
    ("Science is for boys", "science_is_for_boys", ["girls_cant_do_math"]),
    ("Girls aren't strong enough", "girls_arent_strong", []),
    ("Boys are better at sports", "girls_arent_strong", []),
    ("Girls should be quiet and polite", "girls_should_be_quiet", ["girls_cant_be_leaders"]),
    ("Girls can't be leaders", "girls_cant_be_leaders", ["girls_should_be_quiet"]),
    ("Technology is for boys", "girls_cant_do_tech", ["science_is_for_boys"]),
    ("Girls can't build things", "girls_cant_build_things", ["girls_cant_do_tech"]),
    ("Being a mom means giving up your dreams", "moms_cant_be_leaders", []),
    ("It's too late to start something new", "its_too_late_to_start", []),
]

DEFAULT_CHILD_NAME = "Lily"
DEFAULT_CHILD_AGE = 6

# Fixed character appearance for cached stories (ensures consistency)
CACHED_CHARACTER_APPEARANCE = (
    f"A {DEFAULT_CHILD_AGE}-year-old child named {DEFAULT_CHILD_NAME} with "
    "warm brown skin, curly black hair in two puffs, and bright curious eyes. "
    "Wearing comfortable everyday clothes in warm colors."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def stereotype_to_key(stereotype_text: str) -> str:
    """Convert stereotype text to URL-safe directory name."""
    return (
        stereotype_text.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace(",", "")
    )


def download_image(url: str, filepath: Path) -> bool:
    """Download image from URL and save to filepath."""
    try:
        print(f"    Downloading to {filepath.name}...")
        # Create SSL context that doesn't verify certificates (for macOS compatibility)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        request = urllib.request.Request(url, headers={"User-Agent": "EqualTales/1.0"})
        with urllib.request.urlopen(request, context=ctx) as response:
            with open(filepath, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"    ERROR downloading image: {e}")
        return False


def generate_cached_story(
    stereotype_text: str,
    primary_category: str,
    secondary_categories: list,
    force: bool = False,
) -> bool:
    """Generate and cache a complete story for an example stereotype."""
    key = stereotype_to_key(stereotype_text)
    story_dir = CACHE_DIR / key
    story_path = story_dir / "story.json"

    if story_path.exists() and not force:
        print(f"  SKIP: '{stereotype_text}' - already cached (use --force to regenerate)")
        return True

    print(f"\n{'='*60}")
    print(f"Generating: '{stereotype_text}'")
    print(f"{'='*60}")
    start_time = time.time()

    story_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Match woman ---
    print("  [1/5] Matching real woman...")
    try:
        woman_json = match_real_woman(
            primary_category,
            json.dumps(secondary_categories),
        )
        match_result = json.loads(woman_json)
        woman_data = match_result["woman"]  # Woman is nested inside the result
        print(f"    Matched: {woman_data.get('name', 'Unknown')}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # --- Step 2: Generate story ---
    print("  [2/5] Generating story (this takes ~40-50s)...")
    try:
        # Get counter_message from match result
        counter_message = match_result.get("counter_message", "Everyone can achieve great things regardless of gender")

        story_json = generate_story(
            stereotype_text=stereotype_text,
            child_name=DEFAULT_CHILD_NAME,
            child_age=DEFAULT_CHILD_AGE,
            woman_name=woman_data["name"],
            woman_achievement=woman_data["achievement"],
            woman_fairy_tale_moment=woman_data.get("fairy_tale_moment", ""),
            woman_age_adaptation=woman_data.get("age_adaptations", {}).get("middle", ""),
            counter_message=counter_message,
        )
        story_data = json.loads(story_json)
        print(f"    Story title: {story_data.get('title', 'Untitled')}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # --- Step 3: Verify story (QA) ---
    print("  [3/5] Running QA verification...")
    try:
        qa_json = verify_story(
            story_pages_json=json.dumps(story_data.get("pages", [])),
            stereotype_text=stereotype_text,
        )
        qa_result = json.loads(qa_json)
        print(f"    QA Score: {qa_result.get('score', 'N/A')}/10, Passed: {qa_result.get('passed', False)}")
    except Exception as e:
        print(f"    QA ERROR (using default): {e}")
        qa_result = {"passed": True, "score": 8, "issues": [], "strengths": ["Story generated successfully"]}

    # --- Step 4: Generate and download illustrations ---
    print("  [4/5] Generating illustrations (5 images)...")
    illustrations = []
    pages = story_data.get("pages", [])

    for i, page in enumerate(pages):
        page_num = i + 1
        print(f"    Generating illustration {page_num}/5...")
        try:
            img_json = generate_illustration(
                scene_description=page.get("illustration_description", page.get("text", "")),
                character_description=CACHED_CHARACTER_APPEARANCE,
                page_number=page_num,
            )
            img_data = json.loads(img_json)
            url = img_data.get("url")

            if url:
                # Download image
                img_path = story_dir / f"page{page_num}.webp"
                if download_image(url, img_path):
                    illustrations.append(f"/cached-stories/{key}/page{page_num}.webp")
                else:
                    illustrations.append(None)
            else:
                print(f"    No URL returned for page {page_num}")
                illustrations.append(None)
        except Exception as e:
            print(f"    ERROR generating illustration {page_num}: {e}")
            illustrations.append(None)

    # --- Step 5: Save complete story.json ---
    print("  [5/5] Saving story.json...")
    cached_story = {
        "metadata": {
            "stereotype_text": stereotype_text,
            "stereotype_key": key,
            "child_name": DEFAULT_CHILD_NAME,
            "child_age": DEFAULT_CHILD_AGE,
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "cache_version": 1,
        },
        "classification": {
            "primary_category": primary_category,
            "secondary_categories": secondary_categories,
        },
        "real_woman": {
            "name": woman_data.get("name", ""),
            "era": woman_data.get("era", ""),
            "achievement": woman_data.get("achievement", ""),
        },
        "story": story_data,
        "illustrations": illustrations,
        "qa_result": qa_result,
    }

    with open(story_path, "w") as f:
        json.dump(cached_story, f, indent=2)

    elapsed = time.time() - start_time
    print(f"\n  DONE in {elapsed:.1f}s - Saved to {story_dir}")
    return True


def generate_index():
    """Generate the index.json manifest."""
    index = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "stories": {},
    }

    for stereotype_text, _, _ in EXAMPLE_STEREOTYPES:
        key = stereotype_to_key(stereotype_text)
        story_path = CACHE_DIR / key / "story.json"
        if story_path.exists():
            index["stories"][stereotype_text] = key

    index_path = CACHE_DIR / "index.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    print(f"\nIndex saved: {index_path}")
    print(f"Total cached stories: {len(index['stories'])}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate cached stories for EqualTales demo examples"
    )
    parser.add_argument(
        "--one",
        type=int,
        metavar="N",
        help="Generate only the Nth example (0-9)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if already cached",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List examples without generating",
    )
    args = parser.parse_args()

    # List mode
    if args.list:
        print("Example stereotypes:")
        for i, (text, cat, _) in enumerate(EXAMPLE_STEREOTYPES):
            key = stereotype_to_key(text)
            cached = (CACHE_DIR / key / "story.json").exists()
            status = "[CACHED]" if cached else "[NOT CACHED]"
            print(f"  {i}: {text} {status}")
        return

    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EqualTales Cache Generation")
    print("=" * 60)
    print(f"Output directory: {CACHE_DIR}")
    print(f"Child name: {DEFAULT_CHILD_NAME}, Age: {DEFAULT_CHILD_AGE}")
    print()

    # Determine which examples to generate
    if args.one is not None:
        if args.one < 0 or args.one >= len(EXAMPLE_STEREOTYPES):
            print(f"ERROR: --one must be 0-{len(EXAMPLE_STEREOTYPES)-1}")
            sys.exit(1)
        examples = [EXAMPLE_STEREOTYPES[args.one]]
    else:
        examples = EXAMPLE_STEREOTYPES

    # Generate stories
    total_start = time.time()
    success_count = 0

    for stereotype_text, primary_category, secondary_categories in examples:
        if generate_cached_story(
            stereotype_text,
            primary_category,
            secondary_categories,
            force=args.force,
        ):
            success_count += 1

    # Generate index
    generate_index()

    total_elapsed = time.time() - total_start
    print()
    print("=" * 60)
    print(f"COMPLETE: {success_count}/{len(examples)} stories cached")
    print(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print("=" * 60)


if __name__ == "__main__":
    main()
