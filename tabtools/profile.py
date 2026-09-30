"""
tabtools.profile
================
Quick table profiling and category-candidate discovery.

Read-only helpers — they inspect DataFrames without mutating them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from tabtools._messages import info, skip, warn

__all__ = [
    "quick_profile",
    "category_candidates",
]


def _is_object_or_string(series: pd.Series) -> bool:
    dtype = series.dtype
    return (
        pd.api.types.is_object_dtype(dtype)
        or pd.api.types.is_string_dtype(dtype)
    )


def _category_candidate(n_unique: int, max_unique: int) -> bool:
    return n_unique <= max_unique


def quick_profile(
    df: pd.DataFrame,
    category_max_unique: int | None = 50,
) -> pd.DataFrame:
    """
    Build a one-row-per-column profile and print emoji notices.

    Parameters
    ----------
    df : pandas.DataFrame
        Table to profile.
    category_max_unique : int or None, optional
        When set, object/string columns with at most this many unique values
        are flagged as ``smart_categories`` candidates in the output.
        Default ``50``.  Pass ``None`` to omit category hints.

    Returns
    -------
    pandas.DataFrame
        Profile with ``column``, ``dtype``, ``null_pct``, ``n_unique``,
        ``mean``, ``std``, and ``category_candidate``.  Non-numeric columns
        have NaN for ``mean`` and ``std``.
    """
    profile_columns = [
        "column", "dtype", "null_pct", "n_unique", "mean", "std", "category_candidate",
    ]

    if category_max_unique is not None and category_max_unique < 1:
        raise ValueError(
            warn(
                "quick_profile",
                f"category_max_unique must be a positive integer or None, "
                f"got {category_max_unique!r}.",
            )
        )

    if df.empty:
        print(info("quick_profile", "Empty DataFrame — nothing to profile."))
        return pd.DataFrame(columns=profile_columns)

    n_rows = len(df)
    rows: list[dict] = []

    for col in df.columns:
        series = df[col]
        null_pct = round(100.0 * series.isna().sum() / n_rows, 2)
        n_unique = int(series.nunique(dropna=True))
        dtype = str(series.dtype)

        mean = std = np.nan
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().any():
            mean = round(float(numeric.mean()), 4)
            std = round(float(numeric.std(ddof=0)), 4)

        is_candidate = False
        if category_max_unique is not None and _is_object_or_string(series):
            is_candidate = _category_candidate(n_unique, category_max_unique)

        rows.append(
            {
                "column": col,
                "dtype": dtype,
                "null_pct": null_pct,
                "n_unique": n_unique,
                "mean": mean,
                "std": std,
                "category_candidate": is_candidate,
            }
        )

    print(info("quick_profile", f"{len(df.columns)} columns, {n_rows:,} rows"))
    print()

    candidate_cols: list[str] = []

    for row in rows:
        col = row["column"]
        null_pct = row["null_pct"]
        n_unique = row["n_unique"]
        dtype = row["dtype"]
        mean = row["mean"]
        is_candidate = row["category_candidate"]
        suffix = " — category candidate" if is_candidate else ""

        if is_candidate:
            candidate_cols.append(col)

        if null_pct >= 50.0:
            print(
                warn(
                    "quick_profile",
                    f"'{col}': {null_pct:.1f}% null — high missingness{suffix}",
                )
            )
        elif np.isfinite(mean):
            print(
                info(
                    "quick_profile",
                    f"'{col}': {dtype}, {n_unique} unique, mean={mean}{suffix}",
                )
            )
        else:
            print(
                info(
                    "quick_profile",
                    f"'{col}': {dtype}, {n_unique} unique{suffix}",
                )
            )

    if category_max_unique is not None and candidate_cols:
        print()
        joined = ", ".join(candidate_cols)
        print(
            info(
                "quick_profile",
                f"category candidates (≤{category_max_unique} unique): {joined}",
            )
        )

    print()
    return pd.DataFrame(rows)


def category_candidates(
    df: pd.DataFrame,
    max_unique: int = 50,
) -> pd.DataFrame:
    """
    Scan object and string columns for category conversion candidates.

    Read-only — does not mutate the DataFrame or convert dtypes.  A column
    is a candidate when its unique count is at most *max_unique*.

    Parameters
    ----------
    df : pandas.DataFrame
        Table to scan.
    max_unique : int, optional
        Maximum unique values for a column to be considered category-worthy.
        Default ``50``.

    Returns
    -------
    pandas.DataFrame
        One row per object/string column with ``n_unique``, ``unique_pct``,
        and ``candidate``.
    """
    if max_unique < 1:
        raise ValueError(
            warn(
                "category_candidates",
                f"max_unique must be a positive integer, got {max_unique!r}.",
            )
        )

    n_rows = len(df)
    if n_rows == 0:
        print(info("category_candidates", "Empty DataFrame — nothing to scan."))
        return pd.DataFrame(columns=["column", "n_unique", "unique_pct", "candidate"])

    obj_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if not obj_cols:
        print(skip("category_candidates", "No object or string columns found."))
        return pd.DataFrame(columns=["column", "n_unique", "unique_pct", "candidate"])

    rows: list[dict] = []
    n_candidates = 0

    for col in obj_cols:
        n_unique = int(df[col].nunique(dropna=True))
        unique_pct = round(100.0 * n_unique / n_rows, 2) if n_rows else 0.0
        candidate = _category_candidate(n_unique, max_unique)
        rows.append(
            {
                "column": col,
                "n_unique": n_unique,
                "unique_pct": unique_pct,
                "candidate": candidate,
            }
        )
        if candidate:
            n_candidates += 1
            print(
                info(
                    "category_candidates",
                    f"'{col}': {n_unique} unique ({unique_pct:.1f}%) — candidate",
                )
            )
        else:
            print(
                skip(
                    "category_candidates",
                    f"'{col}': {n_unique} unique ({unique_pct:.1f}%) — above max_unique={max_unique}",
                )
            )

    print(
        info(
            "category_candidates",
            f"{n_candidates} of {len(obj_cols)} object/string columns are candidates",
        )
    )
    print()
    return pd.DataFrame(rows)