# Test Benchmark 1

This is a framework smoke test for image input, structured responses and scoring. It is hidden from research benchmark listings (`display: false`) and deliberately excluded from BenchmarkCard requirements.

## Input and output

The input is one newspaper-page image, [jaccuse.jpg](images/jaccuse.jpg), of Émile Zola's *J'accuse*. The [prompt](prompts/prompt.txt) requests named entities; the [PersonList schema](dataclass.py) accepts `{"persons_mentioned": ["name", "..."]}`. The reference names are in [jaccuse.json](ground_truths/jaccuse.json).

## Scoring and limitations

[benchmark.py](benchmark.py) lowercases names and removes combining accents, then uses Python's `difflib.SequenceMatcher`. Each reference person counts as found when its best response-name similarity is at least 0.8. The metric named `fuzzy` is the fraction of reference persons found, from 0 to 1; higher is better. It is not a count of all entity types or an F1 score.

Extra predicted names incur no penalty, and a prediction can match more than one reference person. The benchmark score averages object scores; there is only one object. The scorer returns zero for `parsed=None`, but the normal schema-configured runner skips unparseable responses before calling it. This single-page fixture does not support general model-quality claims.

## Running the fixture

From the repository root, after the [provider setup](../../README.md#quick-start), run:

```console
python scripts/run_single_test.py --test_id T0001
```

This makes a paid provider request unless a stored result is reused. Test definitions are in [benchmarks_tests.csv](../benchmarks_tests.csv). No provider call is needed to run the existing local scoring tests.
