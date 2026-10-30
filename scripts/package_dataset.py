"""Package a built dataset for the release repository and for Zenodo.

The GitHub-Zenodo webhook deposits the repository's source zipball at the tag rather than
the files attached to a release, so anything that must reach Zenodo has to be committed.
That constraint, with GitHub's 100 MB per-file limit, determines what this script produces
from a finished ``dataset/``:

  * ``release/`` -- the tree to commit. Parquet tables only, text files gzipped, and the
    payload sidecars as built (``payloads/<benchmark>/<YYYY-MM>.jsonl.gz``), so that one
    repository and one record hold the whole dataset. ``datapackage.json`` and the README are
    regenerated for this tree, because the build's copies describe files that packaging
    renames or omits.
  * ``SHA256SUMS``, written beside the output rather than inside it.

Packaging stops before writing anything when the inputs do not match
``manifest.output_sha256``, when an output path would overwrite an input, or, unless
``--development`` is given, when the build is partial, carries a blocking diagnostic, or
does not reconcile against the frontend export. It also refuses any release file over
GitHub's 100 MB per-file limit.

With ``--release-repo``, the release tree is then synced into a clone of the release
repository (see ``sync_release_repo``), with its ``.gitattributes``, ``LICENSE`` and
``.zenodo.json`` written beside it (``write_repo_files``), ready to review and commit.

    python -m scripts.package_dataset [--dataset dataset] [--out dist] [--development]
                                      [--release-repo PATH]
"""
import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.export_dataset import docs
from scripts.export_dataset.paths import check as check_paths

GITHUB_FILE_LIMIT = 100 * 1024 * 1024
"""Hard: a push containing a larger file is rejected outright."""

GITHUB_WARN_LIMIT = 50 * 1024 * 1024
"""Soft: GitHub warns, and the repository grows by this much per release forever."""

COMPRESS = (".csv", ".jsonl")
"""Text that compresses by an order of magnitude. Parquet is already compressed."""

EXCLUDE = (".csv",)
"""Table CSVs do not ship: Parquet is the lossless copy, the CSV cannot express the
distinction between a null and an empty string without a companion column, and shipping
both invites an analyst to reach for the one that loses information. `coverage.csv` is the
exception -- it has no Parquet form -- and ships gzipped."""

KEEP_CSV = ("coverage.csv",)

GENERATED_DOCS = ("datapackage.json", "README.md")
"""Rewritten for the release tree rather than copied from the build."""


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _gzip_to(source, target):
    """Deterministic gzip: no name and no timestamp in the header."""
    with open(source, "rb") as raw, open(target, "wb") as out:
        with gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0,
                           compresslevel=9) as gz:
            shutil.copyfileobj(raw, gz)


# --- verification ----------------------------------------------------------------

def verify_inputs(dataset, manifest):
    """Every file the build recorded is present and still hashes to what it recorded.

    Returns the list of problems rather than raising, so the caller can report all of them
    at once. `manifest.json` is the one expected exception: it cannot contain its own hash.
    """
    dataset = Path(dataset)
    declared = manifest.get("output_sha256")
    problems = []

    if not isinstance(declared, dict) or not declared:
        return ["manifest.json has no output_sha256, so nothing can be verified against it"]

    for relative, expected in sorted(declared.items()):
        path = dataset / relative
        if not path.is_file():
            problems.append("declared but missing: %s" % relative)
            continue
        actual = sha256_of(path)
        if actual != expected:
            problems.append("changed since the build: %s\n      recorded %s\n      actual   %s"
                            % (relative, expected, actual))

    on_disk = set(p.relative_to(dataset).as_posix()
                  for p in dataset.rglob("*") if p.is_file())
    extra = sorted(on_disk - set(declared) - {"manifest.json"})
    for relative in extra:
        problems.append("present but not in the build manifest: %s" % relative)

    return problems


# --- release preflight -----------------------------------------------------------

