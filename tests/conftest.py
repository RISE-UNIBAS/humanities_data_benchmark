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