"""
Unit tests for EqualTales MCP Server (mcp_server/server.py)

Tests all 5 MCP tools, helper functions, and error handling.
Run with: pytest tests/test_mcp_server.py -v
"""
import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add mcp_server to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'mcp_server'))


# ============================================================
# HELPER FUNCTION TESTS
# ============================================================

class TestGetAgeGroup:
    """Test _get_age_group helper function."""

    def test_age_3_is_young(self):
        from server import _get_age_group
        assert _get_age_group(3) == "young"

    def test_age_5_is_young(self):
        from server import _get_age_group
        assert _get_age_group(5) == "young"

    def test_age_6_is_middle(self):
        from server import _get_age_group
        assert _get_age_group(6) == "middle"

    def test_age_8_is_middle(self):
        from server import _get_age_group
        assert _get_age_group(8) == "middle"

    def test_age_9_is_older(self):
        from server import _get_age_group
        assert _get_age_group(9) == "older"

    def test_age_10_is_older(self):
        from server import _get_age_group
        assert _get_age_group(10) == "older"


class TestParseJsonResponse:
    """Test _parse_json_response helper function."""

    def test_parses_valid_json(self):
        from server import _parse_json_response
        result = _parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parses_json_in_markdown_block(self):
        from server import _parse_json_response
        text = '```json\n{"key": "value"}\n```'
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_parses_json_with_surrounding_text(self):
        from server import _parse_json_response
        text = 'Here is the result:\n{"key": "value"}\nThat\'s it!'
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_raises_on_invalid_json(self):
        from server import _parse_json_response
        with pytest.raises(ValueError):
            _parse_json_response('not json at all')

    def test_handles_nested_json(self):
        from server import _parse_json_response
        text = '{"outer": {"inner": "value"}}'
        result = _parse_json_response(text)
        assert result["outer"]["inner"] == "value"


# ============================================================
# CLASSIFY STEREOTYPE TOOL TESTS
# ============================================================

