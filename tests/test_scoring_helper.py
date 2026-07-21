"""Unit tests for scripts/scoring_helper.py (pure scoring logic)."""
import pytest
from pydantic import BaseModel

from scoring_helper import (
    calculate_fuzzy_score,
    get_all_keys,
    get_nested_value,
    remove_none,
)


class TestCalculateFuzzyScore:
    def test_equal_values(self):
        assert calculate_fuzzy_score("abc", "abc") == 1.0

    def test_either_none(self):
        assert calculate_fuzzy_score(None, "abc") == 0.0
        assert calculate_fuzzy_score("abc", None) == 0.0
        assert calculate_fuzzy_score(None, None) == 1.0  # both equal (==) short-circuits

    def test_int_str_coercion(self):
        assert calculate_fuzzy_score(2024, "2024") == 1.0
        assert calculate_fuzzy_score("2024", 2024) == 1.0

    def test_non_scalar_returns_zero(self):
        assert calculate_fuzzy_score({"a": 1}, "a") == 0.0
        assert calculate_fuzzy_score(["a"], ["a"]) == 1.0  # equal short-circuits before type check
        assert calculate_fuzzy_score(["a"], ["b"]) == 0.0

    def test_partial_match_is_fractional(self):
        score = calculate_fuzzy_score("hello", "hallo")
        assert 0.0 < score < 1.0
        assert score == pytest.approx(0.8)

    def test_closer_string_scores_higher(self):
        assert calculate_fuzzy_score("kitten", "kitten ") > calculate_fuzzy_score("kitten", "xxxxxx")


class _Model(BaseModel):
    a: int
    b: str


class TestGetAllKeys:
    def test_flat_dict(self):
        assert sorted(get_all_keys({"a": 1, "b": 2})) == ["a", "b"]

    def test_nested_dict(self):
        assert sorted(get_all_keys({"a": {"b": 1, "c": 2}})) == ["a.b", "a.c"]

    def test_list_indices(self):
        assert get_all_keys({"a": [10, 20]}) == ["a[0]", "a[1]"]

    def test_pydantic_model(self):
        assert sorted(get_all_keys(_Model(a=1, b="x"))) == ["a", "b"]

    def test_empty_containers(self):
        assert get_all_keys({}) == []
        assert get_all_keys([]) == []


class TestGetNestedValue:
    def test_dot_path(self):
        assert get_nested_value({"a": {"b": 5}}, "a.b") == 5

    def test_bracket_path(self):
        assert get_nested_value({"a": [{"b": 7}]}, "a[0].b") == 7

    def test_missing_key(self):
        assert get_nested_value({"a": 1}, "b") is None

    def test_index_out_of_range(self):
        assert get_nested_value({"a": [1]}, "a[5]") is None

    def test_descend_past_scalar(self):
        assert get_nested_value({"a": 1}, "a.b") is None

    def test_pydantic_model(self):
        assert get_nested_value(_Model(a=3, b="y"), "a") == 3


class TestRemoveNone:
    def test_drops_top_level_none(self):
        assert remove_none({"a": 1, "b": None}) == {"a": 1}

    def test_nested(self):
        assert remove_none({"a": {"b": None, "c": 2}}) == {"a": {"c": 2}}

    def test_list_preserved(self):
        assert remove_none({"a": [1, 2]}) == {"a": [1, 2]}

    def test_scalar_passthrough(self):
        assert remove_none(5) == 5
        assert remove_none("x") == "x"
