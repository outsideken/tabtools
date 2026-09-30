"""Tests for tabtools.profile."""

from __future__ import annotations

import pandas as pd
import pytest

from tabtools.profile import category_candidates, quick_profile


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "count": [1, 2, 3, 100, 4],
            "label": ["a", "b", "a", "c", "b"],
            "notes": [None, None, "x", None, None],
        }
    )


class TestQuickProfile:
    def test_returns_one_row_per_column(self, sample_df):
        profile = quick_profile(sample_df)
        assert len(profile) == 3
        assert set(profile["column"]) == {"count", "label", "notes"}

    def test_numeric_stats(self, sample_df):
        profile = quick_profile(sample_df)
        count_row = profile.loc[profile["column"] == "count"].iloc[0]
        assert count_row["mean"] == pytest.approx(22.0)
        assert count_row["n_unique"] == 5

    def test_empty_dataframe(self):
        profile = quick_profile(pd.DataFrame())
        assert profile.empty

    def test_flags_category_candidates(self, sample_df):
        profile = quick_profile(sample_df, category_max_unique=3)
        label_row = profile.loc[profile["column"] == "label"].iloc[0]
        assert bool(label_row["category_candidate"])
        assert not bool(profile.loc[profile["column"] == "count", "category_candidate"].iloc[0])

    def test_category_hints_disabled(self, sample_df):
        profile = quick_profile(sample_df, category_max_unique=None)
        assert profile["category_candidate"].eq(False).all()


class TestCategoryCandidates:
    def test_finds_low_cardinality_columns(self, sample_df):
        result = category_candidates(sample_df, max_unique=3)
        label_row = result.loc[result["column"] == "label"].iloc[0]
        assert bool(label_row["candidate"])
        assert label_row["n_unique"] == 3

    def test_no_object_columns(self):
        df = pd.DataFrame({"count": [1, 2, 3]})
        result = category_candidates(df)
        assert result.empty

    def test_invalid_max_unique_raises(self):
        with pytest.raises(ValueError, match="max_unique"):
            category_candidates(pd.DataFrame({"a": ["x"]}), max_unique=0)