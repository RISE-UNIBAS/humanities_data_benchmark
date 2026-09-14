"""Package a built dataset for the release repository and for Zenodo.

Plan §6.1. The GitHub-Zenodo webhook deposits the repository's source zipball at the tag,
not the files attached to the release, so whatever should reach Zenodo has to be committed.
That plus GitHub's hard 100 MB per-file limit is what this script exists to satisfy.

It produces two things from a finished `dataset/`:

  * `release/` -- the tree to commit to the release repository. Parquet tables as they are,
    CSV copies and the source manifest gzipped, everything else copied. About 48 MB, and
    every file well under the limit. `scores_long.csv` is 206 MB and GitHub refuses it
    outright; gzipped it is around 13 MB.
  * `payloads-<version>.tar.gz` -- the sidecars, kept out of the release repository. They
    are 191 MB, four fifths of the artifact, and the part this project has least standing
    to license, being mostly third-party model output. If they are wanted they become their
    own Zenodo record, related with `isPartOf`.

Checksums go in `SHA256SUMS`, which is written beside the output rather than inside it: a
checksum sealed inside the thing it verifies proves nothing.

`packaging.json` records, for every file that was compressed, the name and hash it had in
the build and the name and hash it has here. Without it the release repository would hold
`scores_long.csv.gz` while `manifest.json` hashes `scores_long.csv`, and an auditor would
have no way to connect the two.

    python -m scripts.package_dataset [--dataset dataset] [--out dist]
"""
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import tarfile
from pathlib import Path

GITHUB_FILE_LIMIT = 100 * 1024 * 1024
"""Hard: a push containing a larger file is rejected outright."""

GITHUB_WARN_LIMIT = 50 * 1024 * 1024
"""Soft: GitHub warns, and the repository grows by this much per release forever."""

COMPRESS = (".csv", ".jsonl")
"""Text that compresses by an order of magnitude. Parquet is already compressed and gzip
would only make it bigger and unreadable to `pyarrow` without a decompression step."""

PAYLOAD_DIR = "payloads"


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


def build_release_tree(dataset, out):
    """Copy the dataset into `out`, compressing what is too big to commit."""
    dataset, out = Path(dataset), Path(out)
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
        if relative.parts and relative.parts[0] == PAYLOAD_DIR:
            continue

        if source.suffix in COMPRESS:
            target = out / relative.with_suffix(source.suffix + ".gz")
            target.parent.mkdir(parents=True, exist_ok=True)
            _gzip_to(source, target)
            packaging.append({
                "built_path": relative.as_posix(),
                "built_sha256": built.get(relative.as_posix()),
                "built_bytes": source.stat().st_size,
                "packaged_path": target.relative_to(out).as_posix(),
                "packaged_sha256": sha256_of(target),
                "packaged_bytes": target.stat().st_size,
                "transform": "gzip",
            })
        else:
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            packaging.append({
                "built_path": relative.as_posix(),
                "built_sha256": built.get(relative.as_posix()),
                "built_bytes": source.stat().st_size,
                "packaged_path": target.relative_to(out).as_posix(),
                "packaged_sha256": sha256_of(target),
                "packaged_bytes": target.stat().st_size,
                "transform": "copy",
            })

    (out / "packaging.json").write_text(
        json.dumps({"dataset_version": manifest.get("dataset_version"),
                    "schema_version": manifest.get("schema_version"),
                    "files": packaging}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return manifest, packaging


def check_sizes(out):
    """Refuse to hand over a tree GitHub will reject, and name what is close to the line."""
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
    # mtime and name pinned for the same reason the sidecars pin theirs: two packagings of
    # one build should produce one archive.
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
    args = parser.parse_args(argv)

    dataset, out = Path(args.dataset), Path(args.out)
    if not (dataset / "manifest.json").is_file():
        raise SystemExit("No built dataset at %s. Run `python -m scripts.export_dataset` "
                         "first." % dataset.resolve())

    out.mkdir(parents=True, exist_ok=True)
    release = out / "release"

    print("Release tree ...")
    manifest, packaging = build_release_tree(dataset, release)
    version = manifest.get("dataset_version") or "unknown"
    total = sum(entry["packaged_bytes"] for entry in packaging)
    print("  %s  %d files, %.1f MB" % (release, len(packaging), total / 1048576))
    if manifest.get("partial"):
        print("  WARNING: this build is partial and must not be released.")
    if manifest.get("source_worktree_dirty"):
        print("  WARNING: built from a dirty worktree; provenance is not commit-only.")

    blocked, warned = check_sizes(release)
    for path, size in warned:
        print("  note: %s is %.1f MB, over GitHub's %d MB warning threshold"
              % (path.relative_to(release), size / 1048576,
                 GITHUB_WARN_LIMIT // 1048576))
    if blocked:
        raise SystemExit(
            "Refusing to package: %d file(s) exceed GitHub's %d MB hard limit and cannot "
            "be committed:\n  %s"
            % (len(blocked), GITHUB_FILE_LIMIT // 1048576,
               "\n  ".join("%s (%.1f MB)" % (p.relative_to(release), s / 1048576)
                           for p, s in blocked)))

    archive = None
    if not args.skip_payloads:
        print("Payload archive ...")
        archive = pack_payloads(dataset, out, version)
        if archive:
            print("  %s  %.1f MB" % (archive, archive.stat().st_size / 1048576))

    # Beside the output, never inside it.
    print("Checksums ...")
    lines = []
    for path in sorted(release.rglob("*")):
        if path.is_file():
            lines.append("%s  release/%s" % (sha256_of(path),
                                             path.relative_to(release).as_posix()))
    if archive:
        lines.append("%s  %s" % (sha256_of(archive), archive.name))
    sums = out / "SHA256SUMS"
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("  %s  %d entries" % (sums, len(lines)))

    print("\nDataset version %s. Commit %s/ to the release repository, tag it, and let the "
          "Zenodo webhook deposit it." % (version, release))
    return 0


if __name__ == "__main__":
    sys.exit(main())
