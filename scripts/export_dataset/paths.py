"""Refuse a build whose output would destroy its input.

`build_release_tree` and `build` both `rmtree` their destination before writing it, and
`publish` renames directories around. None of that checked whether the destination *was*
the source. `--dataset <p>/release --out <p>` makes both resolve to `<p>/release`, and the
source is deleted before the copy loop starts; `--out results` lets publication replace the
raw archive with the generated dataset and then drop the original through `.previous`.

The audit reproduced the first of those in an isolated fixture by intercepting the deletion.
Nothing real was lost, and nothing should be able to be.

Two rules, checked against resolved paths so a Windows case alias or a junction cannot slip
past a string comparison:

  * No two of source, destination, staging and backup may be the same directory, and none
    may contain another. A destination inside the source is how a packager comes to consume
    its own output.
  * The directories the build reads -- `results/`, `benchmarks/`, `scripts/data/` -- are
    never writable destinations, whatever the arguments say.

Checked before any `mkdir`, `rmtree` or rename, so a refusal leaves the filesystem as it
was.
"""
from pathlib import Path

from scripts.results_index import BENCHMARKS_PATH, PROJECT_ROOT, RESULTS_PATH

PROTECTED_INPUTS = (
    RESULTS_PATH,
    BENCHMARKS_PATH,
    PROJECT_ROOT / "scripts" / "data",
)
"""Read by every build. Writing a generated artifact over any of them destroys the corpus
this project exists to preserve, and `results/` cannot be regenerated at all."""


class UnsafePaths(RuntimeError):
    """Raised before anything is created, deleted or renamed."""


def _resolved(path):
    """An absolute path that compares correctly on Windows.

    `Path.resolve()` follows junctions and normalises case for a path that exists, which is
    what makes `DATASET` and `dataset` compare equal here. For a path that does not exist
    yet it still absolutises and normalises separators, which is enough: the dangerous
    comparisons are all against directories that do exist.
    """
    return Path(path).expanduser().resolve()


def _contains(parent, child):
    """Whether `child` is `parent` or sits underneath it."""
    return parent == child or parent in child.parents


def check(**paths):
    """Reject overlapping roles. Pass any of source=, out=, staging=, previous=.

    Keyword names are used in the message, so the caller's own vocabulary reaches the
    operator rather than this module's.
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
