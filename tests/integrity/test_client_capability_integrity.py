"""Integrity guards over what the ai_client dependency will actually send.

Some clients silently drop parts of a request rather than failing, so a test
config can look correct while the model never sees the data it is scored on.
These guards turn that silence into a failure.

Run logic-only with: pytest -m "not integrity".
"""
import csv
import os

import pytest

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(REPO_ROOT, "benchmarks", "benchmarks_tests.csv")
BENCHMARKS_DIR = os.path.join(REPO_ROOT, "benchmarks")


def _has_images(benchmark: str) -> bool:
    return os.path.isdir(os.path.join(BENCHMARKS_DIR, benchmark, "images"))


@pytest.fixture(scope="module")
def non_legacy_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)
                if r["legacy_test"].strip().lower() != "true"]


# DeepSeek models the benchmark runs *for* their vision capability. Text-only
# DeepSeek models are excluded: the client drops their images by design.
DEEPSEEK_VISION_MODELS = {"deepseek-v4-flash-vision-exp", "deepseek-flash"}


def test_deepseek_vision_models_pass_the_client_image_gate(non_legacy_rows):
    """DeepSeekClient strips images from models whose name misses its keyword list.

    ai_client.deepseek_client._VISION_MODEL_KEYWORDS gates image input on a
    substring of the model name. A model that fails the gate still runs: the
    images are dropped with a warning and the model is scored on the prompt
    alone. Released 0.4.6 ships ("vl", "vision"), which misses deepseek-flash,
    so scripts/benchmark_base.py extends the tuple on import. Importing it is
    what puts the runner's gate in place, and what this reads.

    So this fails when a DeepSeek vision model is added to the catalogue and to
    DEEPSEEK_VISION_MODELS below without being added to the keywords.
    """
    import benchmark_base  # noqa: F401  -- imported for the keyword extension
    from ai_client.deepseek_client import _VISION_MODEL_KEYWORDS

    configured = {
        r["model"] for r in non_legacy_rows
        if r["provider"] == "deepseek" and _has_images(r["name"])
    } & DEEPSEEK_VISION_MODELS

    stripped = sorted(
        m for m in configured
        if not any(kw in m.lower() for kw in _VISION_MODEL_KEYWORDS)
    )
    assert not stripped, (
        f"DeepSeek vision models whose images the installed client will silently "
        f"drop: {stripped}. Re-apply the _VISION_MODEL_KEYWORDS patch to the "
        f"installed ai_client -- see dev/DEPENDENCY_PATCHES.md."
    )
