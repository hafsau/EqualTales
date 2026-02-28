"""
Integration tests for EqualTales full pipeline.

These tests verify the complete story generation flow works end-to-end.
They can be run with real APIs (for pre-deployment verification) or
with mocks (for CI/CD pipelines).

Run with real APIs:
    INTEGRATION_TEST=true pytest tests/test_integration.py -v

Run with mocks (default):
    pytest tests/test_integration.py -v
"""

import json
import os
import sys
import time
from unittest.mock import patch, MagicMock

import pytest

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if we should use real APIs
USE_REAL_APIS = os.getenv("INTEGRATION_TEST", "false").lower() == "true"


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def client():
    """Flask test client."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_full_pipeline():
    """Mock the entire MCP tool pipeline for integration testing."""
    mock_tools = {
        "classify": MagicMock(return_value=json.dumps({
            "primary_category": "girls_cant_do_math",
            "secondary_categories": ["science_is_for_boys"],
            "stereotype_essence": "Girls are not suited for mathematical thinking",
            "age_strategy": {
                "young": "Use simple counting and shapes",
                "middle": "Connect math to everyday activities",
                "older": "Discuss real achievements in mathematics"
            },
            "emotional_tone": "limiting"
        })),
        "match": MagicMock(return_value=json.dumps({
            "woman": {
                "name": "Katherine Johnson",
                "era": "1918-2020",
                "category": "math",
                "achievement": "NASA mathematician whose calculations were critical to the first US crewed spaceflights",
                "fairy_tale_moment": "When rockets needed to reach the stars, it was Katherine's brilliant calculations that showed them the way.",
                "age_adaptations": {
                    "young": "She counted the stars and helped rockets fly to space!",
                    "middle": "Her math helped astronauts travel safely through space.",
                    "older": "Her precise calculations were trusted over computers for the Mercury missions."
                },
                "counters_stereotypes": ["girls_cant_do_math", "science_is_for_boys"]
            },
            "counter_message": "Mathematics has no gender. Girls can excel at math just as much as boys.",
            "match_quality": "strong"
        })),
        "generate": MagicMock(return_value=json.dumps({
            "title": "Lily and the Stars",
            "pages": [
                {
                    "page_number": 1,
                    "page_title": "The Belief",
                    "text": "Lily loved looking at the stars. One day at school, a boy said, 'Math is too hard for girls.' Lily felt sad.",
                    "illustration_description": "A young child looking sadly at math homework while other children play in the background."
                },
                {
                    "page_number": 2,
                    "page_title": "The Question",
                    "text": "That night, Lily counted the stars. 'One, two, three...' she whispered. 'If math is hard for girls, how can I count so many stars?'",
                    "illustration_description": "A child at a window, counting stars with wonder, the night sky full of twinkling lights."
                },
                {
                    "page_number": 3,
                    "page_title": "The Discovery",
                    "text": "Lily's grandmother showed her a book about Katherine Johnson. 'She used math to send astronauts to the moon,' grandmother said.",
                    "illustration_description": "A grandmother and child looking at a book together, with images of rockets and space visible on the pages."
                },
                {
                    "page_number": 4,
                    "page_title": "The Inspiration",
                    "text": "Katherine Johnson was so good at math that NASA trusted her calculations more than their computers. Her numbers helped astronauts travel safely to space and back.",
                    "illustration_description": "A portrait-style scene of Katherine Johnson working at her desk, surrounded by mathematical equations and images of rockets."
                },
                {
                    "page_number": 5,
                    "page_title": "The New Belief",
                    "text": "The next day at school, Lily raised her hand. 'I want to learn more math,' she said with a big smile. 'Maybe I can help rockets fly too!'",
                    "illustration_description": "A confident child raising her hand in class, with a bright smile, mathematical symbols floating playfully around her."
                }
            ],
            "real_woman_name": "Katherine Johnson",
            "real_woman_achievement": "NASA mathematician whose calculations were critical to early space missions",
            "discussion_prompts": [
                "What made Lily change her mind about math?",
                "What would you like to count or measure?",
                "Can you think of other times when someone said you couldn't do something, but you did it anyway?"
            ],
            "activity_suggestion": "Count objects around your home and make a chart showing how many of each thing you found."
        })),
        "verify": MagicMock(return_value=json.dumps({
            "passed": True,
            "score": 9,
            "issues": [],
            "strengths": [
                "Story naturally counters the stereotype through example",
                "Katherine Johnson's achievement is presented age-appropriately",
                "Child protagonist shows agency and curiosity",
                "Ending is empowering without being preachy"
            ],
            "suggestion": None
        })),
        "illustrate": MagicMock(return_value=json.dumps({
            "url": "https://example.com/test-illustration.png",
            "page_number": 1,
            "revised_prompt": "A warm watercolor illustration of a child...",
            "status": "success"
        }))
    }
    return mock_tools


# ============================================================
# END-TO-END STREAMING TESTS
# ============================================================

class TestStreamingPipeline:
    """Test the complete SSE streaming pipeline."""

    def test_full_generation_flow(self, client, mock_full_pipeline):
        """Test complete story generation from stereotype to illustrated story."""
        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "My daughter thinks math is only for boys",
                    "child_name": "Lily",
                    "child_age": 6
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.data.decode('utf-8')

            # Verify all expected events are present
            assert '"type": "status"' in data
            assert '"type": "classification"' in data
            assert '"type": "real_woman"' in data
            assert '"type": "story"' in data
            assert '"type": "qa_result"' in data
            assert '"type": "illustration"' in data
            assert '"type": "complete"' in data

    def test_event_order(self, client, mock_full_pipeline):
        """Test that events are streamed in correct order."""
        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "Girls can't do math",
                    "child_name": "Emma",
                    "child_age": 7
                }),
                content_type='application/json')

            data = response.data.decode('utf-8')
            events = data.split('\n\n')

            # Parse events
            event_types = []
            for event in events:
                if event.startswith('data: '):
                    try:
                        parsed = json.loads(event[6:])
                        event_types.append(parsed.get('type'))
                    except json.JSONDecodeError:
                        pass

            # Classification should come before story
            if 'classification' in event_types and 'story' in event_types:
                assert event_types.index('classification') < event_types.index('story')

            # Story should come before complete
            if 'story' in event_types and 'complete' in event_types:
                assert event_types.index('story') < event_types.index('complete')

    def test_all_ages_generate_successfully(self, client, mock_full_pipeline):
        """Test story generation works for all age groups (3-10)."""
        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            for age in [3, 5, 6, 8, 9, 10]:
                response = client.post('/api/generate/stream',
                    data=json.dumps({
                        "stereotype": "Girls aren't good at sports",
                        "child_name": "TestChild",
                        "child_age": age
                    }),
                    content_type='application/json')

                assert response.status_code == 200
                data = response.data.decode('utf-8')
                assert '"type": "story"' in data

    def test_various_stereotypes(self, client, mock_full_pipeline):
        """Test that various stereotype inputs work."""
        stereotypes = [
            "Girls can't do math",
            "Science is only for boys",
            "Girls aren't strong enough",
            "Boys are better at sports",
            "Girls should be quiet",
            "Technology is for boys",
        ]

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            for stereotype in stereotypes:
                response = client.post('/api/generate/stream',
                    data=json.dumps({
                        "stereotype": stereotype,
                        "child_name": "TestChild",
                        "child_age": 6
                    }),
                    content_type='application/json')

                assert response.status_code == 200
                data = response.data.decode('utf-8')
                assert '"type": "story"' in data, f"Failed for stereotype: {stereotype}"


# ============================================================
# NON-STREAMING END-TO-END TESTS
# ============================================================

class TestNonStreamingPipeline:
    """Test the non-streaming /api/generate endpoint."""

    def test_full_generation_returns_all_fields(self, client, mock_full_pipeline):
        """Test that non-streaming endpoint returns complete response."""
        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate',
                data=json.dumps({
                    "stereotype": "Girls can't do math",
                    "child_name": "Maya",
                    "child_age": 8
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)

            # Verify all top-level fields
            assert 'story' in data
            assert 'illustrations' in data
            assert 'classification' in data
            assert 'real_woman' in data
            assert 'qa_result' in data
            assert 'metadata' in data

            # Verify story structure
            assert 'title' in data['story']
            assert 'pages' in data['story']
            assert len(data['story']['pages']) == 5

            # Verify metadata
            assert data['metadata']['child_name'] == 'Maya'
            assert data['metadata']['child_age'] == 8
            assert data['metadata']['age_group'] == 'middle'

    def test_parallel_execution_completes(self, client, mock_full_pipeline):
        """Test that parallel QA + illustration execution completes."""
        # Make illustrations take a bit of time to simulate real behavior
        def slow_illustrate(*args, **kwargs):
            time.sleep(0.01)  # Small delay
            return json.dumps({
                "url": "https://example.com/illustration.png",
                "page_number": kwargs.get('page_number', 1),
                "status": "success"
            })

        mock_full_pipeline['illustrate'] = MagicMock(side_effect=slow_illustrate)

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            start = time.time()
            response = client.post('/api/generate',
                data=json.dumps({
                    "stereotype": "Girls can't do math",
                    "child_name": "Test",
                    "child_age": 6
                }),
                content_type='application/json')
            elapsed = time.time() - start

            assert response.status_code == 200
            data = json.loads(response.data)

            # All 5 illustrations should be present
            assert len(data['illustrations']) == 5

            # QA should also have completed
            assert data['qa_result']['passed'] is True


# ============================================================
# ERROR RECOVERY TESTS
# ============================================================

class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_illustration_failure_doesnt_crash(self, client, mock_full_pipeline):
        """Test that a DALL-E failure doesn't crash the whole pipeline."""
        # Make first illustration fail, rest succeed
        call_count = [0]
        def flaky_illustrate(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("DALL-E rate limit")
            return json.dumps({
                "url": f"https://example.com/page{call_count[0]}.png",
                "page_number": kwargs.get('page_number', 1),
                "status": "success"
            })

        mock_full_pipeline['illustrate'] = MagicMock(side_effect=flaky_illustrate)

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "Test stereotype",
                    "child_name": "Test",
                    "child_age": 6
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.data.decode('utf-8')
            # Should still complete
            assert 'complete' in data

    def test_qa_failure_uses_safe_default(self, client, mock_full_pipeline):
        """Test that QA failure returns safe default."""
        mock_full_pipeline['verify'] = MagicMock(side_effect=Exception("QA service error"))

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "Test stereotype",
                    "child_name": "Test",
                    "child_age": 6
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.data.decode('utf-8')
            # Should still complete
            assert 'complete' in data
            # Should have QA result (safe default)
            assert 'qa_result' in data

    def test_classification_fallback(self, client, mock_full_pipeline):
        """Test that missing primary_category uses fallback."""
        mock_full_pipeline['classify'] = MagicMock(return_value=json.dumps({
            "secondary_categories": [],
            "stereotype_essence": "Test"
            # Missing primary_category
        }))

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "Some unusual stereotype",
                    "child_name": "Test",
                    "child_age": 6
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.data.decode('utf-8')
            # Should still work due to fallback
            assert 'story' in data or 'real_woman' in data

    def test_all_illustrations_fail_gracefully(self, client, mock_full_pipeline):
        """Test that if all illustrations fail, story still completes."""
        mock_full_pipeline['illustrate'] = MagicMock(side_effect=Exception("All DALL-E calls fail"))

        with patch('app.get_mcp_tools', return_value=mock_full_pipeline):
            response = client.post('/api/generate/stream',
                data=json.dumps({
                    "stereotype": "Test stereotype",
                    "child_name": "Test",
                    "child_age": 6
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.data.decode('utf-8')
            # Should still have story and complete
            assert '"type": "story"' in data
            assert '"type": "complete"' in data


# ============================================================
# REAL API INTEGRATION TESTS (only run with INTEGRATION_TEST=true)
# ============================================================

@pytest.mark.skipif(not USE_REAL_APIS, reason="Real API tests disabled")
class TestRealAPIIntegration:
    """Integration tests that use real APIs.

    These tests are skipped by default and only run when
    INTEGRATION_TEST=true is set in the environment.

    WARNING: These tests consume API credits!
    """

    def test_real_classification(self, client):
        """Test real Claude API classification."""
        response = client.post('/api/generate/stream',
            data=json.dumps({
                "stereotype": "My daughter thinks girls can't be good at math",
                "child_name": "TestChild",
                "child_age": 6
            }),
            content_type='application/json')

        # Just check that we get some response without errors
        # Full generation would be too expensive for regular testing
        data = response.data.decode('utf-8')
        # Should at least start the pipeline
        assert 'status' in data or 'classification' in data

    def test_health_with_real_kb(self, client):
        """Test health endpoint with real knowledge base."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify knowledge base is loaded
        assert data['knowledge_base']['women'] == 50
        assert data['knowledge_base']['categories'] == 14


# ============================================================
# PERFORMANCE TESTS
# ============================================================

class TestPerformance:
    """Performance and timing tests."""

    def test_validation_is_fast(self, client):
        """Test that input validation doesn't add significant latency."""
        start = time.time()
        for _ in range(10):
            client.post('/api/generate/stream',
                data=json.dumps({"stereotype": "", "child_name": "Test", "child_age": 6}),
                content_type='application/json')
        elapsed = time.time() - start

        # 10 validation requests should complete in under 1 second
        assert elapsed < 1.0

    def test_static_endpoints_are_fast(self, client):
        """Test that static endpoints respond quickly."""
        endpoints = ['/api/health', '/api/examples', '/api/women', '/api/categories']

        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            elapsed = time.time() - start

            assert response.status_code == 200
            assert elapsed < 0.1, f"{endpoint} took too long: {elapsed}s"
