"""
Pytest configuration and fixtures for EqualTales backend tests.
"""
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# SAMPLE DATA FIXTURES
# ============================================================

@pytest.fixture
def sample_knowledge_base():
    """Minimal knowledge base for testing."""
    return {
        "women": [
            {
                "name": "Katherine Johnson",
                "era": "1918-2020",
                "category": ["math", "space"],
                "achievement": "Calculated trajectories for NASA missions",
                "fairy_tale_moment": "She became the human computer who sent astronauts to the moon",
                "age_adaptations": {
                    "young": "She was so good at counting!",
                    "middle": "Katherine's math helped rockets fly.",
                    "older": "Katherine's calculations were trusted over computers."
                },
                "counters_stereotypes": ["girls_cant_do_math", "science_is_for_boys"]
            },
            {
                "name": "Mae Jemison",
                "era": "1956-present",
                "category": ["science", "space"],
                "achievement": "First African American woman astronaut",
                "fairy_tale_moment": "She flew among the stars",
                "age_adaptations": {
                    "young": "She flew to space!",
                    "middle": "Mae became an astronaut and doctor.",
                    "older": "Mae broke barriers in science and space."
                },
                "counters_stereotypes": ["science_is_for_boys", "girls_cant_be_adventurous"]
            }
        ],
        "stereotype_categories": {
            "girls_cant_do_math": {
                "counter_message": "Math is for everyone!",
                "suggested_women": ["Katherine Johnson", "Ada Lovelace"]
            },
            "science_is_for_boys": {
                "counter_message": "Science belongs to curious minds of all kinds!",
                "suggested_women": ["Mae Jemison", "Marie Curie"]
            }
        }
    }


@pytest.fixture
def sample_classification():
    """Sample classification result."""
    return {
        "primary_category": "girls_cant_do_math",
        "secondary_categories": ["science_is_for_boys"],
        "stereotype_essence": "Belief that mathematical ability is gender-linked",
        "age_strategy": {
            "young": "Focus on counting and simple patterns",
            "middle": "Show problem-solving adventures",
            "older": "Discuss historical mathematicians"
        },
        "emotional_tone": "limiting"
    }


@pytest.fixture
def sample_story_data():
    """Sample generated story."""
    return {
        "title": "Lily and the Number Stars",
        "pages": [
            {
                "page_number": 1,
                "page_title": "The Belief",
                "text": "Lily loved her classroom, but one day she heard something strange.",
                "illustration_description": "A child in a colorful classroom looking curious."
            },
            {
                "page_number": 2,
                "page_title": "The Question",
                "text": "Wait, thought Lily. That doesn't seem right.",
                "illustration_description": "A child looking thoughtful with question marks around."
            },
            {
                "page_number": 3,
                "page_title": "The Discovery",
                "text": "In the library, Lily found a magical book about Katherine Johnson.",
                "illustration_description": "A child discovering a glowing book in a library."
            },
            {
                "page_number": 4,
                "page_title": "The Inspiration",
                "text": "Katherine Johnson calculated the paths for rockets to the moon!",
                "illustration_description": "A woman working on equations with rockets in the background."
            },
            {
                "page_number": 5,
                "page_title": "The New Belief",
                "text": "Lily smiled. Anyone can do math. Even me!",
                "illustration_description": "A happy child writing numbers with confidence."
            }
        ],
        "real_woman_name": "Katherine Johnson",
        "real_woman_achievement": "NASA mathematician who calculated space flight trajectories",
        "discussion_prompts": [
            "What did Lily learn?",
            "Have you ever felt like you couldn't do something?",
            "What would you like to try?"
        ],
        "activity_suggestion": "Count the objects in your room!"
    }


@pytest.fixture
def sample_qa_result():
    """Sample QA verification result."""
    return {
        "passed": True,
        "score": 9,
        "issues": [],
        "strengths": ["Age-appropriate language", "Natural story flow", "Empowering ending"],
        "suggestion": None
    }


@pytest.fixture
def sample_illustration_result():
    """Sample illustration generation result."""
    return {
        "url": "https://example.com/image.png",
        "page_number": 1,
        "revised_prompt": "A warm watercolor illustration...",
        "status": "success"
    }


# ============================================================
# MOCK FIXTURES
# ============================================================

