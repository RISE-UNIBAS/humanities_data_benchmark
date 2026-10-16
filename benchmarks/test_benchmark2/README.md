# Test Benchmark 2

This is an incomplete framework scaffold, hidden from research benchmark listings (`display: false`) and excluded from BenchmarkCard requirements. Its scores are placeholders and must not be used to compare models.

## Files and current behaviour

- [texts/file.txt](texts/file.txt) is empty. There is no input image of Luther's theses in this fixture.
- [prompts/a_prompt.txt](prompts/a_prompt.txt) asks for persons, places and dates, not for thesis extraction.
- [ground_truths/luther.json](ground_truths/luther.json) does not match the input basename `file`, so it is not the reference the normal runner would load for that input.
- There is no `dataclass.py` response schema.

[benchmark.py](benchmark.py) returns constant per-request values (`score: 66`, `scoresdfsdf_2: 77`, `score_3: 88`) without comparing content, and the benchmark aggregate is `{"score": "niy"}`. The image-resizing override has no input image to act on.

## Work needed before use

Supply a non-empty input and matching ground truth, choose a consistent task and response format, and implement and test meaningful scoring. Existing rows in [benchmarks_tests.csv](../benchmarks_tests.csv) are scaffold configurations, not evidence that this is a usable research benchmark. Avoid paid provider runs until those pieces are implemented.
