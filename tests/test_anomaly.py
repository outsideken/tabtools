"""Tests for tabtools.anomaly."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tabtools.anomaly import anomaly_score, anomaly_summary, flag_outliers


@pytest.fixture
def count_series():
    return pd.Series([1, 2, 3, 4, 10_000], name="event_count")


class TestAnomalyScore:
    def test_zscore_extreme_value_has_largest_abs_score(self, count_series):
        scores = anomaly_score(count_series, method="zscore")
        assert scores.abs().idxmax() == count_series.index[-1]
        assert scores.abs().iloc[-1] > scores.abs().iloc[:-1].max()

    def test_mad_returns_series(self, count_series):
        scores = anomaly_score(count_series, method="mad")
        assert isinstance(scores, pd.Series)
        assert len(scores) == len(count_series)

    def test_iqr_handles_uniform_values(self):
        scores = anomaly_score([5, 5, 5, 5], method="iqr")
        assert np.allclose(scores.fillna(0), 0.0)

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="method must be"):
            anomaly_score([1, 2, 3], method="sigma")


class TestFlagOutliers:
    def test_on_precomputed_scores(self, count_series):
        scores = anomaly_score(count_series, method="mad")
        flags = flag_outliers(scores, threshold=2.0)
        assert bool(flags.iloc[-1])
        assert flags.sum() >= 1

    def test_with_method_on_raw_values(self, count_series):
        flags = flag_outliers(count_series, threshold=2.0, method="mad")
        assert flags.dtype == bool
        assert flags.sum() >= 1

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError, match="threshold"):
            flag_outliers([1, 2, 3], threshold=-1.0)


class TestAnomalySummary:
    def test_summary_shape(self, count_series):
        df = pd.DataFrame({"event_count": count_series, "label": ["a"] * 5})
        summary = anomaly_summary(
            df, columns=["event_count"], threshold=2.0, method="mad"
        )
        assert len(summary) == 1
        assert summary.iloc[0]["column"] == "event_count"
        assert summary.iloc[0]["n_flagged"] >= 1

    def test_missing_column_raises(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        with pytest.raises(KeyError, match="Columns not found"):
            anomaly_summary(df, columns=["missing"])