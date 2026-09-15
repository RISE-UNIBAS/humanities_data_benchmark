"""Packaging a built dataset for the release repository.

The artifact is committed to a release repository rather than attached to a release,
because the GitHub-Zenodo webhook deposits the repository's source zipball and ignores
attached assets. That makes GitHub's 100 MB per-file limit a release-blocking constraint
rather than a nuisance.

The findings-level tests -- verification, preflight, described paths -- live in
`test_audit_findings.py` beside the audit entries they close. What stays here is the
mechanics: what gets compressed, what gets dropped, and whether the output is stable.

Note the fixture. It computes real hashes for `output_sha256`. The version this replaces
used the literals `deadbeef` and `cafe` and asserted that one of them was copied into the
output, which the audit fairly cited as evidence that packaging never checked the bytes it
was handed.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import gzip
import json

import pytest

from scripts import package_dataset as P


@pytest.fixture(autouse=True)
def reconciliation_tested_separately(monkeypatch):
    """Preflight now reconciles against the frontend export, which is a real file in the
    repository covering 2,371 runs. Every fixture here is a miniature dataset of two or
    three rows, so a genuine reconciliation would report the whole corpus as missing and
    say nothing about the mechanics these tests are for. The reconciliation itself is
    tested below against a stubbed crosscheck."""
    monkeypatch.setattr(P, "_reconciliation_blockers", lambda dataset: [])


@pytest.fixture
def built(tmp_path):
    """A miniature `dataset/`: one of each kind of file the packager must handle."""
    d = tmp_path / "dataset"
    (d / "payloads").mkdir(parents=True)
    (d / "scores_long.csv").write_text("a,b\n1,2\n" * 500, encoding="utf-8")
    (d / "scores_long.parquet").write_bytes(b"PAR1fake-scores")
    (d / "runs.parquet").write_bytes(b"PAR1fake-runs")
    (d / "coverage.csv").write_text("table,column\nruns,run_id\n", encoding="utf-8")
    (d / "source_manifest.jsonl").write_text('{"path":"x"}\n' * 200, encoding="utf-8")
    (d / "payloads" / "business_letters.jsonl.gz").write_bytes(b"\x1f\x8bfakegz")

    declared = {}
    for path in sorted(d.rglob("*")):
        if path.is_file():
            declared[path.relative_to(d).as_posix()] = P.sha256_of(path)

    (d / "manifest.json").write_text(json.dumps({
        "dataset_version": "2026-09-09.2",
        "schema_version": "1.1.0",
        "data_cutoff": "2026-09-09",
        "partial": False,
        "source_commit": "abc1234567890",
        "source_worktree_dirty": False,
        "row_counts": {"runs": 1, "requests": 1, "scores_long": 1, "metrics": 1},
        "inventory": {"files_hashed": len(declared)},
        "output_sha256": declared,
    }), encoding="utf-8")
    return d


def test_parquet_ships_as_is_and_text_is_compressed(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    assert (out / "runs.parquet").is_file(), (
        "parquet is already compressed; gzipping it would grow the file and stop pyarrow "
        "reading it directly")
    assert (out / "source_manifest.jsonl.gz").is_file()
    assert (out / "coverage.csv.gz").is_file()


def test_table_csvs_are_dropped_entirely(built, tmp_path):
    """Parquet is the lossless copy, and shipping both invites the lossy one."""
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    assert not (out / "scores_long.csv").exists()
    assert not (out / "scores_long.csv.gz").exists()
    assert (out / "scores_long.parquet").is_file()


def test_payloads_are_left_out_of_the_release_tree(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    assert not (out / "payloads").exists(), (
        "the sidecars are four fifths of the artifact and mostly third-party model "
        "output; they are kept out of the release repository")


def test_a_compressed_file_still_unpacks_to_the_original(built, tmp_path):
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    original = (built / "source_manifest.jsonl").read_bytes()
    with gzip.open(out / "source_manifest.jsonl.gz", "rb") as handle:
        assert handle.read() == original


def test_packaging_json_connects_the_two_names(built, tmp_path):
    """Without it the repo holds source_manifest.jsonl.gz while the manifest hashes the
    uncompressed name, and the two cannot be reconciled."""
    out = tmp_path / "release"
    P.build_release_tree(built, out)
    entries = dict((e["packaged_path"], e)
                   for e in json.loads((out / "packaging.json").read_text())["files"])

    entry = entries["source_manifest.jsonl.gz"]
    assert entry["built_path"] == "source_manifest.jsonl"
    assert entry["built_sha256"] == P.sha256_of(built / "source_manifest.jsonl")
    assert entry["transform"] == "gzip"
    assert entry["packaged_sha256"] != entry["built_sha256"]

    assert entries["README.md"]["transform"] == "generated_for_release", (
        "the release README is written for this tree, not copied from the build")


def test_gzip_output_is_byte_stable(built, tmp_path):
    """Two packagings of one build must produce one release tree."""
    a, b = tmp_path / "a", tmp_path / "b"
    P.build_release_tree(built, a)
    P.build_release_tree(built, b)
    assert (a / "source_manifest.jsonl.gz").read_bytes() == \
        (b / "source_manifest.jsonl.gz").read_bytes()


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
    """Fail here, not at `git push` after a four-minute build."""
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


def test_a_development_package_is_labelled_and_not_told_to_deposit(built, tmp_path, capsys):
    manifest = json.loads((built / "manifest.json").read_text())
    manifest["partial"] = True
    (built / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    declared = manifest["output_sha256"]
    declared["manifest.json"] = None
    del declared["manifest.json"]

    dist = tmp_path / "dist"
    P.main(["--dataset", str(built), "--out", str(dist), "--skip-payloads",
            "--development"])
    out = capsys.readouterr().out
    assert (dist / "release-development").is_dir()
    assert "deposit" not in out and "Not releasable" in out


def test_a_missing_dataset_is_refused_with_a_usable_message(tmp_path):
    with pytest.raises(SystemExit, match="No built dataset"):
        P.main(["--dataset", str(tmp_path / "absent"), "--out", str(tmp_path / "dist")])


# --- reconciliation is part of the release decision ---------------------------------

REAL_RECONCILIATION = P._reconciliation_blockers
"""Captured at import, before the autouse fixture stubs it out."""


class _Crosscheck:
    """Enough of `crosscheck` to exercise the preflight branch without a corpus."""

    def __init__(self, exists=True, findings=(), raises=None):
        self.FRONTEND_EXPORT = _Export(exists)
        self._findings = list(findings)
        self._raises = raises

    def load_frontend(self):
        if self._raises:
            raise self._raises
        return {}

    def load_dataset(self, dataset_dir):
        return [], [], []

    def compare(self, runs, requests, scores, frontend):
        return self._findings, 2371


class _Export:
    def __init__(self, exists):
        self._exists = exists

    def is_file(self):
        return self._exists

    def __str__(self):
        return "collected_results/test_runs_export.json"

    def __fspath__(self):
        return str(self)


def _blockers(monkeypatch, stub):
    import scripts.export_dataset as pkg
    monkeypatch.setattr(pkg, "crosscheck", stub, raising=False)
    return REAL_RECONCILIATION("dataset")


def test_an_unreconciled_build_is_not_releasable(monkeypatch):
    """Absent is not clean. Nothing compared the two pipelines."""
    blockers = _blockers(monkeypatch, _Crosscheck(exists=False))
    assert len(blockers) == 1 and "nothing reconciled this build" in blockers[0]
    assert "generate_all" in blockers[0], "say how to fix it"


def test_a_crosscheck_finding_blocks_the_release(monkeypatch):
    blockers = _blockers(monkeypatch, _Crosscheck(findings=[
        {"check": "pricing", "detail": "T0001@2026-01-01: frontend resolved 2.0"}]))
    assert len(blockers) == 1
    assert "pricing" in blockers[0] and "T0001@2026-01-01" in blockers[0]


def test_a_reconciled_build_carries_no_blocker(monkeypatch):
    assert _blockers(monkeypatch, _Crosscheck()) == []


def test_a_crosscheck_that_cannot_run_blocks_rather_than_crashes(monkeypatch):
    blockers = _blockers(monkeypatch, _Crosscheck(raises=ValueError("truncated json")))
    assert len(blockers) == 1 and "could not run" in blockers[0]
    assert "truncated json" in blockers[0], "keep the reason"
