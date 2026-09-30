# tabtools

Workspace-wide rules (single checkout, GitHub installs, shared venv, how Claude and
Cursor work together) are in `../AGENTS.md`. This file covers tabtools only.

## What it is

Tabular profiling and anomaly scoring for pandas DataFrames: `quick_profile`,
`category_candidates`, `anomaly_score` (z-score, MAD, IQR), `flag_outliers`,
`anomaly_summary`. Published to GitHub (public) on 2026-09-30; before that it was a
local-only folder.

Today it is **notebook-only** code, so the JEMA sandbox rules don't apply and
`from __future__ import annotations` is fine. Watch for this changing:
`jema-tools/jematools/jema_utils.py` says several of its helpers are slated to move
here. If jematools ever imports tabtools, tabtools becomes JEMA code and must follow
the rules in `jema-tools/AGENTS.md` (Python 3.9, no `__future__`/`os`/`sys`/`pathlib`,
no `X | Y` unions); add its runtime-rules test at that point.

## Layout

- `tabtools/` — the package: `profile.py`, `anomaly.py`, `_messages.py` (re-exports
  `wherewhen._messages`), `_version.py`.
- `tests/` — pytest suite. CI (`.github/workflows/ci.yml`) runs it on Python 3.12 and
  3.9.
- `CHANGELOG.md` — record every user-visible change under `[Unreleased]`.

## Rules

- Keep `requires-python >=3.9` true; the 3.9 CI job checks it.
- Depends on `wherewhen` (installed from GitHub). Pair with
  `viztools.palettes.ANOMALY_PALETTE` for colours, but don't add viztools as a
  dependency.
- Releases: bump `tabtools/_version.py` and `pyproject.toml` together, update
  `tests/test_package.py`'s version check, `CHANGELOG.md`, and the README badges.

## Testing

`../.venv/bin/python -m pytest -q` from the repo root (about a second).

## Open work

Track to-dos as GitHub issues on outsideken/tabtools, claimed with the
`agent:claude` / `agent:cursor` labels.