def release_preflight(dataset, manifest, reconcile=True):
    """Return the reasons this build must not be released. An empty list permits it.

    Set reconcile to false to skip the crosscheck against the frontend export. A release
    always reconciles; the parameter exists so that tests of the other blockers need not
    construct a frontend export.
    """
    blockers = []
    if manifest.get("partial"):
        blockers.append("the build is partial (%s); it covers a filtered subset of runs"
                        % json.dumps(manifest.get("build_filters")))
    if manifest.get("source_worktree_dirty"):
        blockers.append("built from a dirty worktree, so the recorded commit does not "
                        "describe the code that produced it")
    if manifest.get("source_worktree_dirty") is None:
        blockers.append("git provenance is unknown, so the recorded commit is unverified")

    diagnostics = Path(dataset) / "diagnostics.jsonl"
    if diagnostics.is_file():
        blocking = []
        for line in diagnostics.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("severity") == "blocking":
                    blocking.append("%s (%s)" % (row.get("source_path"), row.get("issue")))
        if blocking:
            blockers.append("%d blocking diagnostic(s), first: %s"
                            % (len(blocking), blocking[0]))
    if reconcile:
        blockers.extend(_reconciliation_blockers(dataset))
    return blockers


def _reconciliation_blockers(dataset):
    """Return blockers from reconciling the dataset against the frontend export.

    The website's export (benchmark-frontend) reads the same corpus with its own reader, and
    the dataset embeds one of the comparison artifacts, so the two can disagree about a run's
    identity, visibility, recorded scores or resolved prices. Reconciliation runs as part of the release decision rather than as
    a separate command.

    An absent frontend export is itself a blocker: it records that no reconciliation took
    place, not that none was needed.
    """
    from scripts.export_dataset import crosscheck

    if not crosscheck.FRONTEND_EXPORT.is_file():
        return ["no frontend export at %s, so nothing reconciled this build; run "
                "python -m generate in benchmark-frontend, or set BENCHMARK_FRONTEND_EXPORT"
                % crosscheck.FRONTEND_EXPORT]
    try:
        frontend = crosscheck.load_frontend()
        runs, requests, scores = crosscheck.load_dataset(dataset)
    except Exception as error:
        return ["the crosscheck against the frontend export could not run (%s)" % error]

    findings, shared = crosscheck.compare(runs, requests, scores, frontend)
    if findings:
        return ["%d crosscheck finding(s) over %d runs shared with the frontend export, "
                "first: %s -- %s. Run python -m scripts.export_dataset.crosscheck for the "
                "full report" % (len(findings), shared, findings[0]["check"],
                                 findings[0]["detail"])]
    print("  crosscheck: no unexpected differences over %d shared runs" % shared)
    return []


