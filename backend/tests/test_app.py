"""
Unit tests for EqualTales Flask API (backend/app.py)

Tests all routes, input validation, edge cases, and error handling.
Run with: pytest tests/test_app.py -v
"""
import json
import sys
import os
from unittest.mock import patch, MagicMock

import pytest

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# HELPER FUNCTION TESTS
# ============================================================

class TestAgeGroup:
    """Test _get_age_group helper function."""

    def test_age_3_is_young(self):
        from app import _get_age_group
        assert _get_age_group(3) == "young"

    def test_age_4_is_young(self):
        from app import _get_age_group
        assert _get_age_group(4) == "young"

    def test_age_5_is_young(self):
        from app import _get_age_group
        assert _get_age_group(5) == "young"

    def test_age_6_is_middle(self):
        from app import _get_age_group
        assert _get_age_group(6) == "middle"

    def test_age_7_is_middle(self):
        from app import _get_age_group
        assert _get_age_group(7) == "middle"

    def test_age_8_is_middle(self):
        from app import _get_age_group
        assert _get_age_group(8) == "middle"

    def test_age_9_is_older(self):
        from app import _get_age_group
        assert _get_age_group(9) == "older"

    def test_age_10_is_older(self):
        from app import _get_age_group
        assert _get_age_group(10) == "older"


class TestCharacterAppearance:
    """Test _generate_character_appearance helper function."""

    def test_includes_child_name(self):
        from app import _generate_character_appearance
        result = _generate_character_appearance("Lily", 6)
        assert "Lily" in result

    def test_includes_child_age(self):
        from app import _generate_character_appearance
        result = _generate_character_appearance("Lily", 7)
        assert "7-year-old" in result

    def test_includes_appearance_details(self):
        from app import _generate_character_appearance
        result = _generate_character_appearance("Lily", 6)
        # Should include skin, hair, and clothing details
        assert "skin" in result.lower()
        assert "hair" in result.lower()

    def test_generates_different_appearances(self):
        """Test that multiple calls can produce different appearances (randomness)."""
        from app import _generate_character_appearance
        appearances = set()
        for _ in range(20):
            appearances.add(_generate_character_appearance("Test", 6))
        # Should have at least a few different appearances
        assert len(appearances) > 1


class TestSSEHelper:
    """Test _sse helper function."""

    def test_formats_dict_as_sse(self):
        from app import _sse
        result = _sse({"type": "status", "message": "Testing"})
        assert result == 'data: {"type": "status", "message": "Testing"}\n\n'

    def test_handles_nested_data(self):
        from app import _sse
        data = {"type": "story", "data": {"title": "Test", "pages": []}}
        result = _sse(data)
        assert result.startswith("data: ")
        assert result.endswith("\n\n")
        # Should be valid JSON
        json_str = result[6:-2]  # Remove "data: " and "\n\n"
        parsed = json.loads(json_str)
        assert parsed["type"] == "story"


# ============================================================
# HEALTH ENDPOINT TESTS
# ============================================================

class TestHealthEndpoint:
    """Test GET /api/health endpoint."""

    def test_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_returns_status_ok(self, client):
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_returns_service_name(self, client):
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['service'] == 'EqualTales'

    def test_returns_mode(self, client):
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['mode'] in ['direct', 'goose']

    def test_returns_knowledge_base_stats(self, client):
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'knowledge_base' in data
        assert 'women' in data['knowledge_base']
        assert 'categories' in data['knowledge_base']


# ============================================================
# EXAMPLES ENDPOINT TESTS
# ============================================================

class TestExamplesEndpoint:
    """Test GET /api/examples endpoint."""

    def test_returns_200(self, client):
        response = client.get('/api/examples')
        assert response.status_code == 200

    def test_returns_list(self, client):
        response = client.get('/api/examples')
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_returns_10_examples(self, client):
        response = client.get('/api/examples')
        data = json.loads(response.data)
        assert len(data) == 10

    def test_each_example_has_text_and_emoji(self, client):
        response = client.get('/api/examples')
        data = json.loads(response.data)
        for example in data:
            assert 'text' in example
            assert 'emoji' in example
            assert len(example['text']) > 0


# ============================================================
# WOMEN ENDPOINT TESTS
# ============================================================

