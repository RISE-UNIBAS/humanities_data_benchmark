"""The documented commands start, run as CLAUDE.md runs them.

The rest of the suite imports through conftest.py, which puts scripts/ on sys.path, so a
module that only imports there passes it and still fails as a command: an import of
benchmark_base broke generate_compare_detail and generate_all this way (2026-11-20).
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("command", [
    ["-m", "scripts.compare.generate_compare_detail", "--help"],
    ["-m", "scripts.export_dataset", "--help"],
    ["-m", "scripts.package_dataset", "--help"],
    ["scripts/rescore.py", "--help"],
    # generate_all takes no arguments and runs on start, so only its import is tried.
    ["-c", "import scripts.compare.generate_all"],
])
def test_the_command_starts(command):
    result = subprocess.run([sys.executable, *command], cwd=PROJECT_ROOT,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr[-2000:]
