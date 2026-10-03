# Changelog

All notable changes to tabtools will be documented here.

This package versions **independently** of jematools, wherewhen, h3tools, and
viztools.

---

## [Unreleased]

### Changed
- The version is typed in one place, ``tabtools/_version.py``.
  ``pyproject.toml`` reads it (``dynamic = ["version"]``), the README's
  hand-typed version and test-count badges are replaced by the CI badge, and
  the version test checks the single source instead of a literal (#2).
- Published to GitHub (outsideken/tabtools); README installs from GitHub instead of
  local editable paths
- Author metadata set to OutsideKen; added ``LICENSE`` (MIT, as already declared)

---

## [0.1.1] — 2026-06-17

### Changed
- README — test-count badge added (19 passing)
- ``tests/test_package.py`` — version string expectations updated to **0.1.1**

---

## [0.1.0] — 2026-06-08

### Added
- `tabtools.profile.quick_profile` — one-row-per-column table profile with emoji notices
- `tabtools.profile.category_candidates` — read-only scan for category-worthy columns
- `tabtools.anomaly.anomaly_score` — signed z-score, MAD, and IQR scores
- `tabtools.anomaly.flag_outliers` — boolean outlier mask from raw values or scores
- `tabtools.anomaly.anomaly_summary` — per-column flagged counts and score ranges
- `tabtools.list_functions` — module catalogue helper
- Import-time load notice via `wherewhen._messages.loaded()`
- Tests covering profile, anomaly, and package metadata

### Dependencies
- `pandas`, `numpy`, `wherewhen>=0.2.0`