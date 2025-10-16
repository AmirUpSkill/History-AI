"""
test_card_service.py

Comprehensive unit tests for the CardService class.

Tests cover:
- get_cards() with and without filtering
- get_card() success and not found scenarios
- create_card_from_ai() with various scenarios
- Error handling and exception propagation
- PDF parsing integration
- AI service integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID
from typing import List

from app.services.card_service import (
    CardService,
    CardServiceError,
    CardNotFoundError,
    AIGenerationError,
    PDFParsingError,
)
from app.services.ai_service import AIService, AIServiceError
from app.db.models import Card
from app.schemas.card import CardResponse, CardBase
from app.schemas.ai import CopilotResponse, BiasJudgeResponse


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def mock_ai_service():
    """Create a mock AIService."""
    return Mock(spec=AIService)


@pytest.fixture
def card_service(mock_ai_service):
    """Create a CardService instance with mocked AI service."""
    return CardService(ai_service=mock_ai_service)


@pytest.fixture
def sample_card():
    """Create a sample Card database model."""
    card = Card()
    card.id = uuid4()
    card.title = "The Six-Day War (1967)"
    card.description = "# The Six-Day War\n\nA brief but decisive conflict..."
    card.keywords = ["Conflict", "Israel", "Egypt", "Syria", "Jordan"]
    return card


@pytest.fixture
def sample_cards_list(sample_card):
    """Create a list of sample cards."""
    card2 = Card()
    card2.id = uuid4()
    card2.title = "The Arab Spring"
    card2.description = "# The Arab Spring\n\nA series of protests..."
    card2.keywords = ["Uprising", "Protest", "Democracy", "Tunisia", "Egypt"]
    
    return [sample_card, card2]


@pytest.fixture
def sample_ai_response():
    """Sample AI generation response."""
    return {
        "title": "The Suez Crisis of 1956",
        "description": "# The Suez Crisis of 1956\n\nThe **Suez Crisis** was a major international incident...",
        "keywords": ["Suez Canal", "Egypt", "Nasser", "Cold War", "UK"],
    }


# ============================================================================
# TEST: get_cards()
# ============================================================================


class TestGetCards:
    """Test suite for CardService.get_cards()"""

    @patch("app.services.card_service.CardCRUD")
    def test_get_all_cards_success(self, mock_crud, card_service, mock_db_session, sample_cards_list):
        """Test retrieving all cards without filters."""
        # Arrange
        mock_crud.get_multi.return_value = sample_cards_list

        # Act
        result = card_service.get_cards(db=mock_db_session)

        # Assert
        assert len(result) == 2
        assert all(isinstance(card, CardResponse) for card in result)
        mock_crud.get_multi.assert_called_once_with(
            mock_db_session, title=None, skip=0, limit=100
        )

    @patch("app.services.card_service.CardCRUD")
    def test_get_cards_with_title_filter(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test retrieving cards with title filter."""
        # Arrange
        mock_crud.get_multi.return_value = [sample_card]
        title_filter = "Six-Day War"

        # Act
        result = card_service.get_cards(db=mock_db_session, title_filter=title_filter)

        # Assert
        assert len(result) == 1
        assert result[0].title == sample_card.title
        mock_crud.get_multi.assert_called_once_with(
            mock_db_session, title=title_filter, skip=0, limit=100
        )

    @patch("app.services.card_service.CardCRUD")
    def test_get_cards_with_pagination(self, mock_crud, card_service, mock_db_session, sample_cards_list):
        """Test retrieving cards with pagination parameters."""
        # Arrange
        mock_crud.get_multi.return_value = sample_cards_list
        skip = 10
        limit = 50

        # Act
        result = card_service.get_cards(db=mock_db_session, skip=skip, limit=limit)

        # Assert
        mock_crud.get_multi.assert_called_once_with(
            mock_db_session, title=None, skip=skip, limit=limit
        )

    @patch("app.services.card_service.CardCRUD")
    def test_get_cards_empty_result(self, mock_crud, card_service, mock_db_session):
        """Test retrieving cards when database returns empty list."""
        # Arrange
        mock_crud.get_multi.return_value = []

        # Act
        result = card_service.get_cards(db=mock_db_session)

        # Assert
        assert result == []

    @patch("app.services.card_service.CardCRUD")
    def test_get_cards_database_error(self, mock_crud, card_service, mock_db_session):
        """Test error handling when database operation fails."""
        # Arrange
        mock_crud.get_multi.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_cards(db=mock_db_session)
        
        assert "Failed to fetch cards" in str(exc_info.value)


