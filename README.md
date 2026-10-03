# tabtools

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/outsideken/tabtools/actions/workflows/ci.yml/badge.svg)

Tabular profiling and anomaly scoring for the JEMA toolkit.  Versions
independently of jematools, wherewhen, h3tools, and viztools.  See
[CHANGELOG.md](CHANGELOG.md).  The version is `tabtools.__version__`, set only
in `tabtools/_version.py`.

Import directly — not re-exported through jematools or h3tools.

---

## Installation

Install **wherewhen** first (declared dependency, not on PyPI), then tabtools:

```bash
pip install git+https://github.com/outsideken/wherewhen.git
pip install git+https://github.com/outsideken/tabtools.git
```

---

## Quick start

```python
import pandas as pd
import matplotlib.pyplot as plt

from tabtools.profile import quick_profile
from tabtools.anomaly import anomaly_score, flag_outliers, anomaly_summary
from viztools.palettes import ANOMALY_PALETTE
from viztools.viz import format_plot

df = pd.read_parquet("events.parquet")
quick_profile(df)

scores = anomaly_score(df["event_count"], method="mad")
flags = flag_outliers(scores, threshold=2.5)
anomaly_summary(df, columns=["event_count"])

colors = [ANOMALY_PALETTE[0] if s < 0 else ANOMALY_PALETTE[-1] for s in scores[flags]]
fig, ax = plt.subplots()
ax.bar(range(flags.sum()), scores[flags], color=colors)
format_plot(ax)
plt.show()
```

```python
import tabtools
tabtools.list_functions()
```

---

## Modules

### `profile` — table inspection

```python
from tabtools.profile import quick_profile, category_candidates

profile = quick_profile(df)                    # returns DataFrame + prints notices
candidates = category_candidates(df, max_unique=50)
```

### `anomaly` — signed scores and flags

```python
from tabtools.anomaly import anomaly_score, flag_outliers, anomaly_summary

scores = anomaly_score(df["count"], method="zscore")   # or 'mad', 'iqr'
flags  = flag_outliers(scores, threshold=2.0)
flags  = flag_outliers(df["count"], threshold=2.0, method="mad")
summary = anomaly_summary(df, columns=["count"])
```

Pair with `viztools.palettes.ANOMALY_PALETTE` for diverging anomaly colours.

---

## Tests

```bash
pip install -e . pytest
pytest tests/ -q
```

---

## Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| `pandas` | Yes | DataFrames and Series |
| `numpy` | Yes | Numeric scoring |
| `wherewhen` | Yes | Notification helpers |