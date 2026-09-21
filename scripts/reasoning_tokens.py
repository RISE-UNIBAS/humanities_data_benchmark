"""Reasoning tokens a provider billed for but left out of `output_tokens`.

`reasoning_tokens` is the part not already counted in `output_tokens`. Providers differ:
some report reasoning outside their completion count, others inside it. Defining the
field as the uncounted remainder makes `input + output + reasoning == total` hold for
every provider, so consumers need no per-provider rules.

Kept separate from its callers so the derivation has one definition.
"""
import json
import os
import sys
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

REPORTED_PATHS = (
    ("usage_metadata", "thoughts_token_count"),                       # genai
    ("usage", "completion_tokens_details", "reasoning_tokens"),       # x-ai, openai chat
    ("usage", "output_tokens_details", "reasoning_tokens"),           # openai responses
)


def as_dict(raw_response) -> Optional[dict]:
    """Parse a stored `raw_response`; it is a JSON string more often than a dict."""
    if isinstance(raw_response, dict):
        return raw_response
    if isinstance(raw_response, str):
        try:
            parsed = json.loads(raw_response)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def reported_reasoning(raw_response) -> Optional[int]:
    """The provider's own reasoning count, or None if it reported none."""
    doc = as_dict(raw_response)
    if doc is None:
        return None
    for path in REPORTED_PATHS:
        node = doc
        for key in path:
            if not isinstance(node, dict):
                node = None
                break
            node = node.get(key)
        if isinstance(node, int):
            return node
    return None


def gap_of(usage) -> Optional[int]:
    """`total - input - output`, or None when the provider reported no total.

    A missing or zero `total_tokens` means unknown, which is not the same as zero.
    """
    total = usage.get("total_tokens") or 0
    if not total:
        return None
    return total - (usage.get("input_tokens") or 0) - (usage.get("output_tokens") or 0)


def uncounted_reasoning(usage, raw_response=None) -> Optional[int]:
    """Billed reasoning tokens not already inside `output_tokens`.

    Clamped to the gap, so a provider reporting reasoning inside `output_tokens` yields 0.
    """
    gap = gap_of(usage)
    if gap is None:
        return None
    reported = reported_reasoning(raw_response)
    value = gap if reported is None else reported
    return max(0, min(value, gap))

