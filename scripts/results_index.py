"""Read-only access to the result tree, the test CSV and the benchmark metadata.

The export and scoring path walked `results/` in six places and read
`benchmarks_tests.csv` in two, each with its own idea of what to skip. That was tolerable
while every caller was the frontend export, which may legitimately drop what it cannot
chart. It stops being tolerable with a dataset export in the tree, because that one is
required to drop nothing: a run whose test id is not in the CSV, a request file that will
not parse and a run with no `scoring.json` are all rows it must emit, with a diagnostic,
rather than silences it must explain later.

`generate_date_report.py`, `generate_test_report.py` and `inject_costs.py` still keep their
own iteration and are deliberately untouched: the first two only ever read one date or one
run, and the third writes back into `results/`, which is not this module's business.

So the walk here is complete and the filtering is explicit. `iter_run_dirs` yields every
run directory and `iter_request_records` yields every request file, malformed included;
`known_tests` is the frontend's "skip unknown ids" rule, extracted and named, applied by
the callers that want it. Nothing here decides what is worth keeping.

Three rules this module keeps, each for a reason that bit somebody:

  * It is silent. `print` is observable behaviour for these tools -- the export's
    "Warning: No test config found" lines are how a missing row is noticed -- so every
    message stays at its call site and failures come back as data (`JsonRead.status`).
  * It has no module-level state. `tests/conftest.py` puts both the repo root and
    `scripts/` on `sys.path`, so this module can legitimately exist twice in one process
    as `results_index` and `scripts.results_index`. Two stateless copies are harmless;
    two caches would not be. For the same reason, nothing here should be `isinstance`-d --
    the NamedTuples are tuples, duck-type them.
  * It knows no metric names, no status vocabulary and no prices, and it imports nothing
    from `scripts` or `benchmarks`. The frontend and the dataset export disagree about
    what a score means and about whether an unknown id is a skip or a row, so those
    decisions belong to them. In particular this module never reaches
    `Benchmark.load_saved_answer`, which recalculates missing costs at today's prices --
    fine for the runner, wrong for anything reporting what a run actually recorded.

Importing this as `scripts.results_index` runs `scripts/__init__.py`, which creates a
`logs/` directory, configures root logging and loads the pricing table. That is inherited,
not caused here, and the pricing table it loads is not used by anything in this module.
"""
import csv
import json
import re
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
RESULTS_PATH = PROJECT_ROOT / "results"
TEST_RUNS_PATH = PROJECT_ROOT / "test_runs"
"""Ad-hoc runs, same `<date>/<id>/` shape as `results/` but ids absent from the CSV."""

BENCHMARKS_PATH = PROJECT_ROOT / "benchmarks"
TESTS_CSV = BENCHMARKS_PATH / "benchmarks_tests.csv"
COLLECTED_RESULTS_PATH = PROJECT_ROOT / "collected_results"


JSON_STATUSES = ("ok", "missing", "unreadable", "invalid")


class JsonRead(NamedTuple):
    """A JSON file read attempt: the value, or why there isn't one."""

    value: object
    """The decoded JSON when `status` is "ok", otherwise None."""

    status: str
    """One of `JSON_STATUSES`."""

    error: str
    """The exception text for "unreadable" and "invalid", otherwise None."""


def read_json(path):
    """Decode a JSON file without raising, so a bad file is data rather than a crash.

    The status matters as much as the value: a file holding `null`, `0`, `[]` or `{}`
    reads as "ok" with a falsy value, which is a different fact from "missing". Callers
    that collapse both to None cannot tell an empty usage block from an absent one, and
    the dataset export is required to.
    """
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as handle:
            return JsonRead(json.load(handle), "ok", None)
    except FileNotFoundError:
        return JsonRead(None, "missing", None)
    except json.JSONDecodeError as error:
        return JsonRead(None, "invalid", str(error))
    except UnicodeDecodeError as error:
        # Not decodable as UTF-8. Previously this escaped and aborted the whole
        # extraction; it is an unreadable file like any other, and the export's job is to
        # record it and keep its bytes rather than stop.
        return JsonRead(None, "invalid", str(error))
    except OSError as error:
        return JsonRead(None, "unreadable", str(error))