def build_release_tree(dataset, out):
    """Copy the dataset into `out`: Parquet and payloads as-is, text gzipped, CSV tables
    dropped."""
    dataset, out = Path(dataset), Path(out)
    check_paths(source=dataset, out=out)

    manifest = json.loads((dataset / "manifest.json").read_bytes().decode("utf-8"))
    built = manifest.get("output_sha256", {})

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    packaging = []
    for source in sorted(dataset.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(dataset)
        posix = relative.as_posix()
        if posix in GENERATED_DOCS:
            continue
        if source.suffix in EXCLUDE and source.name not in KEEP_CSV:
            continue

        if source.suffix in COMPRESS:
            target = out / relative.with_suffix(source.suffix + ".gz")
            target.parent.mkdir(parents=True, exist_ok=True)
            _gzip_to(source, target)
            transform = "gzip"
        else:
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            transform = "copy"

        packaging.append({
            "built_path": posix,
            "built_sha256": built.get(posix),
            "built_bytes": source.stat().st_size,
            "packaged_path": target.relative_to(out).as_posix(),
            "packaged_sha256": sha256_of(target),
            "packaged_bytes": target.stat().st_size,
            "transform": transform,
        })

    packaged_paths = set(entry["packaged_path"] for entry in packaging)
    for name, text in (
        ("datapackage.json",
         json.dumps(docs.release_datapackage(manifest, packaged_paths | set(GENERATED_DOCS)),
                    indent=2, sort_keys=True) + "\n"),
        ("README.md", docs.release_readme(manifest, packaged_paths | set(GENERATED_DOCS))),
    ):
        (out / name).write_text(text, encoding="utf-8", newline="\n")
        packaging.append({
            "built_path": None,
            "built_sha256": None,
            "built_bytes": None,
            "packaged_path": name,
            "packaged_sha256": sha256_of(out / name),
            "packaged_bytes": (out / name).stat().st_size,
            "transform": "generated_for_release",
        })

    (out / "packaging.json").write_text(
        json.dumps({"dataset_version": manifest.get("dataset_version"),
                    "schema_version": manifest.get("schema_version"),
                    "files": packaging}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return manifest, packaging


def check_declared_paths(out):
    """Every resource the packaged descriptor names must exist in the packaged tree."""
    out = Path(out)
    package = json.loads((out / "datapackage.json").read_bytes().decode("utf-8"))
    return [r["path"] for r in package.get("resources", [])
            if not (out / r["path"]).is_file()]


def check_sizes(out):
    blocked, warned = [], []
    for path in sorted(Path(out).rglob("*")):
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > GITHUB_FILE_LIMIT:
            blocked.append((path, size))
        elif size > GITHUB_WARN_LIMIT:
            warned.append((path, size))
    return blocked, warned


# --- the release repository ------------------------------------------------------

REPO_OWN = (".git", ".gitattributes", ".gitignore", ".zenodo.json", "LICENSE", ".github")
"""Top-level entries of the release repository that the release tree never contains and
the sync never deletes: the repository itself and its furniture. `write_repo_files` writes
three of them (`REPO_FILES`); the rest are the repository's own business."""

REPO_FILES = (".gitattributes", "LICENSE", ".zenodo.json")

LEGAL_CODE = Path(__file__).resolve().parent / "export_dataset" / "CC-BY-4.0.txt"
"""The CC BY 4.0 legal code, as creativecommons.org publishes it, for the repository's
LICENSE: GitHub recognises the licence from the full text, not from a name."""

GITATTRIBUTES = """\
# Committed bytes are the released bytes: no line-ending conversion, so every
# file still matches SHA256SUMS after a checkout on any platform.
* -text
"""

GITHUB_REPO_RECOMMENDED = 1024 * 1024 * 1024
"""GitHub recommends keeping a repository under 1 GB."""


def _git_in(repo, *args):
    result = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True,
                            text=True, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit("git %s failed in %s: %s"
                         % (" ".join(args), repo, result.stderr.strip()))
    return result.stdout


def _ignored(repo, paths):
    """The paths among `paths` (repository-relative) that the repository's ignore rules match."""
    result = subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", "-z",
                             "--stdin"], input="\0".join(sorted(paths)), capture_output=True,
                            text=True, encoding="utf-8")
    # 1 means none matched; anything above it is git failing.
    if result.returncode > 1:
        raise SystemExit("git check-ignore failed in %s: %s" % (repo, result.stderr.strip()))
    return set(filter(None, result.stdout.split("\0")))


def sync_release_repo(release, repo):
    """Make the working tree of the release repository hold exactly `release`, plus its own
    files (`REPO_OWN`). Return ``(added, changed, removed)`` as sorted path lists.

    Refuses a target that is not a git repository or has uncommitted changes, so whatever
    the sync does can be inspected with `git status` and undone with `git checkout`. Only
    tracked files are removed or overwritten: an ignored file is the one thing `git status`
    does not show and `git checkout` cannot bring back, so it is left alone, and a release
    file the ignore rules match is refused, since it would not be committed. Never removes
    the target itself: `build_release_tree` replaces its destination wholesale, which pointed
    at a repository would delete `.git`.
    """
    release, repo = Path(release), Path(repo)
    check_paths(source=release, release_repo=repo)
    if not (repo / ".git").exists():
        raise SystemExit("%s is not a git repository; clone the release repository there "
                         "first." % repo)
    if _git_in(repo, "status", "--porcelain").strip():
        raise SystemExit("%s has uncommitted changes; commit or discard them first, so the "
                         "sync is the only change in the tree." % repo)

    produced = set(p.relative_to(release).as_posix()
                   for p in release.rglob("*") if p.is_file())
    present = set(p for p in _git_in(repo, "ls-files", "-z").split("\0")
                  if p and p.split("/")[0] not in REPO_OWN)
    clash = sorted(p for p in produced if p.split("/")[0] in REPO_OWN)
    if clash:
        raise SystemExit("The release tree contains files the repository keeps as its own: "
                         "%s" % clash)
    ignored = _ignored(repo, produced)
    if ignored:
        raise SystemExit("The ignore rules of %s match %d release file(s), which would not be "
                         "committed: %s" % (repo, len(ignored), sorted(ignored)[:5]))

    added, changed, removed = [], [], []
    for relative in sorted(produced):
        source, target = release / relative, repo / relative
        if target.is_file() and sha256_of(target) == sha256_of(source):
            continue
        (changed if target.is_file() else added).append(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for relative in sorted(present - produced):
        (repo / relative).unlink()
        removed.append(relative)
    for directory in sorted((d for d in repo.rglob("*") if d.is_dir()
                             and d.relative_to(repo).parts[0] not in REPO_OWN),
                            key=lambda d: len(d.parts), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()
    return added, changed, removed


def zenodo_metadata(citation):
    """`.zenodo.json` for the dataset, from the release's own CITATION.cff (parsed).

    Zenodo reads this file in preference to CITATION.cff and to what it infers from GitHub;
    without it a deposit is typed software, and the type of a concept record cannot be
    changed after its first deposit. The version is left out: Zenodo takes the tag."""
    creators = []
    for author in citation.get("authors") or []:
        creator = {"name": "%s, %s" % (author["family-names"], author["given-names"])}
        if author.get("orcid"):
            creator["orcid"] = str(author["orcid"]).rsplit("/", 1)[-1]
        if author.get("affiliation"):
            creator["affiliation"] = author["affiliation"]
        creators.append(creator)
    return {
        "upload_type": "dataset",
        "title": citation["title"],
        # Self-contained, as the University of Basel's Zenodo community requires: the subject
        # and its context must be clear without the README or any other source.
        "description": "<p>The RISE Humanities Data Benchmark, maintained by RISE (Research "
                       "and Infrastructure Support) at the University of Basel, evaluates large "
                       "language models on tasks from humanities research: transcribing, "
                       "interpreting and extracting structured data from historical documents "
                       "such as letters, library cards, newspaper advertisements and medieval "
                       "manuscripts, scored against ground truths defined by domain experts, "
                       "with the cost and runtime of every request.</p><p>%s</p><p>Tables in "
                       "Parquet, a metric dictionary, coverage, diagnostics and a source "
                       "manifest, with the original request and scoring JSON as gzipped JSON "
                       "Lines. A new release follows each release of the benchmark software; "
                       "each is a complete snapshot. README.md documents the tables and how to "
                       "use them, CHANGELOG.md what changed between releases.</p>"
                       % " ".join(str(citation["abstract"]).split()),
        "creators": creators,
        "access_right": "open",
        "license": "cc-by-4.0",
        "keywords": citation.get("keywords") or [],
        "related_identifiers": [{"identifier": docs.SOFTWARE_CONCEPT_DOI,
                                 "relation": "isSupplementTo", "resource_type": "software",
                                 "scheme": "doi"}],
    }


def write_repo_files(release, repo):
    """Write `REPO_FILES` into the release repository and return their names.

    Rewritten at every sync, so the deposit's description and authors follow the release
    being committed rather than the first one."""
    import yaml

    release, repo = Path(release), Path(repo)
    citation = yaml.safe_load((release / "CITATION.cff").read_text(encoding="utf-8"))
    (repo / ".gitattributes").write_text(GITATTRIBUTES, encoding="utf-8", newline="\n")
    shutil.copyfile(LEGAL_CODE, repo / "LICENSE")
    (repo / ".zenodo.json").write_text(
        json.dumps(zenodo_metadata(citation), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    return list(REPO_FILES)


def repo_size_after(repo, added, changed):
    """Return ``(packed_bytes, adding_bytes)``: the repository's history so far, and what
    committing the synced files adds to it. Parquet and gzip do not compress further, so
    their size on disk is close to what the commit costs."""
    packed = 0
    for line in _git_in(repo, "count-objects", "-v").splitlines():
        key, _, value = line.partition(":")
        if key.strip() in ("size", "size-pack"):
            packed += int(value.strip()) * 1024
    adding = sum((Path(repo) / p).stat().st_size for p in list(added) + list(changed))
    return packed, adding


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", default="dataset")
    parser.add_argument("--out", default="dist")
    parser.add_argument("--development", action="store_true",
                        help="package a build that is not releasable; output is labelled "
                             "and no deposit instruction is printed")
    parser.add_argument("--release-repo",
                        help="clone of the release repository: its working tree is made to "
                             "hold the release, ready to review and commit")
    args = parser.parse_args(argv)
    if args.release_repo and args.development:
        raise SystemExit("A development package never goes to the release repository.")

    dataset, out = Path(args.dataset), Path(args.out)
    if not (dataset / "manifest.json").is_file():
        raise SystemExit("No built dataset at %s. Run `python -m scripts.export_dataset` "
                         "first." % dataset.resolve())
    # The release tree and SHA256SUMS both land under `out`: one check covers them,
    # and it must precede the first write.
    check_paths(source=dataset, out=out)
    manifest = json.loads((dataset / "manifest.json").read_bytes().decode("utf-8"))
    version = manifest.get("dataset_version") or "unknown"

    print("Verify build inputs ...")
    problems = verify_inputs(dataset, manifest)
    if problems:
        raise SystemExit(
            "Refusing to package: the build directory does not match its own manifest.\n  "
            + "\n  ".join(problems)
            + "\n\nPackaging would checksum these bytes and present them as the recorded "
              "build. Rebuild, or establish where the difference came from.")
    print("  %d files verified against manifest.output_sha256"
          % len(manifest.get("output_sha256", {})))

    print("Release preflight ...")
    blockers = release_preflight(dataset, manifest)
    if blockers and not args.development:
        raise SystemExit(
            "Refusing to package for release:\n  - " + "\n  - ".join(blockers)
            + "\n\nUse --development to package it anyway; the output is labelled and "
              "carries no deposit instruction.")
    if blockers:
        print("  %d blocker(s), overridden by --development:" % len(blockers))
        for blocker in blockers:
            print("    - %s" % blocker)
    else:
        print("  releasable")

    out.mkdir(parents=True, exist_ok=True)
    release = out / ("release-development" if args.development else "release")

    print("Release tree ...")
    _manifest, packaging = build_release_tree(dataset, release)
    total = sum(entry["packaged_bytes"] for entry in packaging)
    print("  %s  %d files, %.1f MB" % (release, len(packaging), total / 1048576))

    missing = check_declared_paths(release)
    if missing:
        raise SystemExit("Packaged datapackage.json names resources that are not there: %s"
                         % missing)
    print("  every declared resource path resolves")

    blocked, warned = check_sizes(release)
    for path, size in warned:
        print("  note: %s is %.1f MB, over GitHub's %d MB warning threshold"
              % (path.relative_to(release).as_posix(), size / 1048576,
                 GITHUB_WARN_LIMIT // 1048576))
    if blocked:
        raise SystemExit(
            "Refusing to package: %d file(s) exceed GitHub's %d MB hard limit:\n  %s"
            % (len(blocked), GITHUB_FILE_LIMIT // 1048576,
               "\n  ".join("%s (%.1f MB)" % (p.relative_to(release).as_posix(), s / 1048576)
                           for p, s in blocked)))

    print("Checksums ...")
    lines = []
    for path in sorted(release.rglob("*")):
        if path.is_file():
            lines.append("%s  %s/%s" % (sha256_of(path), release.name,
                                        path.relative_to(release).as_posix()))
    sums = out / "SHA256SUMS"
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("  %s  %d entries" % (sums, len(lines)))

    if args.development:
        print("\nDevelopment package at %s. Not releasable; see the blockers above."
              % release)
        return 0
    if not args.release_repo:
        print("\nDataset version %s. Sync it into the release repository with "
              "--release-repo, commit, tag it, and let the Zenodo webhook deposit it."
              % version)
        return 0

    print("Release repository ...")
    repo = Path(args.release_repo)
    added, changed, removed = sync_release_repo(release, repo)
    print("  %s  %d added, %d changed, %d removed" % (repo, len(added), len(changed),
                                                      len(removed)))
    print("  wrote %s" % ", ".join(write_repo_files(release, repo)))
    packed, adding = repo_size_after(repo, added, changed)
    print("  history %.1f MB; committing this release adds about %.1f MB"
          % (packed / 1048576, adding / 1048576))
    if packed + adding > GITHUB_REPO_RECOMMENDED:
        print("  note: over GitHub's recommended 1 GB per repository")
    print("\nDataset version %s. Review with git status in %s, commit, tag %s, and let the "
          "Zenodo webhook deposit it." % (version, repo, version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
