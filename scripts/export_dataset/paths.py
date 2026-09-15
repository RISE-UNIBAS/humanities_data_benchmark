"""Validate source and output paths before dataset filesystem operations.

Reject identical or nested paths assigned to different roles, including source,
output, staging, and backup. Reject writable destinations inside the protected
results, benchmark, and shared-data directories.

Resolve paths before comparison to account for relative paths and filesystem
links. Builders call these checks before creating or replacing output directories.
"""
from pathlib import Path

from scripts.results_index import BENCHMARKS_PATH, PROJECT_ROOT, RESULTS_PATH

PROTECTED_INPUTS = (
    RESULTS_PATH,
    BENCHMARKS_PATH,
    PROJECT_ROOT / "scripts" / "data",
)
"""Repository input directories that cannot contain generated output destinations."""


class UnsafePaths(RuntimeError):
    """Raised when source or output paths violate the separation rules."""


def _resolved(path):
    """Expand the home directory and resolve the path to an absolute Path.

    Resolve existing filesystem links and allow nonexistent path components.
    Subsequent comparisons use the host platform's Path semantics.
    """
    return Path(path).expanduser().resolve()


def _contains(parent, child):
    """Return whether child equals parent or is nested beneath it."""
    return parent == child or parent in child.parents


def check(**paths):
    """Validate the supplied source, out, staging, and previous path roles.

    Ignore None values. Treat every role except source as writable, and use keyword
    names in error messages. Return True on success or raise UnsafePaths.
    """
    named = [(name, _resolved(path)) for name, path in paths.items() if path is not None]

    for index, (name, path) in enumerate(named):
        for other_name, other in named[index + 1:]:
            if path == other:
                raise UnsafePaths(
                    "%s and %s are the same directory (%s). The build deletes its "
                    "destination before writing it, so this would destroy the input."
                    % (name, other_name, path))
            if _contains(path, other):
                raise UnsafePaths(
                    "%s (%s) contains %s (%s). A destination inside the source makes the "
                    "build consume its own output." % (name, path, other_name, other))
            if _contains(other, path):
                raise UnsafePaths(
                    "%s (%s) contains %s (%s). A destination inside the source makes the "
                    "build consume its own output." % (other_name, other, name, path))

    writable = [(name, path) for name, path in named if name != "source"]
    for name, path in writable:
        for protected in PROTECTED_INPUTS:
            resolved_protected = _resolved(protected)
            if _contains(resolved_protected, path) or path == resolved_protected:
                raise UnsafePaths(
                    "%s (%s) is inside %s, which the build reads. Generated output must "
                    "never replace the stored corpus -- results/ in particular cannot be "
                    "regenerated." % (name, path, resolved_protected))
    return True