def read_test_rows(path=TESTS_CSV):
    """Every row of the test CSV in file order, exactly as `csv.DictReader` gives it."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class TestCatalog:
    """The test CSV, with the views its readers have grown, computed once.

    Held as an object rather than module functions because the callers that need it walk
    2,371 run directories: `iter_run_inputs` re-read and re-parsed all 1,741 rows for
    every one of them. Views are memoised on the instance, never on the module.
    """

    __test__ = False
    """`pytest.ini` collects `Test*` classes, and a test module that imports this one
    would otherwise get a collection warning for it. This is not a test class."""

    def __init__(self, rows):
        self.rows = tuple(rows)
        self._raw_by_id = None
        self._typed_rows = None
        self._typed_by_id = None
        self._benchmark_map = None

    @classmethod
    def load(cls, path=TESTS_CSV):
        return cls(read_test_rows(path))

    def raw_by_id(self):
        """{test_id: row}, ids stripped, blank ids dropped, later rows winning."""
        if self._raw_by_id is None:
            rows = {}
            for row in self.rows:
                test_id = (row.get("id") or "").strip()
                if test_id:
                    rows[test_id] = row
            self._raw_by_id = rows
        return self._raw_by_id

    def typed_rows(self):
        """Rows with empty strings as None, `temperature` float and `legacy_test` bool.

        The order of the branches is load-bearing and is kept from `get_all_tests`: the
        empty-string test runs first, so a blank `temperature` is None rather than 0.0
        and a blank `legacy_test` is None rather than False. Callers read the difference
        between "not configured" and "configured false".
        """
        if self._typed_rows is None:
            typed = []
            for row in self.rows:
                cleaned = {}
                for key, value in row.items():
                    if value == "":
                        cleaned[key] = None
                    elif key == "temperature" and value:
                        cleaned[key] = float(value)
                    elif key == "legacy_test":
                        cleaned[key] = value.lower() == "true"
                    else:
                        cleaned[key] = value
                typed.append(cleaned)
            self._typed_rows = typed
        return self._typed_rows

    def typed_by_id(self):
        if self._typed_by_id is None:
            self._typed_by_id = dict((row.get("id"), row) for row in self.typed_rows()
                                     if row.get("id"))
        return self._typed_by_id

    def benchmark_map(self):
        """{test_id: benchmark}. A run directory does not record its own benchmark."""
        if self._benchmark_map is None:
            self._benchmark_map = dict(
                (test_id, (row.get("name") or "").strip())
                for test_id, row in self.raw_by_id().items()
                if (row.get("name") or "").strip())
        return self._benchmark_map

    def benchmark_of(self, test_id):
        return self.benchmark_map().get(test_id)

    def rules_of(self, test_id):
        """The run's `rules`, parsed as `Benchmark.__init__` parses it.

        None when absent or unusable. Not decoration: `personnel_cards` reads which
        fields to score out of it, so scoring a run without its rules scores a different
        field set than the run did.
        """
        raw = (self.raw_by_id().get(test_id) or {}).get("rules")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return None

    def __contains__(self, test_id):
        return test_id in self.raw_by_id()


def benchmark_names():
    """Benchmark directory names; a directory without a meta.json is not a benchmark."""
    if not BENCHMARKS_PATH.is_dir():
        return []
    return sorted(entry.name for entry in BENCHMARKS_PATH.iterdir()
                  if entry.is_dir() and not entry.name.startswith(".")
                  and (entry / "meta.json").is_file())


def benchmark_meta(name):
    """A benchmark's meta.json as a `JsonRead`, so absent and unparseable stay distinct."""
    return read_json(BENCHMARKS_PATH / name / "meta.json")


class RunDir(NamedTuple):
    """One stored run directory, `<root>/<date>/<test_id>/`."""

    path: Path
    date: str
    """The date directory's name. Not parsed and not validated as a date."""

    test_id: str
    """The run directory's name. Not validated against the CSV."""

    run_id: str
    """`<test_id>@<date>`, the dataset export's key for a stored run in a snapshot."""


def iter_run_dirs(root=RESULTS_PATH, newest_first=False):
    """Every run directory under `root`, date-major, both levels sorted.

    The complete walk: a run with an unknown test id, a run with no `scoring.json`, a run
    with no request files and a run whose every file is corrupt are all yielded. Callers
    that want less apply a named filter -- see `known_tests`.

    Sorted rather than in directory order so the same inputs give the same output on any
    filesystem; on NTFS the two already agree, on ext4 they do not.
    """
    root = Path(root)
    if not root.is_dir():
        return
    dates = sorted((p for p in root.iterdir() if p.is_dir()), reverse=newest_first)
    for date_dir in dates:
        for run_dir in sorted((p for p in date_dir.iterdir() if p.is_dir()),
                              reverse=newest_first):
            yield RunDir(run_dir, date_dir.name, run_dir.name,
                         "%s@%s" % (run_dir.name, date_dir.name))


