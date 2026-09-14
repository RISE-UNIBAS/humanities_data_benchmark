"""Package a built dataset for the release repository and for Zenodo.

Plan §6.1. The GitHub-Zenodo webhook deposits the repository's source zipball at the tag,
not the files attached to the release, so whatever should reach Zenodo has to be committed.
That plus GitHub's hard 100 MB per-file limit is what this script exists to satisfy.

It produces, from a finished `dataset/`:

  * `release/` -- the tree to commit. **Parquet tables only.** Text files gzipped, payloads
    left out, and a `datapackage.json` and README written for this tree rather than copied
    from the build, because the build's describe files that packaging renames or omits.
  * `payloads-<version>.tar.gz` -- the sidecars, kept out of the release repository. Four
    fifths of the artifact and mostly third-party model output, so they are their own
    Zenodo record related with `isPartOf`.
  * `SHA256SUMS`, beside the output rather than inside it: a checksum sealed inside the
    thing it verifies proves nothing.

Three things it refuses to do, each because the earlier version did them:

  * Package inputs it has not verified. `manifest.output_sha256` was copied into
    `packaging.json` as provenance without ever being compared against the bytes on disk,
    so a changed, missing or extra file packaged successfully and the new checksums
    authenticated whatever was there.
  * Hand a partial build or one with blocking diagnostics to an operator with instructions
    to commit, tag and deposit it. "Blocking" was a label, not a blocker.
  * Delete or overwrite its own input. See `export_dataset/paths.py`.

    python -m scripts.package_dataset [--dataset dataset] [--out dist] [--development]
"""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import tarfile
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

PAYLOAD_DIR = "payloads"
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


# --- F03: verify before packaging -------------------------------------------------

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


# --- F04: a release blocker must block --------------------------------------------

def release_preflight(dataset, manifest):
    """Reasons this build must not be released. Empty means it may be."""
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
    return blockers


def build_release_tree(dataset, out, payload_archive=None):
    """Copy the dataset into `out`: Parquet as-is, text gzipped, CSV tables dropped."""
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
        if relative.parts and relative.parts[0] == PAYLOAD_DIR:
            continue
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
         json.dumps(docs.release_datapackage(manifest, packaged_paths | set(GENERATED_DOCS),
                                             payload_archive), indent=2, sort_keys=True)
         + "\n"),
        ("README.md", docs.release_readme(manifest, packaged_paths | set(GENERATED_DOCS),
                                          payload_archive)),
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
                    "payload_archive": payload_archive,
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


def pack_payloads(dataset, out, version):
    dataset, out = Path(dataset), Path(out)
    payloads = dataset / PAYLOAD_DIR
    if not payloads.is_dir():
        return None
    archive = out / ("payloads-%s.tar.gz" % version)
    with open(archive, "wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0,
                           compresslevel=6) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for path in sorted(payloads.rglob("*")):
                    if path.is_file():
                        info = tar.gettarinfo(str(path),
                                              arcname=str(path.relative_to(dataset)))
                        info.mtime = 0
                        info.uid = info.gid = 0
                        info.uname = info.gname = ""
                        with open(path, "rb") as handle:
                            tar.addfile(info, handle)
    return archive


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", default="dataset")
    parser.add_argument("--out", default="dist")
    parser.add_argument("--skip-payloads", action="store_true")
    parser.add_argument("--development", action="store_true",
                        help="package a build that is not releasable; output is labelled "
                             "and no deposit instruction is printed")
    args = parser.parse_args(argv)

    dataset, out = Path(args.dataset), Path(args.out)
    if not (dataset / "manifest.json").is_file():
        raise SystemExit("No built dataset at %s. Run `python -m scripts.export_dataset` "
                         "first." % dataset.resolve())
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

    archive = None
    if not args.skip_payloads:
        print("Payload archive ...")
        archive = pack_payloads(dataset, out, version)
        if archive:
            print("  %s  %.1f MB" % (archive, archive.stat().st_size / 1048576))

    print("Release tree ...")
    _manifest, packaging = build_release_tree(dataset, release,
                                              archive.name if archive else None)
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
              % (path.relative_to(release), size / 1048576, GITHUB_WARN_LIMIT // 1048576))
    if blocked:
        raise SystemExit(
            "Refusing to package: %d file(s) exceed GitHub's %d MB hard limit:\n  %s"
            % (len(blocked), GITHUB_FILE_LIMIT // 1048576,
               "\n  ".join("%s (%.1f MB)" % (p.relative_to(release), s / 1048576)
                           for p, s in blocked)))

    print("Checksums ...")
    lines = []
    for path in sorted(release.rglob("*")):
        if path.is_file():
            lines.append("%s  %s/%s" % (sha256_of(path), release.name,
                                        path.relative_to(release).as_posix()))
    if archive:
        lines.append("%s  %s" % (sha256_of(archive), archive.name))
    sums = out / "SHA256SUMS"
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("  %s  %d entries" % (sums, len(lines)))

    if args.development:
        print("\nDevelopment package at %s. Not releasable; see the blockers above."
              % release)
    else:
        print("\nDataset version %s. Commit %s/ to the release repository, tag it, and let "
              "the Zenodo webhook deposit it." % (version, release))
    return 0


if __name__ == "__main__":
    sys.exit(main())
