"""Pytest configuration file to set up proper import paths."""
import sys
import os
from types import SimpleNamespace

import pytest

# Add the scripts directory to Python path
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def make_scorer():
    """Build a benchmark scorer instance without running __init__ (no AI client,
    no API key — CI-safe). Scoring methods only need prepare_scoring_data (base
    class) and, for some benchmarks, self.rules; inject any extra attrs via kwargs.
    """
    def _make(cls, rules=None, **attrs):
        instance = cls.__new__(cls)
        instance.rules = rules
        for key, value in attrs.items():
            setattr(instance, key, value)
        return instance
    return _make


@pytest.fixture
def response():
    """Build a minimal LLMResponse-like stub exposing .parsed and .text."""
    def _response(parsed=None, text=""):
        return SimpleNamespace(parsed=parsed, text=text)
    return _response

@pytest.fixture
def metrics():
    """A score with its comparison detail stripped off.

    Scorers return `field_scores` alongside their metrics -- the values they actually
    compared and the similarity assigned to each -- so a comparison view can show the
    scorer's own judgement instead of re-deriving one that would disagree with it.
    These tests are about the metrics, so drop that rather than restate a large nested
    structure in every expectation.
    """
    def _metrics(score):
        if not isinstance(score, dict):
            return score
        return dict((k, v) for k, v in score.items() if k != "field_scores")
    return _metrics