def known_tests(run_dirs, catalog, benchmark=None):
    """Yields (run, benchmark) for runs whose test id is in the CSV, dropping the rest.

    The frontend's rule, named. What it drops is recoverable by differencing against
    `iter_run_dirs`, and it is deliberately not reported here: an unknown id is a skip for
    the frontend and a row for the dataset export, and only the caller knows which.
    """
    mapping = catalog.benchmark_map()
    for run in run_dirs:
        name = mapping.get(run.test_id)
        if name and (benchmark is None or name == benchmark):
            yield run, name


REQUEST_FILE = re.compile(r"^request_(?P<stem>.+)\.json$")


def object_id_of(file_name, test_id, fallback_prefix=None):
    """The input's identity, which exists only in the request filename.

    The prefix is usually the directory's test id, but not always: 4,296 files in 188
    early run directories store `request_T01_jaccuse.json` under `T0001`, because the ids
    were re-padded without renaming the files and two padding widths are in use. So the
    directory id is tried first and a prefix observed in the directory is the fallback.
    Returns None rather than guessing when neither applies -- a greedy split on
    underscores would silently mangle ids like `Se_18_Bilanz1967_page_4`.
    """
    match = REQUEST_FILE.match(file_name)
    if not match:
        return None
    stem = match.group("stem")
    for prefix in (test_id, fallback_prefix):
        if prefix and stem.startswith(prefix + "_"):
            object_id = stem[len(prefix) + 1:]
            return object_id or None
    return None


def observed_prefix(file_names):
    """The prefix actually used in a run directory, from its first request file."""
    for name in sorted(file_names):
        match = REQUEST_FILE.match(name)
        if match:
            return match.group("stem").split("_")[0]
    return None


class RequestFile(NamedTuple):
    path: Path
    name: str
    object_id: str
    """None when neither prefix resolves. The file is still yielded; that is a diagnostic
    for the caller, not a reason to lose it."""


class RunFiles(NamedTuple):
    run: RunDir
    requests: tuple
    """`RequestFile`s, sorted by filename."""

    prefix: str
    """`observed_prefix` of the directory; None when it holds no request file."""

    scoring_path: Path
    """`scoring.json`, which may not exist."""


def _as_run(run):
    """Accepts a RunDir, a Path or a str, so callers holding a bare path still work."""
    if isinstance(run, RunDir):
        return run
    path = Path(run)
    return RunDir(path, path.parent.name, path.name,
                  "%s@%s" % (path.name, path.parent.name))


def read_run(run):
    """One directory listing: the run's request files and where its scoring would be."""
    run = _as_run(run)
    names = sorted(entry.name for entry in run.path.glob("request_*.json"))
    fallback = observed_prefix(names)
    requests = tuple(
        RequestFile(run.path / name, name, object_id_of(name, run.test_id, fallback))
        for name in names)
    return RunFiles(run, requests, fallback, run.path / "scoring.json")


def _as_files(run):
    return run if isinstance(run, RunFiles) else read_run(run)


def iter_request_files(run):
    return iter(_as_files(run).requests)


def read_scoring(run):
    return read_json(_as_files(run).scoring_path)


def iter_request_records(run):
    """Yields (RequestFile, JsonRead) for every request file, malformed ones included.

    The completeness rule made mechanical: a caller that wants only the readable records
    tests `read.status`, and one that must account for every file already has it.
    """
    for request in _as_files(run).requests:
        yield request, read_json(request.path)


def first_request(run):
    """The first request file and its read, whether or not it parsed. None if there are none."""
    for request, read in iter_request_records(run):
        return request, read
    return None


def first_provider_model(run):
    """Who served this run, from the first stored record naming both.

    A run-level answer to a per-request question: the frontend needs one label per run,
    but the records are what actually identify each response, and they can disagree with
    each other and with the test config.
    """
    for _request, read in iter_request_records(run):
        data = read.value
        if isinstance(data, dict) and data.get("provider") and data.get("model"):
            return data["provider"], data["model"]
    return None, None
