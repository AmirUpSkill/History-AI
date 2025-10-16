"""
Test suite for AI Service

Tests cover:
- Card generation with various inputs
- Copilot answer generation
- Bias judgment analysis
- Error handling and edge cases
- Mocking of external dependencies (Gemini API)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService, AIServiceError
from app.utils import (
    ResponseParseError,
    CardValidationError,
    BiasValidationError,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_api_key():
    """Provide a mock Gemini API key."""
    return "test_api_key_12345"


@pytest.fixture
def ai_service_with_mock(mock_api_key):
    """Create an AIService instance with mocked GeminiClient."""
    with patch("app.services.ai_service.GeminiClient"):
        service = AIService(mock_api_key)
        service.gemini_client = Mock()
        return service


@pytest.fixture
def valid_card_response():
    """Provide a valid card generation response from Gemini."""
    return """{
    "title": "The Arab Spring",
    "description": "# The Arab Spring\\n\\nA series of anti-government protests and uprisings that spread across the Arab world in the early 2010s.",
    "keywords": ["Uprising", "Protest", "Democracy", "Tunisia", "Egypt"]
}"""


@pytest.fixture
def valid_copilot_response():
    """Provide a valid copilot response."""
    return "The Arab Spring was a series of pro-democracy uprisings and armed rebellions that spread across much of the Arab world in early 2011."


@pytest.fixture
def valid_bias_response():
    """Provide a valid bias judge response."""
    return """{
    "bias_score": 35.5,
    "explanation": "The text demonstrates mostly neutral language with minor subjective framing in the description of political motivations."
}"""


@pytest.fixture
def malformed_json_response():
    """Provide a malformed JSON response."""
    return "{invalid json content"


@pytest.fixture
def missing_fields_response():
    """Provide a response missing required fields."""
    return '{"title": "Test Event"}'


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================

class TestAIServiceInitialization:
    """Test AIService initialization."""

    def test_successful_initialization(self, mock_api_key):
        """Test successful AIService initialization."""
        with patch("app.services.ai_service.GeminiClient") as mock_client:
            service = AIService(mock_api_key)
            assert service.gemini_client is not None
            mock_client.assert_called_once_with(mock_api_key)

    def test_initialization_with_missing_api_key(self):
        """Test initialization fails when API key is missing."""
        with patch("app.services.ai_service.GeminiClient") as mock_client:
            mock_client.side_effect = Exception("GEMINI_API_KEY is not set")
            with pytest.raises(AIServiceError):
                AIService(None)

    def test_initialization_with_invalid_api_key(self):
        """Test initialization with invalid API key."""
        with patch("app.services.ai_service.GeminiClient") as mock_client:
            mock_client.side_effect = Exception("Invalid API key")
            with pytest.raises(AIServiceError):
                AIService("invalid_key")


# =============================================================================
# CARD GENERATION TESTS
# =============================================================================

class TestCardGeneration:
    """Test card generation functionality."""

    def test_generate_card_success(self, ai_service_with_mock, valid_card_response):
        """Test successful card generation."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            valid_card_response
        )

        result = ai_service_with_mock.generate_card(
            title="The Arab Spring",
            system_prompt="Focus on political aspects",
            topics_to_cover="Causes, timeline, outcomes",
        )

        assert result["title"] == "The Arab Spring"
        assert "keywords" in result
        assert len(result["keywords"]) > 0
        assert isinstance(result["description"], str)

    def test_generate_card_with_context(self, ai_service_with_mock, valid_card_response):
        """Test card generation with PDF context."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            valid_card_response
        )

        context = "This is extracted PDF context about the Arab Spring"
        result = ai_service_with_mock.generate_card(
            title="The Arab Spring",
            system_prompt="Focus on political aspects",
            topics_to_cover="Causes, timeline, outcomes",
            context_text=context,
        )

        assert result is not None
        assert "title" in result

    def test_generate_card_with_malformed_json(
        self, ai_service_with_mock, malformed_json_response
    ):
        """Test card generation fails with malformed JSON response."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            malformed_json_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card(
                title="The Arab Spring",
                system_prompt="Focus on political aspects",
                topics_to_cover="Causes, timeline, outcomes",
            )

    def test_generate_card_with_missing_fields(
        self, ai_service_with_mock, missing_fields_response
    ):
        """Test card generation fails when required fields are missing."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            missing_fields_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card(
                title="The Arab Spring",
                system_prompt="Focus on political aspects",
                topics_to_cover="Causes, timeline, outcomes",
            )

    def test_generate_card_with_api_failure(self, ai_service_with_mock):
        """Test card generation when Gemini API fails."""
        ai_service_with_mock.gemini_client.call_with_retry.side_effect = Exception(
            "Gemini API error"
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card(
                title="The Arab Spring",
                system_prompt="Focus on political aspects",
                topics_to_cover="Causes, timeline, outcomes",
            )

    def test_generate_card_empty_keywords(self, ai_service_with_mock):
        """Test card generation fails with empty keywords list."""
        invalid_response = """{
        "title": "Test Event",
        "description": "Test description",
        "keywords": []
    }"""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            invalid_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card(
                title="Test Event",
                system_prompt="Test prompt",
                topics_to_cover="Test topics",
            )

    def test_generate_card_short_description(self, ai_service_with_mock):
        """Test card generation fails with description too short."""
        invalid_response = """{
        "title": "Test Event",
        "description": "Too short",
        "keywords": ["keyword1"]
    }"""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            invalid_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card(
                title="Test Event",
                system_prompt="Test prompt",
                topics_to_cover="Test topics",
            )


# =============================================================================
# COPILOT TESTS
# =============================================================================

class TestCopilotAnswer:
    """Test copilot answer generation."""

    def test_copilot_answer_success(
        self, ai_service_with_mock, valid_copilot_response
    ):
        """Test successful copilot answer generation."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            valid_copilot_response
        )

        question = "What was the Arab Spring?"
        context = "# The Arab Spring\n\nA series of anti-government protests..."

        result = ai_service_with_mock.copilot_answer(question, context)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Arab Spring" in result

    def test_copilot_answer_with_whitespace(self, ai_service_with_mock):
        """Test copilot answer strips whitespace."""
        response_with_whitespace = "   Answer with leading and trailing spaces   "
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            response_with_whitespace
        )

        result = ai_service_with_mock.copilot_answer(
            "Test question", "Test context"
        )

        assert result == "Answer with leading and trailing spaces"

    def test_copilot_answer_missing_question(self, ai_service_with_mock):
        """Test copilot fails when question is missing."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.copilot_answer("", "Some context")

    def test_copilot_answer_missing_context(self, ai_service_with_mock):
        """Test copilot fails when context is missing."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.copilot_answer("Some question", "")

    def test_copilot_answer_both_missing(self, ai_service_with_mock):
        """Test copilot fails when both question and context are missing."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.copilot_answer("", "")

    def test_copilot_answer_api_failure(self, ai_service_with_mock):
        """Test copilot fails when API returns error."""
        ai_service_with_mock.gemini_client.call_with_retry.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.copilot_answer(
                "What is this?", "Some context text"
            )

    def test_copilot_answer_none_values(self, ai_service_with_mock):
        """Test copilot fails with None values."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.copilot_answer(None, None)