class TestClassifyStereotype:
    """Test classify_stereotype MCP tool."""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenRouter client."""
        mock = MagicMock()
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = json.dumps({
            "primary_category": "girls_cant_do_math",
            "secondary_categories": ["science_is_for_boys"],
            "stereotype_essence": "Belief that math is gender-linked",
            "age_strategy": {"young": "...", "middle": "...", "older": "..."},
            "emotional_tone": "limiting"
        })
        mock.chat.completions.create.return_value = response
        return mock

    def test_returns_json_string(self, mock_client):
        from server import classify_stereotype
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = classify_stereotype("Girls can't do math")
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    def test_returns_primary_category(self, mock_client):
        from server import classify_stereotype
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(classify_stereotype("Girls can't do math"))
            assert "primary_category" in result

    def test_returns_secondary_categories(self, mock_client):
        from server import classify_stereotype
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(classify_stereotype("Girls can't do math"))
            assert "secondary_categories" in result

    def test_returns_emotional_tone(self, mock_client):
        from server import classify_stereotype
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(classify_stereotype("Girls can't do math"))
            assert "emotional_tone" in result

    def test_uses_sonnet_model(self, mock_client):
        from server import classify_stereotype
        with patch('server.get_openrouter_client', return_value=mock_client):
            classify_stereotype("Girls can't do math")
            call_args = mock_client.chat.completions.create.call_args
            assert 'sonnet' in call_args.kwargs['model']


# ============================================================
# MATCH REAL WOMAN TOOL TESTS
# ============================================================

class TestMatchRealWoman:
    """Test match_real_woman MCP tool."""

    def test_returns_json_string(self):
        from server import match_real_woman
        result = match_real_woman("girls_cant_do_math", "[]")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_returns_woman_object(self):
        from server import match_real_woman
        result = json.loads(match_real_woman("girls_cant_do_math", "[]"))
        assert "woman" in result
        assert "name" in result["woman"]

    def test_returns_counter_message(self):
        from server import match_real_woman
        result = json.loads(match_real_woman("girls_cant_do_math", "[]"))
        assert "counter_message" in result

    def test_returns_match_quality(self):
        from server import match_real_woman
        result = json.loads(match_real_woman("girls_cant_do_math", "[]"))
        assert "match_quality" in result
        assert result["match_quality"] in ["strong", "fallback"]

    def test_handles_secondary_categories(self):
        from server import match_real_woman
        result = json.loads(match_real_woman(
            "girls_cant_do_math",
            '["science_is_for_boys"]'
        ))
        assert "woman" in result

    def test_handles_invalid_secondary_categories_json(self):
        from server import match_real_woman
        # Should not crash, just treat as empty
        result = json.loads(match_real_woman("girls_cant_do_math", "not valid json"))
        assert "woman" in result

    def test_handles_unknown_category(self):
        from server import match_real_woman
        # Should fall back to random woman
        result = json.loads(match_real_woman("unknown_category", "[]"))
        assert "woman" in result
        assert result["match_quality"] == "fallback"

    def test_woman_has_required_fields(self):
        from server import match_real_woman
        result = json.loads(match_real_woman("girls_cant_do_math", "[]"))
        woman = result["woman"]
        assert "name" in woman
        assert "era" in woman
        assert "achievement" in woman
        assert "fairy_tale_moment" in woman
        assert "age_adaptations" in woman


# ============================================================
# GENERATE STORY TOOL TESTS
# ============================================================

class TestGenerateStory:
    """Test generate_story MCP tool."""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenRouter client for story generation."""
        mock = MagicMock()
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = json.dumps({
            "title": "Test Story",
            "pages": [
                {"page_number": i+1, "page_title": t, "text": f"Page {i+1}", "illustration_description": f"Scene {i+1}"}
                for i, t in enumerate(["The Belief", "The Question", "The Discovery", "The Inspiration", "The New Belief"])
            ],
            "real_woman_name": "Katherine Johnson",
            "real_woman_achievement": "NASA mathematician",
            "discussion_prompts": ["Q1?", "Q2?", "Q3?"],
            "activity_suggestion": "Try counting!"
        })
        mock.chat.completions.create.return_value = response
        return mock

    def test_returns_json_string(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="She sent astronauts to the moon",
                woman_age_adaptation="Katherine loved numbers",
                counter_message="Math is for everyone"
            )
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    def test_returns_title(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="...",
                woman_age_adaptation="...",
                counter_message="..."
            ))
            assert "title" in result

    def test_returns_5_pages(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="...",
                woman_age_adaptation="...",
                counter_message="..."
            ))
            assert len(result["pages"]) == 5

    def test_pages_have_required_fields(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="...",
                woman_age_adaptation="...",
                counter_message="..."
            ))
            for page in result["pages"]:
                assert "page_number" in page
                assert "page_title" in page
                assert "text" in page
                assert "illustration_description" in page

    def test_returns_discussion_prompts(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="...",
                woman_age_adaptation="...",
                counter_message="..."
            ))
            assert "discussion_prompts" in result
            assert len(result["discussion_prompts"]) == 3

    def test_uses_opus_model(self, mock_client):
        from server import generate_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            generate_story(
                stereotype_text="Girls can't do math",
                child_name="Lily",
                child_age=6,
                woman_name="Katherine Johnson",
                woman_achievement="NASA mathematician",
                woman_fairy_tale_moment="...",
                woman_age_adaptation="...",
                counter_message="..."
            )
            call_args = mock_client.chat.completions.create.call_args
            assert 'opus' in call_args.kwargs['model']


# ============================================================
# VERIFY STORY TOOL TESTS
# ============================================================

