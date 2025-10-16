import json
import types as pytypes
import builtins
import pytest

from app.services.ai_service import AIService, AIServiceError

class _PatchGenAI:
    """Context manager to patch google.genai and client inside AIService.
    We replace genai.Client() with our dummy and skip configure()."""
    def __init__(self, monkeypatch: pytest.MonkeyPatch, dummy_client):
        self.monkeypatch = monkeypatch
        self.dummy_client = dummy_client

    def __enter__(self):
        # Patch genai module used in ai_service
        import app.services.ai_service as ai_mod
        # Provide a stub for genai with configure and Client
        class StubGenAI:
            @staticmethod
            def configure(api_key: str):
                return None
            class Client:
                def __init__(self_inner):
                    # substitute with provided dummy client
                    self_inner.models = self.dummy_client.models
        self.monkeypatch.setattr(ai_mod, "genai", StubGenAI, raising=True)
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

@pytest.fixture
def ai_service(monkeypatch, make_dummy_client, dummy_success_json_response):
    dummy = make_dummy_client([dummy_success_json_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        yield svc


def test_generate_card_success(ai_service):
    res = ai_service.generate_card(
        title="Suez Crisis",
        system_prompt="Neutral, academic tone",
        topics_to_cover="Background; International response; Consequences",
        context_text="Some pdf context",
    )
    assert res["title"] == "T"
    assert isinstance(res["description"], str) and len(res["description"]) > 0
    assert isinstance(res["keywords"], list) and res["keywords"]


def test_generate_card_parses_markdown_wrapped_json(monkeypatch, make_dummy_client, dummy_markdown_wrapped_json_response):
    dummy = make_dummy_client([dummy_markdown_wrapped_json_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        res = svc.generate_card(
            title="Event",
            system_prompt="Perspective",
            topics_to_cover="Topics",
        )
        assert res["title"] == "T"


def test_generate_card_empty_response_raises(monkeypatch, make_dummy_client, dummy_empty_response):
    dummy = make_dummy_client([dummy_empty_response, dummy_empty_response, dummy_empty_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError):
            svc.generate_card(
                title="Event",
                system_prompt="Perspective",
                topics_to_cover="Topics",
            )


def test_json_parse_error_raises(monkeypatch, make_dummy_client):
    # Return invalid JSON
    from tests.conftest import DummyResponse
    dummy = make_dummy_client([DummyResponse("not json")])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError):
            svc.generate_card(
                title="Event",
                system_prompt="Perspective",
                topics_to_cover="Topics",
            )


# =============================================================================
# COPILOT ANSWER TESTS
# =============================================================================

def test_copilot_answer_success(monkeypatch, make_dummy_client, dummy_copilot_response):
    dummy = make_dummy_client([dummy_copilot_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        answer = svc.copilot_answer(
            question="What was the Protocol of Sèvres?",
            context="# The Suez Crisis...The invasion was planned under the Protocol of Sèvres...",
        )
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "Protocol" in answer or "protocol" in answer.lower()


def test_copilot_answer_empty_question_raises(monkeypatch, make_dummy_client, dummy_copilot_response):
    dummy = make_dummy_client([dummy_copilot_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="Question and context are required"):
            svc.copilot_answer(question="", context="Some context")


def test_copilot_answer_empty_context_raises(monkeypatch, make_dummy_client, dummy_copilot_response):
    dummy = make_dummy_client([dummy_copilot_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="Question and context are required"):
            svc.copilot_answer(question="What happened?", context="")


def test_copilot_answer_api_failure_raises(monkeypatch, make_dummy_client, dummy_empty_response):
    dummy = make_dummy_client([dummy_empty_response, dummy_empty_response, dummy_empty_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError):
            svc.copilot_answer(
                question="What happened?",
                context="Some context",
            )


# =============================================================================
# BIAS JUDGE TESTS
# =============================================================================

def test_judge_bias_success(monkeypatch, make_dummy_client, dummy_bias_judge_response):
    dummy = make_dummy_client([dummy_bias_judge_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        bias_score, explanation = svc.judge_bias(
            content="# The Glorious Nationalization\nIn a bold and heroic move, President Nasser rightfully reclaimed the canal..." * 5,
        )
        assert isinstance(bias_score, float)
        assert 0.0 <= bias_score <= 100.0
        assert isinstance(explanation, str)
        assert len(explanation) > 0


def test_judge_bias_content_too_short_raises(monkeypatch, make_dummy_client, dummy_bias_judge_response):
    dummy = make_dummy_client([dummy_bias_judge_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="at least 50 characters"):
            svc.judge_bias(content="Too short")


def test_judge_bias_empty_content_raises(monkeypatch, make_dummy_client, dummy_bias_judge_response):
    dummy = make_dummy_client([dummy_bias_judge_response])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="at least 50 characters"):
            svc.judge_bias(content="")


def test_judge_bias_invalid_json_raises(monkeypatch, make_dummy_client):
    from tests.conftest import DummyResponse
    dummy = make_dummy_client([DummyResponse("not valid json")])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError):
            svc.judge_bias(content="Some content that is long enough to pass validation checks")


def test_judge_bias_missing_fields_raises(monkeypatch, make_dummy_client):
    from tests.conftest import DummyResponse
    # Valid JSON but missing required fields
    dummy = make_dummy_client([DummyResponse('{"bias_score": 50.0}')])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="Invalid bias judge response format"):
            svc.judge_bias(content="Some content that is long enough to pass validation checks")


def test_judge_bias_score_out_of_range_raises(monkeypatch, make_dummy_client):
    from tests.conftest import DummyResponse
    # Score > 100
    dummy = make_dummy_client([DummyResponse('{"bias_score": 150.0, "explanation": "Test"}')])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="Bias score out of range"):
            svc.judge_bias(content="Some content that is long enough to pass validation checks")


def test_judge_bias_negative_score_raises(monkeypatch, make_dummy_client):
    from tests.conftest import DummyResponse
    # Negative score
    dummy = make_dummy_client([DummyResponse('{"bias_score": -10.0, "explanation": "Test"}')])
    with _PatchGenAI(monkeypatch, dummy):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError, match="Bias score out of range"):
            svc.judge_bias(content="Some content that is long enough to pass validation checks")