@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client for Claude API calls."""
    mock_client = MagicMock()

    def create_completion(*args, **kwargs):
        response = MagicMock()
        response.choices = [MagicMock()]

        # Determine what kind of response based on the model
        model = kwargs.get('model', '')
        messages = kwargs.get('messages', [{}])
        content = messages[0].get('content', '') if messages else ''

        if 'sonnet' in model and 'Analyze this stereotype' in content:
            # Classification response
            response.choices[0].message.content = json.dumps({
                "primary_category": "girls_cant_do_math",
                "secondary_categories": ["science_is_for_boys"],
                "stereotype_essence": "Belief that math is for boys",
                "age_strategy": {"young": "...", "middle": "...", "older": "..."},
                "emotional_tone": "limiting"
            })
        elif 'opus' in model:
            # Story generation response
            response.choices[0].message.content = json.dumps({
                "title": "Test Story",
                "pages": [
                    {"page_number": i+1, "page_title": t, "text": f"Page {i+1} text.", "illustration_description": f"Scene {i+1}"}
                    for i, t in enumerate(["The Belief", "The Question", "The Discovery", "The Inspiration", "The New Belief"])
                ],
                "real_woman_name": "Katherine Johnson",
                "real_woman_achievement": "NASA mathematician",
                "discussion_prompts": ["Q1?", "Q2?", "Q3?"],
                "activity_suggestion": "Try counting!"
            })
        elif 'sonnet' in model and 'stereotype detection' in content.lower():
            # QA verification response
            response.choices[0].message.content = json.dumps({
                "passed": True,
                "score": 9,
                "issues": [],
                "strengths": ["Good story"],
                "suggestion": None
            })
        else:
            response.choices[0].message.content = "{}"

        return response

    mock_client.chat.completions.create = MagicMock(side_effect=create_completion)
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for DALL-E calls."""
    mock_client = MagicMock()

    def generate_image(*args, **kwargs):
        response = MagicMock()
        response.data = [MagicMock()]
        response.data[0].url = "https://example.com/test-image.png"
        response.data[0].revised_prompt = "A warm watercolor test image"
        return response

    mock_client.images.generate = MagicMock(side_effect=generate_image)
    return mock_client


@pytest.fixture
def mock_mcp_tools(sample_classification, sample_story_data, sample_qa_result, sample_illustration_result):
    """Mock MCP tools dictionary."""
    return {
        "classify": MagicMock(return_value=json.dumps(sample_classification)),
        "match": MagicMock(return_value=json.dumps({
            "woman": {
                "name": "Katherine Johnson",
                "era": "1918-2020",
                "category": ["math", "space"],
                "achievement": "NASA mathematician",
                "fairy_tale_moment": "She sent astronauts to the moon with her calculations",
                "age_adaptations": {"young": "...", "middle": "...", "older": "..."},
                "counters_stereotypes": ["girls_cant_do_math"]
            },
            "counter_message": "Math is for everyone!",
            "match_quality": "strong"
        })),
        "generate": MagicMock(return_value=json.dumps(sample_story_data)),
        "verify": MagicMock(return_value=json.dumps(sample_qa_result)),
        "illustrate": MagicMock(return_value=json.dumps(sample_illustration_result))
    }


# ============================================================
# APP FIXTURES
# ============================================================

@pytest.fixture
def app(sample_knowledge_base):
    """Create test Flask application."""
    with patch.dict('os.environ', {'USE_GOOSE': 'false'}):
        # Patch knowledge base loading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_knowledge_base)

            # Import app after patching
            import importlib
            if 'app' in sys.modules:
                del sys.modules['app']

            # We need to handle the import carefully
            import app as flask_app
            flask_app.KNOWLEDGE_BASE = sample_knowledge_base
            flask_app.app.config['TESTING'] = True

            yield flask_app.app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# ============================================================
# VALIDATION TEST DATA
# ============================================================

@pytest.fixture
def valid_generation_input():
    """Valid input for story generation."""
    return {
        "stereotype": "Girls can't do math",
        "child_name": "Lily",
        "child_age": 6
    }


@pytest.fixture
def invalid_inputs():
    """Collection of invalid inputs for edge case testing."""
    return {
        "empty_stereotype": {"stereotype": "", "child_name": "Lily", "child_age": 6},
        "short_stereotype": {"stereotype": "ab", "child_name": "Lily", "child_age": 6},
        "long_stereotype": {"stereotype": "x" * 501, "child_name": "Lily", "child_age": 6},
        "age_too_young": {"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 2},
        "age_too_old": {"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 11},
        "missing_stereotype": {"child_name": "Lily", "child_age": 6},
        "whitespace_stereotype": {"stereotype": "   ", "child_name": "Lily", "child_age": 6},
    }
