import logging
from difflib import SequenceMatcher

import unicodedata

from scripts.benchmark_base import Benchmark


class TestBenchmark(Benchmark):

    def score_benchmark(self, all_scores):
        total_score = 0
        for score in all_scores:
            logging.debug(f"Fuzzy score: {score['fuzzy']}")
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self, object_basename, response, ground_truth):
        structured_response = response.parsed

        persons_found = 0
        for item in ground_truth["persons_mentioned"]:
            best_match, score = score_best_match(item, structured_response["persons_mentioned"])
            if score >= 0.8:
                persons_found += 1

        total_persons = len(ground_truth["persons_mentioned"])
        score = persons_found / total_persons
        return {"fuzzy": score}


def normalize_name(s: str) -> str:
    # lower & remove accents
    s = s.lower()
    s = unicodedata.normalize('NFKD', s)
    return "".join(c for c in s if not unicodedata.combining(c))


def score_best_match(gt_name, extracted_names):
    gt_norm = normalize_name(gt_name)

    best_score = 0.0
    best_name = None

    for name in extracted_names:
        score = SequenceMatcher(None, gt_norm, normalize_name(name)).ratio()
        if score > best_score:
            best_score = score
            best_name = name

    return best_name, best_score