class TestVerifyStory:
    """Test verify_story MCP tool."""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenRouter client for QA."""
        mock = MagicMock()
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = json.dumps({
            "passed": True,
            "score": 9,
            "issues": [],
            "strengths": ["Good story flow", "Age-appropriate language"],
            "suggestion": None
        })
        mock.chat.completions.create.return_value = response
        return mock

    @pytest.fixture
    def sample_pages_json(self):
        return json.dumps([
            {"page_number": 1, "page_title": "The Belief", "text": "Page 1 text"},
            {"page_number": 2, "page_title": "The Question", "text": "Page 2 text"},
            {"page_number": 3, "page_title": "The Discovery", "text": "Page 3 text"},
            {"page_number": 4, "page_title": "The Inspiration", "text": "Page 4 text"},
            {"page_number": 5, "page_title": "The New Belief", "text": "Page 5 text"},
        ])

    def test_returns_json_string(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = verify_story(sample_pages_json, "Girls can't do math")
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    def test_returns_passed_boolean(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(verify_story(sample_pages_json, "Girls can't do math"))
            assert "passed" in result
            assert isinstance(result["passed"], bool)

    def test_returns_score(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(verify_story(sample_pages_json, "Girls can't do math"))
            assert "score" in result
            assert 1 <= result["score"] <= 10

    def test_returns_issues_list(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(verify_story(sample_pages_json, "Girls can't do math"))
            assert "issues" in result
            assert isinstance(result["issues"], list)

    def test_returns_strengths_list(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(verify_story(sample_pages_json, "Girls can't do math"))
            assert "strengths" in result
            assert isinstance(result["strengths"], list)

    def test_handles_invalid_json_input(self, mock_client):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            # Should not crash
            result = json.loads(verify_story("not valid json", "Girls can't do math"))
            assert "passed" in result

    def test_handles_nested_pages_object(self, mock_client):
        from server import verify_story
        nested = json.dumps({"pages": [{"page_number": 1, "text": "Test"}]})
        with patch('server.get_openrouter_client', return_value=mock_client):
            result = json.loads(verify_story(nested, "Girls can't do math"))
            assert "passed" in result

    def test_uses_sonnet_model(self, mock_client, sample_pages_json):
        from server import verify_story
        with patch('server.get_openrouter_client', return_value=mock_client):
            verify_story(sample_pages_json, "Girls can't do math")
            call_args = mock_client.chat.completions.create.call_args
            assert 'sonnet' in call_args.kwargs['model']


# ============================================================
# GENERATE ILLUSTRATION TOOL TESTS
# ============================================================

class TestGenerateIllustration:
    """Test generate_illustration MCP tool."""

    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client for DALL-E."""
        mock = MagicMock()
        response = MagicMock()
        response.data = [MagicMock()]
        response.data[0].url = "https://example.com/image.png"
        response.data[0].revised_prompt = "A warm watercolor illustration..."
        mock.images.generate.return_value = response
        return mock

    def test_returns_json_string(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            result = generate_illustration(
                scene_description="A child in a classroom",
                character_description="A 6-year-old girl",
                page_number=1
            )
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    def test_returns_url(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            result = json.loads(generate_illustration(
                scene_description="A child in a classroom",
                page_number=1
            ))
            assert "url" in result
            assert result["url"] is not None

    def test_returns_page_number(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            result = json.loads(generate_illustration(
                scene_description="A child in a classroom",
                page_number=3
            ))
            assert result["page_number"] == 3

    def test_returns_status_success(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            result = json.loads(generate_illustration(
                scene_description="A child in a classroom",
                page_number=1
            ))
            assert result["status"] == "success"

    def test_handles_dalle_error(self):
        from server import generate_illustration
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("DALL-E error")
        with patch('server.get_openai_client', return_value=mock_client):
            result = json.loads(generate_illustration(
                scene_description="A child in a classroom",
                page_number=1
            ))
            assert result["url"] is None
            assert result["status"] == "failed"
            assert "error" in result

    def test_uses_dalle3_model(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            generate_illustration(
                scene_description="A child in a classroom",
                page_number=1
            )
            call_args = mock_client.images.generate.call_args
            assert call_args.kwargs['model'] == 'dall-e-3'

    def test_uses_1024x1024_size(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            generate_illustration(
                scene_description="A child in a classroom",
                page_number=1
            )
            call_args = mock_client.images.generate.call_args
            assert call_args.kwargs['size'] == '1024x1024'

    def test_character_description_included_in_prompt(self, mock_client):
        from server import generate_illustration
        with patch('server.get_openai_client', return_value=mock_client):
            generate_illustration(
                scene_description="A child in a classroom",
                character_description="A 6-year-old girl with curly hair",
                page_number=1
            )
            call_args = mock_client.images.generate.call_args
            prompt = call_args.kwargs['prompt']
            assert "curly hair" in prompt


# ============================================================
# KNOWLEDGE BASE TESTS
# ============================================================

class TestKnowledgeBase:
    """Test knowledge base loading and structure."""

    def test_knowledge_base_loaded(self):
        from server import KNOWLEDGE_BASE
        assert KNOWLEDGE_BASE is not None
        assert "women" in KNOWLEDGE_BASE
        assert "stereotype_categories" in KNOWLEDGE_BASE

    def test_has_women(self):
        from server import KNOWLEDGE_BASE
        assert len(KNOWLEDGE_BASE["women"]) > 0

    def test_has_categories(self):
        from server import KNOWLEDGE_BASE
        assert len(KNOWLEDGE_BASE["stereotype_categories"]) > 0

    def test_women_have_required_fields(self):
        from server import KNOWLEDGE_BASE
        for woman in KNOWLEDGE_BASE["women"]:
            assert "name" in woman
            assert "era" in woman
            assert "achievement" in woman
            assert "fairy_tale_moment" in woman
            assert "age_adaptations" in woman
            assert "counters_stereotypes" in woman

    def test_categories_have_required_fields(self):
        from server import KNOWLEDGE_BASE
        for category, data in KNOWLEDGE_BASE["stereotype_categories"].items():
            assert "counter_message" in data
            assert "suggested_women" in data

    def test_age_adaptations_have_all_groups(self):
        from server import KNOWLEDGE_BASE
        for woman in KNOWLEDGE_BASE["women"]:
            adaptations = woman["age_adaptations"]
            assert "young" in adaptations
            assert "middle" in adaptations
            assert "older" in adaptations
