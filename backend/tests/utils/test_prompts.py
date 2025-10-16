import pytest

from app.utils.prompts import (
    build_card_generation_prompt,
    build_copilot_prompt,
    build_bias_judge_prompt,
)


def test_build_card_generation_prompt_includes_context():
    prompt = build_card_generation_prompt(
        title="Title",
        system_prompt="Sys",
        topics_to_cover="Topics",
        context_text="CTX",
    )
    assert "TITLE: Title" in prompt
    assert "SYSTEM PROMPT" in prompt
    assert "TOPICS TO COVER" in prompt
    assert "ADDITIONAL CONTEXT" in prompt
    assert "CTX" in prompt


def test_build_card_generation_prompt_without_context():
    prompt = build_card_generation_prompt(
        title="Title",
        system_prompt="Sys",
        topics_to_cover="Topics",
        context_text=None,
    )
    assert "TITLE: Title" in prompt
    assert "ADDITIONAL CONTEXT" not in prompt


def test_build_copilot_prompt():
    prompt = build_copilot_prompt("Q?", "DOC")
    assert "QUESTION FROM USER: Q?" in prompt
    assert "DOCUMENT CONTEXT:" in prompt


def test_build_bias_judge_prompt():
    prompt = build_bias_judge_prompt("CONTENT")
    assert "CONTENT TO ANALYZE:" in prompt
    assert "bias_score" in prompt
