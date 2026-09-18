"""Integrity guard over the token cap OpenAI chat requests actually carry.

gpt-5 and newer reject `max_tokens` with 400, and `ai_client` 0.4.6 hard-codes that
name, so a run against them fails on every object. Passes when either side is fixed
-- the client, or the rename in `scripts/benchmark_base.py`. See
dev/DEPENDENCY_PATCHES.md section 8.

Run logic-only with: pytest -m "not integrity".
"""
import inspect

import pytest

pytestmark = pytest.mark.integrity


def _client_sends_max_completion_tokens() -> bool:
    """True when the installed client already uses the parameter name OpenAI wants."""
    from ai_client import openai_client

    source = inspect.getsource(openai_client)
    # Only the chat path matters: responses maps to max_output_tokens and legacy
    # completions correctly keeps max_tokens.
    return "max_completion_tokens" in source


class _Completions:
    """Stands in for `client.api_client.chat.completions`, recording what it is sent."""

    def __init__(self):
        self.seen = {}

    def create(self, **kwargs):
        self.seen = kwargs
        return None

    def parse(self, **kwargs):
        self.seen = kwargs
        return None


class _Stub:
    def __init__(self):
        self.completions = _Completions()

        class _Chat:
            pass

        chat = _Chat()
        chat.completions = self.completions

        class _ApiClient:
            pass

        api = _ApiClient()
        api.chat = chat
        self.api_client = api


def _repo_renames_the_cap() -> bool:
    """True when this repo's wrapper is present and actually renames the keyword."""
    import benchmark_base  # from scripts/, put on sys.path by tests/conftest.py

    rename = getattr(benchmark_base, "_send_cap_as_max_completion_tokens", None)
    if rename is None:
        return False
    stub = _Stub()
    rename(stub)
    stub.api_client.chat.completions.create(model="gpt-5", max_tokens=123)
    sent = stub.api_client.chat.completions.seen
    return "max_tokens" not in sent and sent.get("max_completion_tokens") == 123


def test_openai_chat_requests_do_not_send_max_tokens():
    """Fails when a gpt-5-class OpenAI request would still carry `max_tokens`.

    Either fix satisfies this: the dependency sending the right name, or the
    rename in `scripts/benchmark_base.py`. When the dependency is fixed the
    wrapper becomes dead code and can be dropped -- this test keeps passing.
    """
    upstream_ok = _client_sends_max_completion_tokens()
    repo_ok = _repo_renames_the_cap()
    assert upstream_ok or repo_ok, (
        "OpenAI chat requests would send 'max_tokens', which gpt-5 and newer reject "
        "with 400 Unsupported parameter, failing every object of every affected test. "
        "Neither the installed ai_client nor this repository renames it. See "
        "dev/DEPENDENCY_PATCHES.md section 8 for the upstream fix and the stopgap."
    )