# ============================================================================
# TEST: get_card()
# ============================================================================


class TestGetCard:
    """Test suite for CardService.get_card()"""

    @patch("app.services.card_service.CardCRUD")
    def test_get_card_success(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test successfully retrieving a card by ID."""
        # Arrange
        card_id = sample_card.id
        mock_crud.get.return_value = sample_card

        # Act
        result = card_service.get_card(db=mock_db_session, card_id=card_id)

        # Assert
        assert isinstance(result, CardResponse)
        assert result.id == card_id
        assert result.title == sample_card.title
        mock_crud.get.assert_called_once_with(mock_db_session, id=card_id)

    @patch("app.services.card_service.CardCRUD")
    def test_get_card_not_found(self, mock_crud, card_service, mock_db_session):
        """Test retrieving a card that doesn't exist."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.return_value = None

        # Act & Assert
        with pytest.raises(CardNotFoundError) as exc_info:
            card_service.get_card(db=mock_db_session, card_id=card_id)
        
        assert str(card_id) in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_card_database_error(self, mock_crud, card_service, mock_db_session):
        """Test error handling when database operation fails."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_card(db=mock_db_session, card_id=card_id)
        
        assert "Failed to fetch card" in str(exc_info.value)


# ============================================================================
# TEST: create_card_from_ai()
# ============================================================================


class TestCreateCardFromAI:
    """Test suite for CardService.create_card_from_ai()"""

    @patch("app.services.card_service.CardCRUD")
    def test_create_card_success_without_pdf(
        self, mock_crud, card_service, mock_db_session, sample_ai_response, sample_card
    ):
        """Test successfully creating a card without PDF context."""
        # Arrange
        card_service.ai_service.generate_card.return_value = sample_ai_response
        mock_crud.create.return_value = sample_card

        # Act
        result = card_service.create_card_from_ai(
            db=mock_db_session,
            title="The Suez Crisis",
            system_prompt="Write a neutral historical account",
            topcis_to_cover="Causes, events, and consequences",
        )

        # Assert
        assert isinstance(result, CardResponse)
        card_service.ai_service.generate_card.assert_called_once()
        call_args = card_service.ai_service.generate_card.call_args[1]
        assert call_args["title"] == "The Suez Crisis"
        assert call_args["system_prompt"] == "Write a neutral historical account"
        assert call_args["context_text"] == ""
        mock_crud.create.assert_called_once()

    @patch("app.services.card_service.extract_text_from_pdf")
    @patch("app.services.card_service.CardCRUD")
    def test_create_card_success_with_pdf(
        self, mock_crud, mock_pdf_parser, card_service, mock_db_session, sample_ai_response, sample_card
    ):
        """Test successfully creating a card with PDF context."""
        # Arrange
        pdf_bytes = b"fake-pdf-content"
        extracted_text = "This is the extracted PDF text content about the Suez Crisis."
        mock_pdf_parser.return_value = extracted_text
        card_service.ai_service.generate_card.return_value = sample_ai_response
        mock_crud.create.return_value = sample_card

        # Act
        result = card_service.create_card_from_ai(
            db=mock_db_session,
            title="The Suez Crisis",
            system_prompt="Write a neutral historical account",
            topcis_to_cover="Causes, events, and consequences",
            pdf_bytes=pdf_bytes,
        )

        # Assert
        assert isinstance(result, CardResponse)
        mock_pdf_parser.assert_called_once_with(pdf_bytes)
        call_args = card_service.ai_service.generate_card.call_args[1]
        assert call_args["context_text"] == extracted_text

    @patch("app.services.card_service.extract_text_from_pdf")
    def test_create_card_pdf_parsing_error(
        self, mock_pdf_parser, card_service, mock_db_session
    ):
        """Test error handling when PDF parsing fails."""
        # Arrange
        pdf_bytes = b"corrupt-pdf"
        mock_pdf_parser.side_effect = Exception("Failed to parse PDF")

        # Act & Assert
        with pytest.raises(PDFParsingError) as exc_info:
            card_service.create_card_from_ai(
                db=mock_db_session,
                title="Test",
                system_prompt="Test",
                topcis_to_cover="Test",
                pdf_bytes=pdf_bytes,
            )
        
        assert "Failed to parse PDF context" in str(exc_info.value)

    @patch("app.services.card_service.extract_text_from_pdf")
    @patch("app.services.card_service.CardCRUD")
    def test_create_card_pdf_empty_text(
        self, mock_crud, mock_pdf_parser, card_service, mock_db_session, sample_ai_response, sample_card
    ):
        """Test handling when PDF extraction returns empty text."""
        # Arrange
        pdf_bytes = b"empty-pdf"
        mock_pdf_parser.return_value = None
        card_service.ai_service.generate_card.return_value = sample_ai_response
        mock_crud.create.return_value = sample_card

        # Act
        result = card_service.create_card_from_ai(
            db=mock_db_session,
            title="Test",
            system_prompt="Test",
            topcis_to_cover="Test",
            pdf_bytes=pdf_bytes,
        )

        # Assert - should still succeed, just without context
        assert isinstance(result, CardResponse)
        call_args = card_service.ai_service.generate_card.call_args[1]
        assert call_args["context_text"] == ""

    def test_create_card_ai_generation_error(self, card_service, mock_db_session):
        """Test error handling when AI generation fails."""
        # Arrange
        card_service.ai_service.generate_card.side_effect = AIServiceError("API quota exceeded")

        # Act & Assert
        with pytest.raises(AIGenerationError) as exc_info:
            card_service.create_card_from_ai(
                db=mock_db_session,
                title="Test",
                system_prompt="Test",
                topcis_to_cover="Test",
            )
        
        assert "Failed to generate card" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_create_card_invalid_ai_response_structure(
        self, mock_crud, card_service, mock_db_session
    ):
        """Test error handling when AI returns invalid data structure."""
        # Arrange
        invalid_response = {"title": "Test"}  # Missing description and keywords
        card_service.ai_service.generate_card.return_value = invalid_response

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.create_card_from_ai(
                db=mock_db_session,
                title="Test",
                system_prompt="Test",
                topcis_to_cover="Test",
            )
        
        assert "Invalid AI response structure" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_create_card_database_error(
        self, mock_crud, card_service, mock_db_session, sample_ai_response
    ):
        """Test error handling when database save fails."""
        # Arrange
        card_service.ai_service.generate_card.return_value = sample_ai_response
        mock_crud.create.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.create_card_from_ai(
                db=mock_db_session,
                title="Test",
                system_prompt="Test",
                topcis_to_cover="Test",
            )
        
        assert "Failed to save card" in str(exc_info.value)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestCardServiceIntegration:
    """Integration-style tests for CardService workflows."""

    @patch("app.services.card_service.extract_text_from_pdf")
    @patch("app.services.card_service.CardCRUD")
    def test_full_card_creation_workflow_with_pdf(
        self, mock_crud, mock_pdf_parser, card_service, mock_db_session, sample_ai_response, sample_card
    ):
        """Test the complete workflow from PDF upload to card creation."""
        # Arrange
        pdf_bytes = b"historical-document"
        extracted_text = "Historical context about the event."
        mock_pdf_parser.return_value = extracted_text
        card_service.ai_service.generate_card.return_value = sample_ai_response
        mock_crud.create.return_value = sample_card

        # Act
        result = card_service.create_card_from_ai(
            db=mock_db_session,
            title="Test Event",
            system_prompt="Be neutral and objective",
            topcis_to_cover="Background, key events, aftermath",
            pdf_bytes=pdf_bytes,
        )

        # Assert - verify the full chain
        mock_pdf_parser.assert_called_once_with(pdf_bytes)
        card_service.ai_service.generate_card.assert_called_once()
        ai_call_args = card_service.ai_service.generate_card.call_args[1]
        assert ai_call_args["context_text"] == extracted_text
        mock_crud.create.assert_called_once()
        assert isinstance(result, CardResponse)

    @patch("app.services.card_service.CardCRUD")
    def test_search_and_retrieve_workflow(
        self, mock_crud, card_service, mock_db_session, sample_cards_list, sample_card
    ):
        """Test searching for cards and then retrieving a specific one."""
        # Arrange
        mock_crud.get_multi.return_value = sample_cards_list
        mock_crud.get.return_value = sample_card

        # Act - Step 1: Search
        search_results = card_service.get_cards(db=mock_db_session, title_filter="War")
        
        # Act - Step 2: Get specific card
        specific_card = card_service.get_card(db=mock_db_session, card_id=sample_card.id)

        # Assert
        assert len(search_results) == 2
        assert specific_card.id == sample_card.id


# ============================================================================
# TEST: Exception Hierarchy
# ============================================================================


class TestGetCopilotAnswer:
    """Test suite for CardService.get_copilot_answer()"""

    @patch("app.services.card_service.CardCRUD")
    def test_get_copilot_answer_success(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test successfully getting a copilot answer."""
        # Arrange
        card_id = sample_card.id
        question = "What were the main causes of this conflict?"
        expected_answer = "The main causes included territorial disputes and political tensions..."
        
        mock_crud.get.return_value = sample_card
        card_service.ai_service.copilot_answer.return_value = expected_answer

        # Act
        result = card_service.get_copilot_answer(
            db=mock_db_session,
            card_id=card_id,
            question=question
        )

        # Assert
        assert isinstance(result, CopilotResponse)
        assert result.answer == expected_answer
        mock_crud.get.assert_called_once_with(mock_db_session, id=card_id)
        card_service.ai_service.copilot_answer.assert_called_once_with(
            question=question,
            context=str(sample_card.description)
        )

    @patch("app.services.card_service.CardCRUD")
    def test_get_copilot_answer_card_not_found(self, mock_crud, card_service, mock_db_session):
        """Test copilot answer when card doesn't exist."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.return_value = None

        # Act & Assert
        with pytest.raises(CardNotFoundError) as exc_info:
            card_service.get_copilot_answer(
                db=mock_db_session,
                card_id=card_id,
                question="Test question?"
            )
        
        assert str(card_id) in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_copilot_answer_database_error(self, mock_crud, card_service, mock_db_session):
        """Test error handling when database operation fails."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_copilot_answer(
                db=mock_db_session,
                card_id=card_id,
                question="Test question?"
            )
        
        assert "Failed to fetch card" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_copilot_answer_ai_service_error(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test error handling when AI service fails."""
        # Arrange
        mock_crud.get.return_value = sample_card
        card_service.ai_service.copilot_answer.side_effect = AIServiceError("API error")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_copilot_answer(
                db=mock_db_session,
                card_id=sample_card.id,
                question="Test question?"
            )
        
        assert "Failed to generate copilot answer" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_copilot_answer_with_special_characters(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test copilot answer with special characters in question."""
        # Arrange
        question = "What about the 'Protocol of Sèvres'—was it secret?"
        expected_answer = "Yes, the Protocol of Sèvres was a secret agreement..."
        
        mock_crud.get.return_value = sample_card
        card_service.ai_service.copilot_answer.return_value = expected_answer

        # Act
        result = card_service.get_copilot_answer(
            db=mock_db_session,
            card_id=sample_card.id,
            question=question
        )

        # Assert
        assert result.answer == expected_answer


# ============================================================================
# TEST: get_bias_analysis()
# ============================================================================


class TestGetBiasAnalysis:
    """Test suite for CardService.get_bias_analysis()"""

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_success(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test successfully getting bias analysis."""
        # Arrange
        card_id = sample_card.id
        expected_score = 25.5
        expected_explanation = "The content shows minimal bias with neutral language..."
        
        mock_crud.get.return_value = sample_card
        card_service.ai_service.judge_bias.return_value = (expected_score, expected_explanation)

        # Act
        result = card_service.get_bias_analysis(
            db=mock_db_session,
            card_id=card_id
        )

        # Assert
        assert isinstance(result, BiasJudgeResponse)
        assert result.bias_score == expected_score
        assert result.explanation == expected_explanation
        mock_crud.get.assert_called_once_with(mock_db_session, id=card_id)
        card_service.ai_service.judge_bias.assert_called_once_with(
            content=str(sample_card.description)
        )

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_high_bias_score(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test bias analysis with high bias score."""
        # Arrange
        expected_score = 85.0
        expected_explanation = "The content contains loaded language and one-sided framing..."
        
        mock_crud.get.return_value = sample_card
        card_service.ai_service.judge_bias.return_value = (expected_score, expected_explanation)

        # Act
        result = card_service.get_bias_analysis(
            db=mock_db_session,
            card_id=sample_card.id
        )

        # Assert
        assert result.bias_score == 85.0
        assert "loaded language" in result.explanation

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_card_not_found(self, mock_crud, card_service, mock_db_session):
        """Test bias analysis when card doesn't exist."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.return_value = None

        # Act & Assert
        with pytest.raises(CardNotFoundError) as exc_info:
            card_service.get_bias_analysis(
                db=mock_db_session,
                card_id=card_id
            )
        
        assert str(card_id) in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_database_error(self, mock_crud, card_service, mock_db_session):
        """Test error handling when database operation fails."""
        # Arrange
        card_id = uuid4()
        mock_crud.get.side_effect = Exception("Database timeout")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_bias_analysis(
                db=mock_db_session,
                card_id=card_id
            )
        
        assert "Failed to fetch card" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_ai_service_error(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test error handling when AI service fails."""
        # Arrange
        mock_crud.get.return_value = sample_card
        card_service.ai_service.judge_bias.side_effect = AIServiceError("Model unavailable")

        # Act & Assert
        with pytest.raises(CardServiceError) as exc_info:
            card_service.get_bias_analysis(
                db=mock_db_session,
                card_id=sample_card.id
            )
        
        assert "Failed to analyze bias" in str(exc_info.value)

    @patch("app.services.card_service.CardCRUD")
    def test_get_bias_analysis_zero_score(self, mock_crud, card_service, mock_db_session, sample_card):
        """Test bias analysis with perfectly neutral content (score 0)."""
        # Arrange
        expected_score = 0.0
        expected_explanation = "The content is perfectly neutral with no detectable bias."
        
        mock_crud.get.return_value = sample_card
        card_service.ai_service.judge_bias.return_value = (expected_score, expected_explanation)

        # Act
        result = card_service.get_bias_analysis(
            db=mock_db_session,
            card_id=sample_card.id
        )

        # Assert
        assert result.bias_score == 0.0
        assert "neutral" in result.explanation.lower()


# ============================================================================
# TEST: Exception Hierarchy
# ============================================================================


class TestExceptionHierarchy:
    """Test that custom exceptions are properly raised and handled."""

    def test_card_not_found_error_is_card_service_error(self):
        """Test that CardNotFoundError inherits from CardServiceError."""
        error = CardNotFoundError("Test")
        assert isinstance(error, CardServiceError)

    def test_ai_generation_error_is_card_service_error(self):
        """Test that AIGenerationError inherits from CardServiceError."""
        error = AIGenerationError("Test")
        assert isinstance(error, CardServiceError)

    def test_pdf_parsing_error_is_card_service_error(self):
        """Test that PDFParsingError inherits from CardServiceError."""
        error = PDFParsingError("Test")
        assert isinstance(error, CardServiceError)
