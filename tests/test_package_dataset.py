"""Packaging a built dataset for the release repository.

Plan §6.1 chose to commit the artifact to a release repository rather than attach it to a
release, because the GitHub-Zenodo webhook deposits the repository's source zipball and
ignores attached assets. That makes GitHub's 100 MB per-file limit a release-blocking
constraint rather than a nuisance, and the point of most of what follows is that the
packager refuses to hand over a tree that cannot be pushed.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import gzip
import json
from pathlib import Path

import pytest

from scripts import package_dataset as P


@pytest.fixture
def built(tmp_path):
    """A miniature `dataset/`: one of each kind of file the packager must handle."""
    d = tmp_path / "dataset"
    (d / "payloads").mkdir(parents=True)
    (d / "scores_long.csv").write_text("a,b\n1,2\n" * 500, encoding="utf-8")
    (d / "runs.parquet").write_bytes(b"PAR1fake")
    (d / "source_manifest.jsonl").write_text('{"path":"x"}\n' * 200, encoding="utf-8")
    (d / "README.md").write_text("# readme\n", encoding="utf-8")
    (d / "payloads" / "business_letters.jsonl.gz").write_bytes(b"\x1f\x8bfakegz")
    (d / "manifest.json").write_text(json.dumps({
        "dataset_version": "2026-09-09.1",
        "schema_version": "1.0.0",
        "partial": False,
        "output_sha256": {"scores_long.csv": "deadbeef", "runs.parquet": "cafe"},
    }), encoding="utf-8")
    return d


def test_text_is_compressed_and_parquet_is_not(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    assert (out / "scores_long.csv.gz").is_file()
    assert not (out / "scores_long.csv").exists()
    assert (out / "source_manifest.jsonl.gz").is_file()
    assert (out / "runs.parquet").is_file(), (
        "parquet is already compressed; gzipping it would grow the file and stop pyarrow "
        "reading it directly")
    assert (out / "README.md").is_file()


def test_payloads_are_left_out_of_the_release_tree(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    assert not (out / "payloads").exists(), (
        "the sidecars are four fifths of the artifact and mostly third-party model "
        "output; §6.1 keeps them out of the release repository")


def test_a_compressed_file_still_unpacks_to_the_original(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    original = (built / "scores_long.csv").read_bytes()
    with gzip.open(out / "scores_long.csv.gz", "rb") as handle:
        assert handle.read() == original


def test_packaging_json_connects_the_two_names(built, tmp_path):
    """Without it the repo holds scores_long.csv.gz while the manifest hashes .csv."""
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    entries = dict((e["packaged_path"], e)
                   for e in json.loads((out / "packaging.json").read_text())["files"])
    entry = entries["scores_long.csv.gz"]
    assert entry["built_path"] == "scores_long.csv"
    assert entry["built_sha256"] == "deadbeef", "the hash the build recorded"
    assert entry["transform"] == "gzip"
    assert entry["packaged_sha256"] and entry["packaged_sha256"] != entry["built_sha256"]


def test_gzip_output_is_byte_stable(built, tmp_path):
    """Two packagings of one build must produce one release tree."""
    a, b = tmp_path / "a", tmp_path / "b"
    P.build_release_tree(built, a)
    P.build_release_tree(built, b)
    assert (a / "scores_long.csv.gz").read_bytes() == (b / "scores_long.csv.gz").read_bytes()


def test_an_oversized_file_is_reported_as_blocking(tmp_path):
    out = tmp_path / "release"
    out.mkdir()
    (out / "huge.parquet").write_bytes(b"\0" * (P.GITHUB_FILE_LIMIT + 1))
    (out / "big.parquet").write_bytes(b"\0" * (P.GITHUB_WARN_LIMIT + 1))
    (out / "small.parquet").write_bytes(b"\0")
    blocked, warned = P.check_sizes(out)
    assert [p.name for p, _ in blocked] == ["huge.parquet"]
    assert [p.name for p, _ in warned] == ["big.parquet"]


def test_packaging_refuses_a_tree_that_cannot_be_pushed(built, tmp_path, monkeypatch):
    """The whole point: fail here, not at `git push` after a four-minute build."""
    monkeypatch.setattr(P, "GITHUB_FILE_LIMIT", 10)
    monkeypatch.setattr(P, "GITHUB_WARN_LIMIT", 5)
    with pytest.raises(SystemExit, match="hard limit"):
        P.main(["--dataset", str(built), "--out", str(tmp_path / "dist"),
                "--skip-payloads"])


def test_checksums_are_written_beside_the_output_not_inside_it(built, tmp_path):
    dist = tmp_path / "dist"
    P.main(["--dataset", str(built), "--out", str(dist), "--skip-payloads"])
    sums = dist / "SHA256SUMS"
    assert sums.is_file()
    assert not (dist / "release" / "SHA256SUMS").exists(), (
        "a checksum sealed inside the thing it verifies proves nothing")
    assert "release/runs.parquet" in sums.read_text()


def test_a_missing_dataset_is_refused_with_a_usable_message(tmp_path):
    with pytest.raises(SystemExit, match="No built dataset"):
        P.main(["--dataset", str(tmp_path / "absent"), "--out", str(tmp_path / "dist")])
