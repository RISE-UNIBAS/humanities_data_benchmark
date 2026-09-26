"""Integrity guard over the token cap OpenAI chat requests actually carry.

gpt-5 and newer reject `max_tokens` with 400, so a run against them fails on every
object. The client renames the cap for the model families it knows; this sends each
catalogued OpenAI model through it and reads the parameters it would put on the wire.

Run logic-only with: pytest -m "not integrity".
"""
import csv
import os
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.integrity

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "benchmarks", "benchmarks_tests.csv")
NEEDS_MAX_COMPLETION_TOKENS = ("gpt-5", "gpt-6", "o1", "o3", "o4")


def _openai_models():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return sorted({r["model"] for r in csv.DictReader(f)
                       if r["provider"] == "openai"
                       and r["legacy_test"].strip().lower() != "true"})


def _sent(model):
    from ai_client import create_ai_client

    seen = {}

    def create(**params):
        seen.update(params)
        message = SimpleNamespace(content="{}", tool_calls=None, refusal=None, parsed=None)
        return SimpleNamespace(model=model, usage=None,
                               choices=[SimpleNamespace(message=message, finish_reason="stop")])

    client = create_ai_client("openai", api_key="unused", max_tokens=123)
    client.api_client = SimpleNamespace(chat=SimpleNamespace(
        completions=SimpleNamespace(create=create)))
    client.prompt(model, "hi")
    return seen


@pytest.mark.parametrize("model", _openai_models())
def test_openai_chat_requests_carry_the_cap_the_model_accepts(model):
    sent = _sent(model)
    if model.startswith(NEEDS_MAX_COMPLETION_TOKENS):
        assert "max_tokens" not in sent and sent.get("max_completion_tokens") == 123, (
            "%s would be sent %r; gpt-5 and newer reject max_tokens with 400 Unsupported "
            "parameter. Add its prefix to MAX_COMPLETION_TOKENS_PREFIXES in "
            "generic-llm-api-client's ai_client/openai_client.py." % (model, sent))
    else:
        assert sent.get("max_tokens") == 123, "%s lost its output cap: %r" % (model, sent)
