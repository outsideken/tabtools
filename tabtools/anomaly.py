"""
tabtools.anomaly
================
Signed anomaly scores and outlier flags for numeric columns.

Pair scores with ``viztools.palettes.ANOMALY_PALETTE`` in notebooks for
diverging choropleths and bar charts.  tabtools returns Series and
DataFrames — no plotting here.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from tabtools._messages import info, warn

__all__ = [
    "anomaly_score",
    "flag_outliers",
    "anomaly_summary",
]

_METHODS = frozenset({"zscore", "mad", "iqr"})


def _as_series(data: pd.Series | Iterable) -> pd.Series:
    if isinstance(data, pd.Series):
        return data
    return pd.Series(data)


def _validate_method(method: str) -> None:
    if method not in _METHODS:
        raise ValueError(
            warn(
                "anomaly_score",
                f"method must be one of {sorted(_METHODS)}, got {method!r}.",
            )
        )


def _numeric_array(series: pd.Series) -> tuple[np.ndarray, pd.Index]:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.to_numpy(dtype=float), series.index


def _scores_from_values(values: np.ndarray, method: str) -> np.ndarray:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.full(values.shape, np.nan, dtype=float)

    scores = np.full(values.shape, np.nan, dtype=float)
    mask = np.isfinite(values)

    if method == "zscore":
        center = float(np.mean(finite))
        spread = float(np.std(finite, ddof=0))
        if spread == 0.0:
            spread = float(np.mean(np.abs(finite - center)))
        if spread == 0.0:
            scores[mask] = 0.0
        else:
            scores[mask] = (values[mask] - center) / spread
        return scores

    if method == "mad":
        center = float(np.median(finite))
        spread = float(np.median(np.abs(finite - center)))
        if spread == 0.0:
            spread = float(np.mean(np.abs(finite - center)))
        if spread == 0.0:
            scores[mask] = 0.0
        else:
            scores[mask] = 0.6745 * (values[mask] - center) / spread
        return scores

    # method == "iqr"
    q1, q3 = np.percentile(finite, [25, 75])
    center = float(np.median(finite))
    spread = float(q3 - q1)
    if spread == 0.0:
        spread = float(np.median(np.abs(finite - center)))
    if spread == 0.0:
        scores[mask] = 0.0
    else:
        scores[mask] = (values[mask] - center) / spread
    return scores


def anomaly_score(
    series: pd.Series | Iterable,
    method: str = "zscore",
) -> pd.Series:
    """
    Return signed normalized anomaly scores for a numeric column.

    Parameters
    ----------
    series : pandas.Series or iterable
        Numeric values to score.  Non-numeric entries become NaN in the
        output.
    method : {'zscore', 'mad', 'iqr'}, optional
        Scoring method.  ``'zscore'`` uses mean and standard deviation;
        ``'mad'`` uses median and median absolute deviation; ``'iqr'``
        uses median and the inter-quartile range.

    Returns
    -------
    pandas.Series
        Signed scores aligned to the input index.  Positive values are
        above the centre; negative values are below.
    """
    _validate_method(method)
    s = _as_series(series)
    values, index = _numeric_array(s)
    scores = _scores_from_values(values, method)
    return pd.Series(scores, index=index, name=s.name)


def flag_outliers(
    series: pd.Series | Iterable,
    threshold: float = 2.0,
    method: str | None = None,
) -> pd.Series:
    """
    Return a boolean mask marking outlier rows.

    When *method* is provided, anomaly scores are computed from raw values
    first.  When *method* is ``None``, *series* is treated as pre-computed
    scores (for example the output of :func:`anomaly_score`).

    Parameters
    ----------
    series : pandas.Series or iterable
        Raw values or pre-computed anomaly scores.
    threshold : float, optional
        Minimum absolute score to flag as an outlier.  Default ``2.0``.
    method : str or None, optional
        Scoring method passed to :func:`anomaly_score`.  Omit when *series*
        already contains scores.

    Returns
    -------
    pandas.Series
        Boolean mask aligned to the input index.
    """
    if threshold < 0:
        raise ValueError(
            warn("flag_outliers", f"threshold must be non-negative, got {threshold}.")
        )

    s = _as_series(series)
    if method is not None:
        _validate_method(method)
        scores = anomaly_score(s, method=method)
    else:
        scores = pd.to_numeric(s, errors="coerce")

    return scores.abs() >= threshold


def anomaly_summary(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    threshold: float = 2.0,
    method: str = "zscore",
) -> pd.DataFrame:
    """
    Summarise anomaly flags across numeric columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input table.
    columns : list of str, optional
        Columns to summarise.  Defaults to all numeric columns.
    threshold : float, optional
        Outlier threshold passed to :func:`flag_outliers`.
    method : str, optional
        Scoring method passed to :func:`anomaly_score`.

    Returns
    -------
    pandas.DataFrame
        One row per column with ``n_flagged``, ``pct_flagged``,
        ``min_score``, and ``max_score``.
    """
    if columns is None:
        cols = df.select_dtypes(include=[np.number]).columns.tolist()
    else:
        missing = sorted(set(columns) - set(df.columns))
        if missing:
            raise KeyError(
                warn("anomaly_summary", f"Columns not found in DataFrame: {missing}")
            )
        cols = list(columns)

    if not cols:
        print(info("anomaly_summary", "No numeric columns to summarise."))
        return pd.DataFrame(
            columns=["column", "n_flagged", "pct_flagged", "min_score", "max_score"]
        )

    rows: list[dict] = []
    for col in cols:
        scores = anomaly_score(df[col], method=method)
        flags = flag_outliers(scores, threshold=threshold)
        n_flagged = int(flags.sum())
        n_rows = len(df)
        pct = 100.0 * n_flagged / n_rows if n_rows else 0.0
        finite = scores[np.isfinite(scores)]
        rows.append(
            {
                "column": col,
                "n_flagged": n_flagged,
                "pct_flagged": round(pct, 2),
                "min_score": float(finite.min()) if finite.size else np.nan,
                "max_score": float(finite.max()) if finite.size else np.nan,
            }
        )
        print(
            info(
                "anomaly_summary",
                f"'{col}': {n_flagged} flagged ({pct:.1f}%) via {method}",
            )
        )

    if rows:
        print()

    return pd.DataFrame(rows)