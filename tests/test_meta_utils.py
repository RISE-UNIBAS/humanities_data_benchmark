"""`meta_utils.load_json` and `get_meta`, whose stdout is part of their contract.

Both now sit on `results_index.read_json`, which is silent and returns a status. The
messages stayed behind, because a generator that cannot parse a file says so on stdout and
that is how a broken export gets noticed. So these tests assert what is printed as well as
what is returned.

They also pin the one deliberate widening: an unreadable file used to propagate its
OSError out of `load_json` and now returns None. That is inert on this corpus, since a
full export opens every file without trouble, but it is a real change and worth a test
rather than a comment.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import pytest

from scripts.ndr_export.meta_utils import get_meta, load_json


def test_load_json_returns_the_decoded_value_and_says_nothing(tmp_path, capsys):
    path = tmp_path / "meta.json"
    path.write_text('{"title": "Business letters"}', encoding="utf-8")

    assert load_json(path) == {"title": "Business letters"}
    assert capsys.readouterr().out == ""


def test_load_json_is_quiet_about_a_missing_file(tmp_path, capsys):
    """Absent is an ordinary state -- get_meta reports it, with a benchmark name attached."""
    assert load_json(tmp_path / "absent.json") is None
    assert capsys.readouterr().out == ""


def test_load_json_names_the_file_it_could_not_parse(tmp_path, capsys):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    assert load_json(path) is None
    assert "Failed to parse" in capsys.readouterr().out


def test_load_json_accepts_a_string_path(tmp_path, capsys):
    """Callers pass os.path.join results; the message must show the same text as before."""
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    assert load_json(str(path)) is None
    assert str(path) in capsys.readouterr().out


def test_load_json_distinguishes_an_empty_object_from_a_failure(tmp_path, capsys):
    path = tmp_path / "empty.json"
    path.write_text("{}", encoding="utf-8")

    assert load_json(path) == {}
    assert capsys.readouterr().out == ""


def test_load_json_returns_none_for_an_unreadable_file_instead_of_raising(tmp_path):
    """The documented widening: an OSError used to escape this function."""
    assert load_json(tmp_path) is None


@pytest.fixture
def benchmarks_dir(tmp_path, monkeypatch):
    """Point both modules' BENCHMARKS_PATH at a scratch tree.

    `benchmark_meta` reads the constant at call time, and `get_meta` builds the path it
    prints from `ndr_export`'s copy, so both have to move together.
    """
    monkeypatch.setattr("scripts.results_index.BENCHMARKS_PATH", tmp_path)
    monkeypatch.setattr("scripts.ndr_export.meta_utils.BENCHMARKS_PATH", tmp_path)
    return tmp_path


def test_get_meta_returns_the_metadata(benchmarks_dir):
    (benchmarks_dir / "business_letters").mkdir()
    (benchmarks_dir / "business_letters" / "meta.json").write_text(
        '{"title": "Business letters", "ranking": {"metric": "f1_macro"}}', encoding="utf-8")

    assert get_meta("business_letters")["ranking"] == {"metric": "f1_macro"}


def test_get_meta_falls_back_to_an_empty_dict(benchmarks_dir, caplog):
    """Three different failures, one return value, because every caller does meta.get()."""
    (benchmarks_dir / "missing").mkdir()

    (benchmarks_dir / "broken").mkdir()
    (benchmarks_dir / "broken" / "meta.json").write_text("{not json", encoding="utf-8")

    (benchmarks_dir / "null").mkdir()
    (benchmarks_dir / "null" / "meta.json").write_text("null", encoding="utf-8")

    for name in ("missing", "broken", "null"):
        assert get_meta(name) == {}, "%s should fall back to {}" % name


def test_get_meta_names_the_benchmark_it_could_not_read(benchmarks_dir, caplog):
    with caplog.at_level("ERROR"):
        get_meta("absent")
    assert "absent" in caplog.text and "Could not find" in caplog.text
