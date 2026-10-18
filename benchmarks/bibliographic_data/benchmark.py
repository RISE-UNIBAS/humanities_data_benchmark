"""Benchmark implementation for bibliographic_data.

Every terminal field of the ground truth outside `metadata` is compared with the response at the
same path and scored with calculate_fuzzy_score; the page score is the mean over those fields.
Response entries are first aligned to ground-truth entries in page order: the alignment keeps
both orders and maximises the summed entry similarity, so a missed or split entry costs only
itself. A ground-truth entry without a counterpart scores 0 in every field; extra response
entries are not scored. A response whose Document is nested under a single wrapper key is
unwrapped; an unparseable response misses every field.
"""
import logging
from typing import Dict

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score

PRINTED_PAGE = {"page_2": 1, "page_3": 2, "page_4": 3, "page_5": 4, "page_10": 9}


def _entry_similarity(response_entry, truth_entry):
    keys = get_all_keys(truth_entry)
    if not keys or not isinstance(response_entry, dict):
        return 0.0
    return sum(calculate_fuzzy_score(get_nested_value(response_entry, k), get_nested_value(truth_entry, k))
               for k in keys) / len(keys)


def align_entries(response_entries, truth_entries):
    """Response entry for each ground-truth entry (or {}), in an order-preserving alignment."""
    n, m = len(truth_entries), len(response_entries)
    sim = [[_entry_similarity(r, t) for r in response_entries] for t in truth_entries]
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            best[i][j] = max(best[i + 1][j], best[i][j + 1], sim[i][j] + best[i + 1][j + 1])
    aligned, i, j = [], 0, 0
    while i < n:
        if j < m and best[i][j] == sim[i][j] + best[i + 1][j + 1] and sim[i][j] > 0:
            aligned.append(response_entries[j])
            i, j = i + 1, j + 1
        elif j < m and best[i][j] == best[i][j + 1]:
            j += 1
        else:
            aligned.append({})
            i += 1
    return aligned


class BibliographicData(Benchmark):

    score_unparseable_as_miss = True

    def get_prompt_kwargs(self, basename: str, filenames) -> Dict:
        """`page_number` is the number in the file name (prompt.txt); `printed_page_number` the page
        as printed (prompt_v2.txt), which matches `metadata.page_number` in the ground truth."""
        page_number = basename.split("_")[-1].split(".")[0]
        return {
            "page_number": page_number,
            "printed_page_number": PRINTED_PAGE.get(basename, page_number),
        }

    def score_benchmark(self, all_scores):
        if not all_scores:
            return {"fuzzy": 0.0}
        total_score = 0
        for score in all_scores:
            logging.debug(f"Fuzzy score: {score['fuzzy']}")
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)

        if isinstance(data, list):
            data = {"entries": data}
        if isinstance(data, dict) and "entries" not in data and len(data) == 1:
            inner = next(iter(data.values()))
            if isinstance(inner, dict) and "entries" in inner:
                data = inner
        if not isinstance(data, dict):
            data = {}
        entries = data.get("entries") if isinstance(data.get("entries"), list) else []
        data = {**data, "entries": align_entries(entries, ground_truth.get("entries", []))}

        my_keys = get_all_keys(ground_truth)

        avg_score = 0
        total_keys = 0
        field_scores = {}
        for k in my_keys:
            # Skip metadata fields to focus on bibliographic entries
            if k.startswith("metadata"):
                continue
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(ground_truth, k)

            score = calculate_fuzzy_score(test_value, gold_value)
            field_scores[k] = {
                'response': test_value,
                'ground_truth': gold_value,
                'score': score,
            }
            avg_score += score
            total_keys += 1

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        # Record what was compared, not just the average. The scorer already has the
        # two values and the similarity it assigned; keeping them lets the comparison
        # view show this scorer's own judgement instead of re-deriving one that would
        # disagree with it. Same shape as library_cards, which has always done this.
        return {"fuzzy": avg_score, "field_scores": field_scores}
