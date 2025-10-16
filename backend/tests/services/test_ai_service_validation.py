import json
import pytest

from app.services.ai_service import AIService, AIServiceError

class Dummy:
    pass

class _PatchGenAI:
    def __init__(self, monkeypatch: pytest.MonkeyPatch, response_text: str):
        self.monkeypatch = monkeypatch
        self.response_text = response_text

    def __enter__(self):
        import app.services.ai_service as ai_mod
        class DummyResp:
            def __init__(self, t):
                self.text = t
        class StubModels:
            def generate_content(self, model, contents, config=None):
                return DummyResp(self.response_text)
        class StubGenAI:
            @staticmethod
            def configure(api_key: str):
                return None
            class Client:
                def __init__(self_inner):
                    self_inner.models = StubModels()
        self.monkeypatch.setattr(ai_mod, "genai", StubGenAI, raising=True)
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

@pytest.mark.parametrize("bad_text", [
    "{}",  # missing required fields
    '{"title": 1, "description": "x" , "keywords": []}',  # wrong type for title
    '{"title": "", "description": "x" , "keywords": ["a"]}',  # title too short
    '{"title": "T", "description": "x" , "keywords": "no-list"}',  # keywords not list
])

def test_validate_card_structure_errors(monkeypatch, bad_text):
    with _PatchGenAI(monkeypatch, bad_text):
        svc = AIService(api_key="dummy")
        with pytest.raises(AIServiceError):
            svc.generate_card("t","s","k")