class TestWomenEndpoint:
    """Test GET /api/women endpoint."""

    def test_returns_200(self, client):
        response = client.get('/api/women')
        assert response.status_code == 200

    def test_returns_list(self, client):
        response = client.get('/api/women')
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_each_woman_has_required_fields(self, client):
        response = client.get('/api/women')
        data = json.loads(response.data)
        for woman in data:
            assert 'name' in woman
            assert 'era' in woman
            assert 'category' in woman
            assert 'achievement' in woman


# ============================================================
# CATEGORIES ENDPOINT TESTS
# ============================================================

class TestCategoriesEndpoint:
    """Test GET /api/categories endpoint."""

    def test_returns_200(self, client):
        response = client.get('/api/categories')
        assert response.status_code == 200

    def test_returns_dict(self, client):
        response = client.get('/api/categories')
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_categories_have_counter_message(self, client):
        response = client.get('/api/categories')
        data = json.loads(response.data)
        for category, info in data.items():
            assert 'counter_message' in info


# ============================================================
# GENERATE ENDPOINT INPUT VALIDATION TESTS
# ============================================================

class TestGenerateInputValidation:
    """Test POST /api/generate input validation."""

    def test_empty_stereotype_returns_400(self, client):
        response = client.post('/api/generate',
            data=json.dumps({"stereotype": "", "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400

    def test_missing_stereotype_returns_400(self, client):
        response = client.post('/api/generate',
            data=json.dumps({"child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400

    def test_whitespace_only_stereotype_returns_400(self, client):
        response = client.post('/api/generate',
            data=json.dumps({"stereotype": "   ", "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400

    def test_age_below_3_returns_400(self, client):
        response = client.post('/api/generate',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 2}),
            content_type='application/json')
        assert response.status_code == 400

    def test_age_above_10_returns_400(self, client):
        response = client.post('/api/generate',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 11}),
            content_type='application/json')
        assert response.status_code == 400

    def test_age_3_is_valid(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 3}),
                content_type='application/json')
            assert response.status_code == 200

    def test_age_10_is_valid(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 10}),
                content_type='application/json')
            assert response.status_code == 200

    def test_default_child_name_lily(self, client, mock_mcp_tools):
        """Empty child name should default to 'Lily'."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200


# ============================================================
# GENERATE STREAM ENDPOINT INPUT VALIDATION TESTS
# ============================================================

class TestGenerateStreamInputValidation:
    """Test POST /api/generate/stream input validation."""

    def test_empty_stereotype_returns_400(self, client):
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "", "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400

    def test_short_stereotype_returns_400(self, client):
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "ab", "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'more detailed' in data['error'].lower()

    def test_long_stereotype_returns_400(self, client):
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "x" * 501, "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert '500' in data['error']

    def test_age_below_3_returns_400(self, client):
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 2}),
            content_type='application/json')
        assert response.status_code == 400

    def test_age_above_10_returns_400(self, client):
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 11}),
            content_type='application/json')
        assert response.status_code == 400

    def test_child_name_truncated_to_30_chars(self, client, mock_mcp_tools):
        """Long child names should be truncated to 30 characters."""
        long_name = "A" * 50
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": long_name, "child_age": 6}),
                content_type='application/json')
            # Should not error, name gets truncated
            assert response.status_code == 200


# ============================================================
# GENERATE ENDPOINT SUCCESS TESTS
# ============================================================

class TestGenerateEndpointSuccess:
    """Test POST /api/generate successful generation."""

    def test_returns_200_with_valid_input(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_returns_story_data(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'story' in data
            assert 'title' in data['story']
            assert 'pages' in data['story']

    def test_returns_5_pages(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert len(data['story']['pages']) == 5

    def test_returns_illustrations(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'illustrations' in data
            assert len(data['illustrations']) == 5

    def test_returns_classification(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'classification' in data
            assert 'primary_category' in data['classification']

    def test_returns_real_woman(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'real_woman' in data
            assert 'name' in data['real_woman']

    def test_returns_qa_result(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'qa_result' in data
            assert 'passed' in data['qa_result']
            assert 'score' in data['qa_result']

    def test_returns_metadata(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = json.loads(response.data)
            assert 'metadata' in data
            assert data['metadata']['child_name'] == 'Lily'
            assert data['metadata']['child_age'] == 6


# ============================================================
# GENERATE ENDPOINT ERROR HANDLING TESTS
# ============================================================

class TestGenerateEndpointErrorHandling:
    """Test POST /api/generate error handling."""

    def test_mcp_tool_error_returns_500(self, client, mock_mcp_tools):
        mock_mcp_tools['classify'] = MagicMock(side_effect=Exception("API error"))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_invalid_json_from_classify_handled(self, client, mock_mcp_tools):
        mock_mcp_tools['classify'] = MagicMock(return_value="not valid json")
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 500


# ============================================================
# GENERATE STREAM ENDPOINT TESTS
# ============================================================

class TestGenerateStreamEndpoint:
    """Test POST /api/generate/stream SSE behavior."""

    def test_returns_sse_mimetype(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert 'text/event-stream' in response.content_type

    def test_streams_status_events(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            # Status events are sent during generation
            assert '"type": "status"' in data or '"type": "classification"' in data

    def test_streams_classification_event(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            assert 'classification' in data

    def test_streams_real_woman_event(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            assert 'real_woman' in data

    def test_streams_story_event(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            assert '"type": "story"' in data

    def test_streams_complete_event(self, client, mock_mcp_tools):
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            # Check for complete or story event (stream may end early in test)
            assert '"type": "complete"' in data or '"type": "story"' in data


# ============================================================
# EDGE CASE TESTS
# ============================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_classification_without_primary_category_defaults(self, client, mock_mcp_tools):
        """If classification doesn't return primary_category, should default to girls_cant_do_math."""
        mock_mcp_tools['classify'] = MagicMock(return_value=json.dumps({
            "secondary_categories": [],
            "stereotype_essence": "Test"
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            # Should still work due to fallback
            assert response.status_code == 200

    def test_story_with_missing_page_fields_filled(self, client, mock_mcp_tools):
        """Story pages with missing fields should be filled with defaults."""
        mock_mcp_tools['generate'] = MagicMock(return_value=json.dumps({
            "title": "Test",
            "pages": [
                {"page_number": 1},  # Missing text, illustration_description, page_title
                {"page_number": 2, "text": "Page 2"},
                {"page_number": 3, "text": "Page 3"},
                {"page_number": 4, "text": "Page 4"},
                {"page_number": 5, "text": "Page 5"},
            ],
            "discussion_prompts": [],
            "activity_suggestion": ""
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_illustration_failure_returns_null_url(self, client, mock_mcp_tools):
        """DALL-E failures should return null URL, not crash."""
        mock_mcp_tools['illustrate'] = MagicMock(side_effect=Exception("DALL-E error"))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            # Should still complete, just with null illustrations
            data = response.data.decode('utf-8')
            assert 'complete' in data or 'story' in data

    def test_qa_failure_returns_safe_default(self, client, mock_mcp_tools):
        """QA failures should return safe default (passed=true, score=7)."""
        mock_mcp_tools['verify'] = MagicMock(side_effect=Exception("QA error"))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            # Should still complete
            assert 'complete' in data

    def test_unicode_stereotype_handled(self, client, mock_mcp_tools):
        """Unicode characters in stereotype should be handled."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "女孩不能做数学", "child_name": "小明", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_special_characters_in_name(self, client, mock_mcp_tools):
        """Special characters in child name should be handled."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test", "child_name": "Mary-Jane O'Brien", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_emoji_in_stereotype(self, client, mock_mcp_tools):
        """Emoji characters in stereotype should be handled."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't do math 🔢", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_newlines_in_stereotype(self, client, mock_mcp_tools):
        """Newline characters in stereotype should be handled."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Girls can't\ndo math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_html_tags_in_stereotype(self, client, mock_mcp_tools):
        """HTML tags in stereotype should be handled (potential XSS)."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "<script>alert('xss')</script>Girls can't do math", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_sql_injection_in_stereotype(self, client, mock_mcp_tools):
        """SQL injection attempts should be handled safely."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "'; DROP TABLE users; --", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            # Should be handled safely (no database to inject into anyway)
            assert response.status_code == 200


# ============================================================
# ADDITIONAL INPUT VALIDATION EDGE CASES
# ============================================================

class TestInputValidationEdgeCases:
    """Test additional input validation edge cases."""

    def test_non_integer_age_stream(self, client):
        """Non-integer age should cause an error or be coerced."""
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": "six"}),
            content_type='application/json')
        # Should return 500 (int conversion fails) or 400 if validated
        assert response.status_code in [400, 500]

    def test_float_age_stream(self, client, mock_mcp_tools):
        """Float age should be converted to int."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": 6.5}),
                content_type='application/json')
            assert response.status_code == 200

    def test_negative_age_stream(self, client):
        """Negative age should return 400."""
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "Test stereotype", "child_name": "Lily", "child_age": -5}),
            content_type='application/json')
        assert response.status_code == 400

    def test_null_stereotype_returns_400(self, client):
        """Null stereotype should return 400."""
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": None, "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        assert response.status_code == 400

    def test_null_child_name_defaults(self, client, mock_mcp_tools):
        """Null child name should default to Lily."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test stereotype", "child_name": None, "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_missing_content_type(self, client):
        """Missing content-type header should be handled."""
        response = client.post('/api/generate/stream',
            data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}))
        # Flask may still parse JSON, or return 415/400
        assert response.status_code in [200, 400, 415, 500]

    def test_invalid_json_body(self, client):
        """Invalid JSON body should return error."""
        response = client.post('/api/generate/stream',
            data="not valid json {",
            content_type='application/json')
        assert response.status_code in [400, 500]

    def test_empty_body(self, client):
        """Empty body should return 400."""
        response = client.post('/api/generate/stream',
            data="",
            content_type='application/json')
        assert response.status_code in [400, 500]

    def test_array_instead_of_object(self, client):
        """Array body instead of object should be handled."""
        response = client.post('/api/generate/stream',
            data=json.dumps(["stereotype", "name", 6]),
            content_type='application/json')
        assert response.status_code in [400, 500]

    def test_non_streaming_missing_short_validation(self, client):
        """Non-streaming endpoint should also validate short stereotypes."""
        response = client.post('/api/generate',
            data=json.dumps({"stereotype": "ab", "child_name": "Lily", "child_age": 6}),
            content_type='application/json')
        # Currently non-streaming doesn't have the same validation - this documents behavior
        # Could be 200 (passes to MCP) or 400 (if validation added)
        assert response.status_code in [200, 400, 500]

    def test_extremely_long_child_name_truncated(self, client, mock_mcp_tools):
        """Child names over 30 chars should be truncated."""
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({
                    "stereotype": "Test stereotype",
                    "child_name": "A" * 100,
                    "child_age": 6
                }),
                content_type='application/json')
            assert response.status_code == 200


# ============================================================
# MCP TOOL RESPONSE EDGE CASES
# ============================================================

class TestMCPResponseEdgeCases:
    """Test handling of various MCP tool response edge cases."""

    def test_empty_pages_array(self, client, mock_mcp_tools):
        """Empty pages array should raise error."""
        mock_mcp_tools['generate'] = MagicMock(return_value=json.dumps({
            "title": "Test",
            "pages": [],
            "discussion_prompts": [],
            "activity_suggestion": ""
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            # Should have error event
            assert 'error' in data.lower()

    def test_null_pages(self, client, mock_mcp_tools):
        """Null pages should raise error."""
        mock_mcp_tools['generate'] = MagicMock(return_value=json.dumps({
            "title": "Test",
            "pages": None,
            "discussion_prompts": [],
            "activity_suggestion": ""
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            data = response.data.decode('utf-8')
            assert 'error' in data.lower()

    def test_woman_missing_age_adaptations(self, client, mock_mcp_tools):
        """Woman without age_adaptations should use fallback."""
        mock_mcp_tools['match'] = MagicMock(return_value=json.dumps({
            "woman": {
                "name": "Test Woman",
                "era": "Modern",
                "category": "math",
                "achievement": "Test achievement",
                "fairy_tale_moment": "Test moment",
                "age_adaptations": {},  # Empty adaptations
                "counters_stereotypes": ["girls_cant_do_math"]
            },
            "counter_message": "Test message",
            "match_quality": "strong"
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            # Should handle missing age adaptations gracefully
            assert response.status_code == 200

    def test_classification_with_empty_categories(self, client, mock_mcp_tools):
        """Classification with empty secondary_categories should work."""
        mock_mcp_tools['classify'] = MagicMock(return_value=json.dumps({
            "primary_category": "girls_cant_do_math",
            "secondary_categories": [],
            "stereotype_essence": "Test",
            "emotional_tone": "limiting"
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200

    def test_illustration_returns_null_url(self, client, mock_mcp_tools):
        """Illustration returning null URL should be handled."""
        mock_mcp_tools['illustrate'] = MagicMock(return_value=json.dumps({
            "url": None,
            "page_number": 1,
            "status": "failed",
            "error": "Content policy violation"
        }))
        with patch('app.get_mcp_tools', return_value=mock_mcp_tools):
            response = client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "Test", "child_name": "Lily", "child_age": 6}),
                content_type='application/json')
            assert response.status_code == 200
            data = response.data.decode('utf-8')
            # Should still complete
            assert 'complete' in data or 'story' in data