# =============================================================================
# BIAS JUDGMENT TESTS
# =============================================================================

class TestBiasJudgment:
    """Test bias judgment functionality."""

    def test_judge_bias_success(self, ai_service_with_mock, valid_bias_response):
        """Test successful bias judgment."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            valid_bias_response
        )

        content = "The glorious Arab Spring uprising against imperial oppression was a righteous revolution." * 2

        bias_score, explanation = ai_service_with_mock.judge_bias(content)

        assert isinstance(bias_score, float)
        assert 0.0 <= bias_score <= 100.0
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    def test_judge_bias_low_bias(self, ai_service_with_mock):
        """Test bias judgment with neutral content returns low score."""
        neutral_response = """{
        "bias_score": 15.0,
        "explanation": "The text maintains a neutral, factual tone with minimal subjective language."
    }"""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            neutral_response
        )

        content = "Historical events description." * 10

        bias_score, _ = ai_service_with_mock.judge_bias(content)

        assert bias_score < 20

    def test_judge_bias_high_bias(self, ai_service_with_mock):
        """Test bias judgment with biased content returns high score."""
        biased_response = """{
        "bias_score": 85.5,
        "explanation": "The content uses highly charged language and presents only one perspective."
    }"""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            biased_response
        )

        content = "This is an extremely biased analysis." * 10

        bias_score, _ = ai_service_with_mock.judge_bias(content)

        assert bias_score > 80

    def test_judge_bias_score_boundaries(self, ai_service_with_mock):
        """Test bias judgment with boundary values."""
        # Test score = 0
        response_zero = '{"bias_score": 0.0, "explanation": "Perfectly neutral content."}'
        ai_service_with_mock.gemini_client.call_with_retry.return_value = response_zero

        bias_score, _ = ai_service_with_mock.judge_bias("Content." * 10)
        assert bias_score == 0.0

        # Test score = 100
        response_hundred = '{"bias_score": 100.0, "explanation": "Extremely biased content."}'
        ai_service_with_mock.gemini_client.call_with_retry.return_value = response_hundred

        bias_score, _ = ai_service_with_mock.judge_bias("Content." * 10)
        assert bias_score == 100.0

    def test_judge_bias_short_content(self, ai_service_with_mock):
        """Test bias judgment fails with too short content."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Too short")

    def test_judge_bias_empty_content(self, ai_service_with_mock):
        """Test bias judgment fails with empty content."""
        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("")

    def test_judge_bias_malformed_json(
        self, ai_service_with_mock, malformed_json_response
    ):
        """Test bias judgment fails with malformed JSON."""
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            malformed_json_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Valid content." * 10)

    def test_judge_bias_missing_score(self, ai_service_with_mock):
        """Test bias judgment fails when score is missing."""
        invalid_response = '{"explanation": "Missing score field"}'
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            invalid_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Valid content." * 10)

    def test_judge_bias_missing_explanation(self, ai_service_with_mock):
        """Test bias judgment fails when explanation is missing."""
        invalid_response = '{"bias_score": 50.0}'
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            invalid_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Valid content." * 10)

    def test_judge_bias_out_of_range_score(self, ai_service_with_mock):
        """Test bias judgment fails when score is out of range."""
        invalid_response = '{"bias_score": 150.0, "explanation": "Invalid score"}'
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            invalid_response
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Valid content." * 10)

    def test_judge_bias_api_failure(self, ai_service_with_mock):
        """Test bias judgment fails when API returns error."""
        ai_service_with_mock.gemini_client.call_with_retry.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(AIServiceError):
            ai_service_with_mock.judge_bias("Valid content." * 10)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestAIServiceIntegration:
    """Integration tests for the full AI Service workflow."""

    def test_full_workflow_card_to_copilot_to_bias(self, ai_service_with_mock):
        """Test complete workflow: generate card -> ask copilot -> judge bias."""
        card_response = """{
        "title": "Test Event",
        "description": "A detailed markdown description of the test event.",
        "keywords": ["test", "event"]
    }"""
        copilot_response = "This is the answer to your question."
        bias_response = '{"bias_score": 35.0, "explanation": "Mostly neutral content."}'

        ai_service_with_mock.gemini_client.call_with_retry.side_effect = [
            card_response,
            copilot_response,
            bias_response,
        ]

        # Generate card
        card = ai_service_with_mock.generate_card(
            title="Test Event",
            system_prompt="Test prompt",
            topics_to_cover="Topics",
        )
        assert card["title"] == "Test Event"

        # Ask copilot
        answer = ai_service_with_mock.copilot_answer(
            "What is this event?", card["description"]
        )
        assert answer == "This is the answer to your question."

        # Judge bias
        score, explanation = ai_service_with_mock.judge_bias(card["description"])
        assert score == 35.0
        assert "neutral" in explanation.lower()

    def test_error_recovery_scenarios(self, ai_service_with_mock):
        """Test that service can recover from individual operation failures."""
        # First operation fails
        ai_service_with_mock.gemini_client.call_with_retry.side_effect = Exception(
            "Error"
        )
        with pytest.raises(AIServiceError):
            ai_service_with_mock.generate_card("Title", "Prompt", "Topics")

        # Service still works for next operation
        valid_response = "This is a valid answer."
        ai_service_with_mock.gemini_client.call_with_retry.side_effect = None
        ai_service_with_mock.gemini_client.call_with_retry.return_value = (
            valid_response
        )

        answer = ai_service_with_mock.copilot_answer("Question", "Context")
        assert answer == "This is a valid answer."
