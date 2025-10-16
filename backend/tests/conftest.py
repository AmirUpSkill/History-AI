# Helpers and fixtures for AI service tests
from typing import Generator
import pytest

class DummyResponse:
    def __init__(self, text: str | None):
        self.text = text

class DummyModelClient:
    def __init__(self, responses: list[DummyResponse]):
        self._responses = responses
        self._i = 0

    def generate_content(self, model: str, contents: str, config=None):
        if self._i < len(self._responses):
            resp = self._responses[self._i]
            self._i += 1
            return resp
        # default empty
        return DummyResponse("")

class DummyGenAIClient:
    def __init__(self, model_client: DummyModelClient):
        self.models = model_client

@pytest.fixture
def dummy_success_json_response() -> DummyResponse:
    return DummyResponse('{"title":"T","description":"Valid description text","keywords":["a","b"]}')

@pytest.fixture
def dummy_markdown_wrapped_json_response() -> DummyResponse:
    return DummyResponse('```json\n{"title":"T","description":"Valid description text","keywords":["a","b"]}\n```')

@pytest.fixture
def dummy_empty_response() -> DummyResponse:
    return DummyResponse("")

@pytest.fixture
def dummy_copilot_response() -> DummyResponse:
    return DummyResponse('The Protocol of Sèvres was a secret agreement made in October 1956.')

@pytest.fixture
def dummy_bias_judge_response() -> DummyResponse:
    return DummyResponse('{"bias_score": 78.5, "explanation": "The text exhibits strong pro-Egyptian bias with loaded language."}')

@pytest.fixture
def make_dummy_client():
    def _make(responses: list[DummyResponse]) -> DummyGenAIClient:
        return DummyGenAIClient(DummyModelClient(responses))
    return _make
