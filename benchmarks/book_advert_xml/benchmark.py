"""Benchmark implementation for Book Advert XML files (malformed) from Avisblatt.

The score compares the model's edits with the reference's edits, both taken against the
advert's input. Before diffing, every string is normalised the same way: whitespace removed,
UTF-8 that was read as Mac Roman repaired, and each closing tag that follows plain text which
follows another closing tag moved up to that closing tag. Tokens are whole tags, character
references and single characters. An edit is a deleted, inserted or substituted token at an input position; renaming
either tag of a mismatched PRICE/PRIZE pair to match the other counts as the same edit. The
advert score is the F1 of matched edits; an unparseable answer misses every edit.
"""
import difflib
import json
import os
import re
from collections import Counter

from scripts.benchmark_base import Benchmark

TEXTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts")
TOKEN = re.compile(r"<[^<>]*>|&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);|.", re.S)
NON_ASCII = re.compile(r"[^\x00-\x7f]+")
PRICE_TAGS = {"<PRICE>", "<PRIZE>", "</PRICE>", "</PRIZE>"}


def _is_tag(token):
    return len(token) > 2 and token[0] == "<" and token[-1] == ">"


def _demojibake(text):
    def repair(match):
        try:
            return match.group().encode("mac_roman").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return match.group()
    return NON_ASCII.sub(repair, text)


def tokens(xml):
    """Normalised token list of an XML string."""
    out, after_close = [], None
    for token in TOKEN.findall(_demojibake(re.sub(r"\s+", "", xml or ""))):
        if _is_tag(token) and token.startswith("</"):
            if after_close is None:
                out.append(token)
                after_close = len(out)
            else:
                out.insert(after_close, token)
                after_close += 1
        else:
            out.append(token)
            if _is_tag(token):
                after_close = None
    return out


def _mismatched_pairs(source):
    """Map each tag index of a mismatched PRICE/PRIZE pair to the pair's opening index."""
    pairs, open_at = {}, None
    for i, token in enumerate(source):
        if token in ("<PRICE>", "<PRIZE>"):
            open_at = i
        elif token in ("</PRICE>", "</PRIZE>"):
            if open_at is not None and source[open_at][1:] != token[2:]:
                pairs[open_at] = pairs[i] = open_at
            open_at = None
    return pairs


def edits(source, target):
    """Multiset of token edits turning `source` into `target`."""
    pairs = _mismatched_pairs(source)
    found = Counter()
    matcher = difflib.SequenceMatcher(None, source, target, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        if op == "replace" and i2 - i1 == j2 - j1:
            for i, new in zip(range(i1, i2), target[j1:j2]):
                old = source[i]
                if i in pairs and new in PRICE_TAGS and old[:2] == new[:2]:
                    found[("price pair", pairs[i])] += 1
                else:
                    found[("sub", i, new)] += 1
            continue
        for i in range(i1, i2):
            found[("del", i)] += 1
        for new in target[j1:j2]:
            found[("ins", i1, new)] += 1
    return found


def f1(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


class BookAdvertXml(Benchmark):
    """Benchmark for Book Advert XML files (malformed) from Avisblatt."""

    score_unparseable_as_miss = True

    @staticmethod
    def load_input(image_name):
        with open(os.path.join(TEXTS, f"{image_name}.json"), encoding="utf-8") as handle:
            return json.load(handle)["xml_string"]

    def score_request_answer(self, image_name, response, ground_truth):
        """Score a single request against ground truth."""
        data = self.prepare_scoring_data(response)
        answer = data.get("fixed_xml") if isinstance(data, dict) else None
        source = tokens(self.load_input(image_name))
        wanted = edits(source, tokens(ground_truth["fixed_xml"]))
        made = edits(source, tokens(answer)) if isinstance(answer, str) else Counter()
        tp = sum((wanted & made).values())
        fp = sum(made.values()) - tp
        fn = sum(wanted.values()) - tp
        score = 1.0 if not wanted and not made else f1(tp, fp, fn)
        return {
            "f1_score": score,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "field_scores": {
                "fixed_xml": {
                    "response": answer,
                    "ground_truth": ground_truth["fixed_xml"],
                    "score": score,
                }
            },
        }

    def score_benchmark(self, all_scores):
        """Macro F1 over adverts and micro F1 over pooled edits."""
        scores = [s for s in all_scores if isinstance(s, dict) and "f1_score" in s]
        if not scores:
            return {"f1_macro": 0.0, "f1_micro": 0.0}
        tp = sum(s["true_positives"] for s in scores)
        fp = sum(s["false_positives"] for s in scores)
        fn = sum(s["false_negatives"] for s in scores)
        return {
            "f1_macro": sum(s["f1_score"] for s in scores) / len(scores),
            "f1_micro": f1(tp, fp, fn),
            "micro_precision": tp / (tp + fp) if tp + fp else 0.0,
            "micro_recall": tp / (tp + fn) if tp + fn else 0.0,
            "total_instances": len(scores),
            "total_tp": tp,
            "total_fp": fp,
            "total_fn": fn,
        }
